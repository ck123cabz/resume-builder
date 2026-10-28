"""The html and svg reader. Split out of readers.py on 9/18 to keep both files
under the line limit; readers.py owns the office formats and the suffix table.

Text is buffered and flushed at a block boundary or a kind change, never per
parser callback. `<p>Run a <em>sanity</em> check</p>` arrives in three callbacks
and has to leave as one row, or a tier-1 phrase straddling the inline tag is
never seen.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from .config import IGNORE_MARKER

# A link is inline text and joins its paragraph. One dressed as a button, with
# role="button" or a class holding btn or button, is pushed as BUTTON_A instead.
BUTTON_A = "a.button"
HTML_KINDS = {
    **{f"h{i}": "heading" for i in range(1, 7)}, "title": "heading", "summary": "heading",
    "button": "button", BUTTON_A: "button",
    "label": "label", "th": "label", "option": "label",
}
# Code, and other people's words: a blockquote or a q is a quotation, and CLAUDE.md
# never filters somebody else's words. walk() drops a plain markdown blockquote
# for the same reason.
HTML_SKIP = {"script", "style", "code", "pre", "blockquote", "q"}
SVG_KINDS = {"text": "heading", "title": "heading"}

# Opening or closing one of these ends the run of text being buffered. A block
# element missing from this set merges with the one beside it: three <text>
# elements in an svg came back as a single heading row on the first one's line.
BLOCK = {
    *{f"h{i}" for i in range(1, 7)},
    "p", "div", "section", "article", "li", "ul", "ol", "table", "tr", "td", "th",
    "header", "footer", "main", "nav", "form", "button", "label", "option", "title",
    "summary", "br", "blockquote", "dl", "dt", "dd", "aside", "figcaption", "caption",
    "text", "tspan", "legend", "address", "figure",
}
# These carry no end tag, so pushing them would leave them on the stack forever.
VOID = {"input", "br", "hr", "img", "meta", "link", "area", "base", "col", "embed",
        "source", "track", "wbr"}
# These may be written without a close tag.
AUTO_CLOSE = {"option", "th", "td", "li", "tr", "dt", "dd"}
INLINE = {"em", "strong", "b", "i", "a", "span", "code", "small", "u", "mark"}
# A template slot is one value, whatever its name: "Replies: {{ count }}" is a
# label and a cell, and "{{ user.first_name }}" is not three words.
SLOT = re.compile(r"\{\{.*?\}\}|\$\{[^}]*\}")
VALUE = "{0}"
PUNCT_GAP = re.compile(r" ([.,;:!?)])")


def _tag(tag: str, attrs) -> str:
    if tag != "a":
        return tag
    a = dict(attrs)
    cls = a.get("class") or ""
    return BUTTON_A if a.get("role") == "button" or "btn" in cls or "button" in cls else "a"


class _Collector(HTMLParser):
    def __init__(self, kinds: dict[str, str], drop_untagged: bool = False):
        super().__init__()
        self.kinds, self.drop_untagged = kinds, drop_untagged
        self.stack: list[str] = []
        self.out: list[tuple[int, str, str, str]] = []
        self.line, self.kind, self.parts = 0, "", []

    def flush(self) -> None:
        # Runs join on a space, except before closing punctuation: "Read <a>the
        # guide</a>." is "Read the guide.", and <span>Replies</span><span>412</span>,
        # with no space in the source, is still two words.
        text = PUNCT_GAP.sub(r"\1", " ".join(self.parts))
        if text:
            self.out.append((self.line, self.kind, text, text))
        self.parts = []

    def _auto_close(self, tag: str) -> None:
        """<option> holds text only, so anything that is not inline ends it. The
        rest close a sibling of the same name. <p> also closes an open <p> that
        sits above the nearest block."""
        if self.stack and self.stack[-1] == "option" and tag not in INLINE:
            self.stack.pop()
        if tag == "p":
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i] == "p":
                    del self.stack[i:]
                    return
                if self.stack[i] in BLOCK:
                    return
        elif tag in AUTO_CLOSE and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_starttag(self, tag, attrs):
        tag = _tag(tag, attrs)
        if tag in BLOCK or tag == BUTTON_A:
            self.flush()
        if tag in VOID:
            return
        self._auto_close(tag)
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "a":
            tag = next((t for t in reversed(self.stack) if t in ("a", BUTTON_A)), tag)
        if tag in BLOCK or tag == BUTTON_A:
            self.flush()
        if tag in self.stack:
            del self.stack[len(self.stack) - 1 - self.stack[::-1].index(tag):]

    def handle_data(self, data):
        text = " ".join(SLOT.sub(VALUE, data).split())
        if not text or set(self.stack) & HTML_SKIP:
            return
        kind = next((self.kinds[t] for t in reversed(self.stack) if t in self.kinds), None)
        if kind is None and self.drop_untagged:
            return
        kind = kind or "prose"
        if self.parts and kind == self.kind:
            self.parts.append(text)
            return
        self.flush()
        self.line, self.kind, self.parts = self.getpos()[0], kind, [text]


def read_markup(path: Path, kinds: dict[str, str],
                drop_untagged: bool = False) -> list[tuple[int, str, str, str]]:
    """The ignore marker in the first 4096 characters skips the file, as it does
    in read_markdown and lint_text."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if IGNORE_MARKER in text[:4096]:
        return []
    c = _Collector(kinds, drop_untagged)
    c.feed(text)
    c.close()
    c.flush()
    return c.out
