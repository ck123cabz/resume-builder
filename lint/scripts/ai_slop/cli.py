"""Command line: paths or stdin in, text or json out, exit code by worst report."""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

from .config import DEFAULT_PHRASES, IGNORE_MARKER, SKIP_PARTS, PhraseFileError, load_phrases
from .core import lint_tagged, lint_text
from .jobs import JOBS, declared_job, resolve_job
from .readers import READERS, SUFFIXES, UI_KINDS, WHOLE_ROWS, read_tagged, ui_rows
from .report import Hit, Report, fmt_text, to_json


# Word and LibreOffice keep a lock file beside an open document, ~$Paper.docx or
# .~lock.Paper.docx#. It carries the suffix and none of the text.
LOCK_PREFIXES = ("~$", ".~lock")


def wanted(p: Path) -> bool:
    s = p.as_posix()
    return (p.suffix.lower() in SUFFIXES and not p.name.startswith(LOCK_PREFIXES)
            and not any(k in s for k in SKIP_PARTS))


def skipped(p: Path) -> bool:
    """Machine state and other people's words, wherever the path came from.

    Applies to an explicitly named file too, not just a directory walk. The
    PostToolUse hook passes whatever file was just written, so without this the
    whole of memory/ was being linted every time a run touched it — that is how
    the harness memory index came to be graded on its em dashes.
    """
    s = p.resolve().as_posix()
    return any(k in s for k in SKIP_PARTS)


def collect(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            out.extend(sorted(f for f in p.rglob("*") if f.is_file() and wanted(f)))
        elif p.is_file() and not skipped(p):
            out.append(p)
    return out


def head(p: Path) -> str:
    """Where a file declares its job, for resolve_job: a markdown file's first
    2 KB, past the longest front matter in the vault, or an html page's head,
    which an inline stylesheet can push well past 2 KB."""
    suffix = p.suffix.lower()
    if suffix not in (".md", ".html"):
        return ""
    with p.open(encoding="utf-8", errors="replace") as fh:
        return fh.read(2048) if suffix == ".md" else fh.read(65536).split("</head>", 1)[0]


def lint_text_path(p: Path, cfg: dict, job: str = "tell") -> Report:
    """Markdown keeps the text path, so the ignore marker and walk() are untouched.
    So does any suffix with no reader: a .txt named on the command line has always
    been linted as markdown, and routing it into READERS would raise a KeyError
    that the caller catches, leaving a file full of tier-1 phrases reported clean."""
    suffix = p.suffix.lower()
    if suffix == ".md" or suffix not in READERS:
        return lint_text(p.read_text(encoding="utf-8"), cfg, str(p), job)
    return lint_tagged(read_tagged(p), cfg, str(p), job, whole_rows=suffix in WHOLE_ROWS)


def name_bad_job(rep: Report, p: Path | None, text_head: str, flag: str | None) -> Report:
    """A declared job nobody has was read as the default. Say so in one hit, so a
    hook sees exit 1 or 2 rather than a silent 3. An ignore-marked file stays quiet."""
    bad = None if flag else declared_job(p, text_head)
    if bad and bad not in JOBS and IGNORE_MARKER not in text_head:
        rep.hits.insert(0, Hit(1, "STRUCT", "bad-job", f"job: {bad} is not one of {', '.join(JOBS)}"))
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Detect AI writing tells in written prose.")
    ap.add_argument("paths", nargs="*", help="files or directories; stdin if omitted")
    ap.add_argument("--phrases", default=str(DEFAULT_PHRASES))
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--quiet", action="store_true", help="summary lines only")
    picks = ap.add_mutually_exclusive_group()
    picks.add_argument("--job", choices=JOBS, default=None,
                       help="copy job; default from front matter, then file type (md=tell)")
    picks.add_argument("--ui", action="store_true",
                       help="stdin is flat interface text under the show job: each line is "
                            "'kind<TAB>text' naming one of %s, or a label" % ", ".join(UI_KINDS))
    args = ap.parse_args(argv)

    try:
        cfg = load_phrases(Path(args.phrases))
    except (OSError, json.JSONDecodeError, PhraseFileError) as exc:
        print(f"ai_slop_lint: cannot read {args.phrases}: {exc}", file=sys.stderr)
        return 3

    reports: list[Report] = []
    # (path, reason) per file that could not be read. Exit 3, unless some other
    # file holds a tier-1 phrase: a banned phrase outranks an unreadable file.
    errors: list[tuple[str, str]] = []
    if args.paths:
        files = collect(args.paths)
        if not files:
            print("ai_slop_lint: no lintable files matched", file=sys.stderr)
            return 0
        for f in files:
            try:
                h = head(f)
                reports.append(name_bad_job(lint_text_path(f, cfg, resolve_job(f, h, args.job)),
                                            f, h, args.job))
            except (OSError, UnicodeDecodeError, zipfile.BadZipFile, KeyError) as exc:
                errors.append((str(f), str(exc)))
                print(f"ai_slop_lint: {f}: {exc}", file=sys.stderr)
    else:
        text = sys.stdin.read()
        if args.ui:
            reports.append(lint_tagged(ui_rows(text), cfg, "<stdin>", "show"))
        else:
            job = resolve_job(None, text[:2048], args.job)
            reports.append(name_bad_job(lint_text(text, cfg, "<stdin>", job),
                                        None, text[:2048], args.job))

    if args.format == "json":
        print(to_json(reports, errors))
    else:
        chunks = [fmt_text(r, args.quiet) for r in reports if r.words or r.hits]
        if chunks:
            print("\n".join(chunks))

    # A controller call on 9/19: 2 if any file holds tier 1, else 3 if any file
    # was unreadable, else the worst of 0 and 1.
    worst = max((r.exit_code() for r in reports), default=0)
    return worst if worst == 2 or not errors else 3
