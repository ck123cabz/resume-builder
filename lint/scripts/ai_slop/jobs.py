"""Copy jobs: which job a document is doing, the shared word lists and the jobs
each one runs in, and the Show rules. Prove, Persuade, Reply and Tell live in jobs_prose.py.
Spec: docs/superpowers/specs/2026-09-18-artifact-copy-gate-design.md

The four regexes below are shape and grammar, not vocabulary, so they stay in
code the way NUMBER_WORD does in sentences.py. Every phrase is in the JSON.
"""
from __future__ import annotations

import re
from pathlib import Path

from .blocks import LIST_ITEM
from .jobs_prose import prose_job_hits
from .lexicon import inflected, phrase_re
from .mentions import mention_spans
from .report import Hit

JOBS = ("show", "prove", "persuade", "reply", "tell")
DEFAULT_JOB = {".html": "show", ".svg": "show", ".docx": "prove", ".pptx": "persuade", ".md": "tell"}
# The front-matter block, and the key inside it. One pattern for each, because a
# single one scanning to the last '---' read the body: a note saying "job: plumber"
# three paragraphs down resolved to plumber.
FRONT_BLOCK = re.compile(r"^---\n((?:.*\n)*?)---")
FRONT_JOB = re.compile(r"^job:\s*([A-Za-z]+)", re.MULTILINE)
# An html page's declaration: <meta name="job" content="tell">, attributes in either order.
META_JOB = re.compile(r"""<meta\b(?=[^>]*\bname=["']job["'])[^>]*\bcontent=["']([A-Za-z]+)["']""",
                      re.IGNORECASE)
LABEL_ROW = re.compile(r"^[^:·]{1,30}[:·]\s*\S")
TITLE_CASE = re.compile(r"^(?:[A-Z][a-z']+ )+[A-Z]")
PROSE_KINDS = ("prose", "subtext")


def declared_job(path: Path | None, text_head: str) -> str | None:
    """The job a file names for itself, lowercased, or None: a markdown file's
    front matter, or an html page's meta tag. text_head is what cli.head() read."""
    block = FRONT_BLOCK.match(text_head or "")
    suffix = path.suffix.lower() if path else ""
    m = (FRONT_JOB.search(block.group(1)) if block
         else META_JOB.search(text_head) if suffix == ".html" else None)
    return m.group(1).lower() if m else None


def resolve_job(path: Path | None, text_head: str, flag: str | None) -> str:
    """The flag, then the declared job, then the suffix's default. A declared job
    nobody has reads as the default, and cli.py names it in a bad-job hit."""
    if flag is not None and flag not in JOBS:
        raise ValueError(f"unknown job {flag!r}; one of {JOBS}")
    declared = declared_job(path, text_head)
    default = DEFAULT_JOB.get(path.suffix.lower() if path else "", "tell")
    return flag or (declared if declared in JOBS else default)


def _named(text: str, start: int) -> bool:
    """A capitalised word inside a sentence is a name: "Empower Semiconductor",
    "Hub". At a sentence start, after a list marker or opening punctuation, the
    capital is grammar and the word still counts."""
    if not text[start].isupper():
        return False
    before = text[:start].rstrip(" \t\"'“‘(*_[")
    return bool(before) and before[-1] not in ".!?" and not LIST_ITEM.fullmatch(before + " ")


def _used(rx: re.Pattern, text: str, quoted: list[tuple[int, int]], prose: bool) -> bool:
    """A match outside every quoted mention (mentions.py says which quotes are)
    that is not, on a prose row, a name."""
    return any(not any(a <= m.start() and m.end() <= b for a, b in quoted)
               and not (prose and _named(text, m.start()))
               for m in rx.finditer(text))


def shared_hits(tagged, cfg: dict, job: str) -> list[Hit]:
    """Each list runs only in the jobs its `jobs` field names (decision 13). A
    heading row is left to pitch-heading, so it draws one label, not two."""
    cues = cfg["mention_cues"]["words"]
    quoted = [mention_spans(m, cues) for _ln, _k, m, _u in tagged]
    out: list[Hit] = []
    for name, spec in cfg["shared"].items():
        if name.startswith("_") or job not in spec["jobs"]:
            continue
        rxs = [(w, inflected(w) if name == "sell" else phrase_re(w)) for w in spec["words"]]
        for (ln, k, m, _u), spans in zip(tagged, quoted):
            if k == "heading":
                continue
            for word, rx in rxs:
                if _used(rx, m, spans, k in PROSE_KINDS):
                    out.append(Hit(ln, "STRUCT", f"shared/{name}:{word}", m.strip()))
    return out


def show_hits(tagged, cfg: dict) -> list[Hit]:
    show = cfg["jobs"]["show"]
    caps, past = show["caps"], re.compile(show["past_tense"], re.IGNORECASE)
    vague = [phrase_re(v) for v in show["vague_buttons"]]
    pronoun = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(p) for p in show["label_pronouns"]),
                         re.IGNORECASE)
    out: list[Hit] = []
    for ln, kind, m, u in tagged:
        text = u.strip()
        # A template row is the rule already obeyed, so the caps and the narration
        # rule step aside. The other three still read it: "Your plan: Pro" is a row
        # and is still a label speaking to the reader.
        is_row = bool(LABEL_ROW.match(text))
        n = len(text.split())
        if "!" in text:
            out.append(Hit(ln, "STRUCT", "show/exclamation", text))
        if not is_row and kind in caps and n > caps[kind]:
            out.append(Hit(ln, "STRUCT", "show/cap", f"{kind} {n} words, cap {caps[kind]}: {text}"))
        if not is_row and re.search(r"\d", text) and past.search(text):
            out.append(Hit(ln, "STRUCT", "show/narrated-value", text))
        if kind in ("button", "heading") and TITLE_CASE.match(text):
            out.append(Hit(ln, "STRUCT", "show/title-case", text))
        if kind == "label" and pronoun.search(text):
            out.append(Hit(ln, "STRUCT", "show/pronoun-in-label", text))
        if kind == "button" and any(v.match(text) for v in vague) and n <= 3:
            out.append(Hit(ln, "STRUCT", "show/vague-button", text))
    return out


def job_hits(tagged, cfg: dict, job: str) -> list[Hit]:
    if job == "show":
        return show_hits(tagged, cfg)
    return prose_job_hits(tagged, cfg, job)
