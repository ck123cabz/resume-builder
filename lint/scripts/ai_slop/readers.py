"""File to tagged lines: (line, kind, masked, unmasked). Markdown keeps its own
walker in prose.py; the rest are stdlib readers for the surfaces the 9/18 spec
added. Nothing here masks, so masked == unmasked on every row.

kinds: heading | button | label | subtext | prose
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

from .config import IGNORE_MARKER
from .prose import walk
from .readers_html import HTML_KINDS, SVG_KINDS, read_markup

Tagged = tuple[int, str, str, str]
SUFFIXES = (".md", ".html", ".svg", ".docx", ".pptx")
# A Word paragraph and a slide are whole: no row from these runs on into the next.
WHOLE_ROWS = (".docx", ".pptx")
UI_KINDS = ("button", "heading", "label", "subtext", "prose")

W_PARA = re.compile(r"</w:p>")
W_TEXT = re.compile(r"<w:t[^>]*>([^<]*)</w:t>")
W_HEAD = re.compile(r'w:pStyle w:val="(?:Heading|Title)')


def read_docx(path: Path) -> list[Tagged]:
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8", "replace")
    out: list[Tagged] = []
    for n, para in enumerate(W_PARA.split(xml), start=1):
        text = "".join(W_TEXT.findall(para)).strip()
        if text:
            out.append((n, "heading" if W_HEAD.search(para) else "prose", text, text))
    return out


A_SHAPE = re.compile(r"</p:sp>")
A_PARA = re.compile(r"</a:p>")
A_TEXT = re.compile(r"<a:t>([^<]*)</a:t>")
SLIDE = re.compile(r"ppt/slides/slide(\d+)\.xml$")


def read_pptx(path: Path) -> list[Tagged]:
    z = zipfile.ZipFile(path)
    names = sorted((int(SLIDE.search(n).group(1)), n) for n in z.namelist() if SLIDE.search(n))
    out: list[Tagged] = []
    for num, name in names:
        xml = z.read(name).decode("utf-8", "replace")
        for shape in A_SHAPE.split(xml):
            title = 'type="title"' in shape or 'type="ctrTitle"' in shape
            for para in A_PARA.split(shape):
                text = "".join(A_TEXT.findall(para)).strip()
                if text:
                    out.append((num, "heading" if title else "subtext", text, text))
    return out


def read_markdown(path: Path) -> list[Tagged]:
    """The ignore marker is honoured here as well as in lint_text, so a caller
    reading rows straight off a path gets the same answer the linter gives."""
    text = path.read_text(encoding="utf-8")
    if IGNORE_MARKER in text[:4096]:
        return []
    return walk(text)


READERS = {
    ".md": read_markdown,
    ".html": lambda p: read_markup(p, HTML_KINDS, drop_untagged=False),
    ".svg": lambda p: read_markup(p, SVG_KINDS, drop_untagged=True),
    ".docx": read_docx,
    ".pptx": read_pptx,
}


def ui_rows(text: str) -> list[Tagged]:
    """Flat interface text, one line per row: the form the gate hook emits. A
    line may name its kind in front of a tab. A word there that is not a kind
    (notification, card) says so once on stderr and the row reads as a label;
    anything else in front of a tab is part of a label's text."""
    rows: list[Tagged] = []
    unknown: set[str] = set()
    for i, line in enumerate(text.splitlines(), 1):
        kind, tab, rest = line.partition("\t")
        if tab and kind not in UI_KINDS and kind.isalpha():
            unknown.add(kind)
            kind = "label"
        elif not (tab and kind in UI_KINDS):
            kind, rest = "label", line
        if rest.strip():
            rows.append((i, kind, rest, rest))
    if unknown:
        print(f"ai_slop_lint: not a kind, read as label: {', '.join(sorted(unknown))}", file=sys.stderr)
    return rows


def read_tagged(path: Path) -> list[Tagged]:
    return READERS[path.suffix.lower()](path)
