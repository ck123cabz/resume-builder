"""PreToolUse gate: pull the human-readable strings out of a tool input so the
surfaces that never touch a file (Pencil, Claude Docs, Claude Design, the Artifact
title) go through the same linter. Usage: python3 -m ai_slop.gate < hook.json
prints one 'kind<TAB>text' line per string, the form `ai_slop_lint.py --ui` reads.
With --markdown it prints each string whole instead, a blank line between two,
for a Claude Doc: the hook lints that as a markdown note under Tell.

Kind inference, deliberately simple:
- a JSON key named title or name gives heading, description gives prose, label
  gives label, whatever the string holds;
- a string under input or replace (Pencil's snippet and its edit) is code, and
  only its quoted literals are read. Each takes its kind from the identifier right
  before the opening parenthesis of the call it sits in, split into camelCase and
  underscore tokens and matched whole: button or btn gives button; heading, title,
  h1, h2 or h3 gives heading; label gives label. With no such token (Pencil's
  Insert, Update, addText, or no call at all) the kind is label at 4 words or
  fewer and prose above that, so body text is not held to a label's cap;
- every other string is markdown and goes through prose.walk(), the walker the
  markdown files use, so a plain blockquote (somebody else's words), a fenced
  block, front matter and an HTML comment drop here exactly as they do in a note.
  A heading row stays a heading; any other row takes the key's kind above, or
  prose. Inline code, urls and links are blanked the way walk() masks them.
  Nothing outside the code keys is parsed as code, however much it looks like it.
A string holding the ignore marker is skipped whole, and so are strings and
objects under find and target (the text an edit removes), paths, urls and ids.
A button is kept at one word; every other row needs two.
"""
from __future__ import annotations

import json
import re
import sys

from .blocks import LIST_ITEM
from .config import IGNORE_MARKER
from .prose import seal, walk

LITERAL = r"""'((?:\\.|[^'\\\n])*)'|"((?:\\.|[^"\\\n])*)"|`((?:\\.|[^`\\\n])*)`"""
TOKEN = re.compile(LITERAL + r"|([A-Za-z_$][\w$]*)|([()])|\S")
SKIP_KEYS = {"file_path", "filePath", "path", "url", "id", "kind", "type", "object", "engine",
             "name_id", "find", "target"}
CODE_KEYS = {"input", "replace"}
KEY_KINDS = {"title": "heading", "name": "heading", "description": "prose", "label": "label"}
CALL_KINDS = {"button": "button", "btn": "button", "heading": "heading", "title": "heading",
              "h1": "heading", "h2": "heading", "h3": "heading", "label": "label"}
CAMEL = re.compile(r"[A-Z]+(?![a-z])\d*|[A-Z]?[a-z]+\d*|\d+")


def _unescape(s: str) -> str:
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n")


def _call_kind(ident: str, text: str) -> str:
    for token in CAMEL.findall(ident):
        if token.lower() in CALL_KINDS:
            return CALL_KINDS[token.lower()]
    return "label" if len(text.split()) <= 4 else "prose"


def _literals(code: str) -> list[tuple[str, str]]:
    """Walk the code token by token. A literal is consumed whole, so a paren
    inside one never moves the list of open calls."""
    out, calls, prev = [], [], ""
    for m in TOKEN.finditer(code):
        a, b, c, ident, paren = m.groups()
        if paren == "(":
            calls.append(prev)
        elif paren == ")" and calls:
            calls.pop()
        elif a is not None or b is not None or c is not None:
            for line in _unescape(a or b or c or "").splitlines():
                out.append((_call_kind(calls[-1] if calls else "", line), line))
        prev = ident or ""
    return out


def _leaves(obj, key: str = ""):
    """(key, string) for every string a reader could see."""
    if key in SKIP_KEYS:
        return
    if isinstance(obj, str):
        if IGNORE_MARKER not in obj[:4096]:
            yield key, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _leaves(v, k)
    elif isinstance(obj, list):
        for v in obj:
            yield from _leaves(v, key)


def _rows(key: str, text: str) -> list[tuple[str, str]]:
    if key in CODE_KEYS:
        return _literals(text)
    kind = KEY_KINDS.get(key, "prose")
    return [("heading" if k == "heading" else kind, " ".join(LIST_ITEM.sub("", m).split()))
            for _ln, k, m, _u in walk(text)]


def extract(tool_input, floor: int = 2) -> list[tuple[str, str]]:
    out, seen = [], set()
    for kind, text in (r for key, t in _leaves(tool_input) for r in _rows(key, t)):
        pair = (kind, text.strip())
        if len(pair[1].split()) >= (1 if kind == "button" else floor) and pair not in seen:
            seen.add(pair)
            out.append(pair)
    return out


def documents(tool_input) -> list[str]:
    """Each string of two words or more, once, whole, and sealed, so a fence or
    a comment one string leaves open cannot hide the next. A Doc's name or title
    is a plain line, not a '# ' heading: tier 1 skips a markdown heading outside
    Show, and a banned phrase in a title is still copy a reader sees."""
    out: list[str] = []
    for _key, text in _leaves(tool_input):
        if len(text.split()) >= 2 and seal(text) not in out:
            out.append(seal(text))
    return out


def main(argv: list[str] | None = None) -> int:
    markdown = "--markdown" in (sys.argv[1:] if argv is None else argv)
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return 0
    if not isinstance(data, dict):
        return 0
    tool_input = data.get("tool_input", {})
    if markdown:
        # The blank first line keeps a string that opens on '---' from reading
        # as front matter and hiding the rest.
        print("\n" + "\n\n".join(documents(tool_input)))
        return 0
    for kind, text in extract(tool_input):
        print(f"{kind}\t{text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
