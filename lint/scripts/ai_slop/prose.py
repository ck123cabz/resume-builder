"""Markdown to prose lines: what the rules read, and what they never see."""
from __future__ import annotations

import re

from .mask import (
    ATTRIBUTION, CALLOUT, FENCE, HEADING, HTML_CLOSE, HTML_OPEN, INLINE_CODE,
    MDLINK, PROVENANCE, TABLE_ROW, URL, WIKILINK, _blank, _fit,
)


def walk(text: str) -> list[tuple[int, str, str, str]]:
    """Return (1-based line number, kind, masked, unmasked) per kept line;
    kind is "prose" or "heading".

    Dropped: YAML frontmatter, fenced code, HTML comments, table rows,
    provenance footers, and plain blockquotes. Headings are kept and tagged so a
    headings pass can read them; prose_lines filters them out. Obsidian callouts
    are blockquotes but they hold our own prose, so their content is kept with the
    '>' markers stripped.

    On a prose row the masked and unmasked forms are the same length, character for
    character. A heading row's masked slot is the bare heading text, so the two
    differ there.
    """
    out: list[tuple[int, str, str, str]] = []
    lines = text.splitlines()
    in_fence = False
    in_front = False
    in_html = False
    # None = not in a blockquote; True = callout (keep); False = plain quote (drop)
    quote_keep: bool | None = None

    for i, raw in enumerate(lines, start=1):
        if i == 1 and raw.strip() == "---":
            in_front = True
            continue
        if in_front:
            if raw.strip() in ("---", "..."):
                in_front = False
            continue

        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # HTML comments are notes to whoever edits the file next, and the one in
        # both project templates propagates into every project note made from them.
        if in_html:
            if HTML_CLOSE.search(raw):
                in_html = False
            continue
        if HTML_OPEN.search(raw):
            if not HTML_CLOSE.search(raw):
                in_html = True
            continue

        stripped = raw.strip()

        if stripped.startswith(">"):
            if quote_keep is None:
                quote_keep = bool(CALLOUT.match(raw))
            if not quote_keep:
                continue
            raw = re.sub(r"^\s*>+\s?", "", raw)
            # The callout's own title line is structure, not prose.
            if CALLOUT.match(stripped):
                continue
            stripped = raw.strip()
        else:
            if stripped == "":
                quote_keep = None
            elif quote_keep is not None:
                quote_keep = None

        if not stripped:
            continue
        if HEADING.match(raw):
            out.append((i, "heading", stripped.lstrip("#").strip(), raw))
            continue
        if TABLE_ROW.match(raw):
            continue
        if stripped in ("---", "***", "___"):
            continue
        if PROVENANCE.match(stripped):
            continue

        # The attribution is blanked in the masked form only. Tier counting and
        # the em-dash cap must not score a book title, but the thin-sentence rule
        # reads the unmasked form and a cited finding is somebody else's sentence:
        # "— *The Mom Test*" is the name that keeps its Why line off the list.
        unmasked = raw
        masked = ATTRIBUTION.sub(_blank, raw)
        masked = INLINE_CODE.sub(_blank, masked)
        masked = URL.sub(_blank, masked)
        masked = MDLINK.sub(lambda m: _fit("] ", m.end() - m.start()), masked)
        # A wikilink label is the title of a note, the same class of thing as a
        # book title. All 4 'register' hits in project-ship.md are the names of
        # two method notes, Open questions register and Risk register, and the
        # only way to clear them by editing the template is to rename his notes.
        # The unmasked line keeps the link, so CARRIES still reads it as a name.
        masked = WIKILINK.sub(_blank, masked)
        if masked.strip():
            out.append((i, "prose", masked, unmasked))
    return out


def seal(text: str) -> str:
    """text, with a fence or an HTML comment it leaves open closed at its end.

    Several strings joined into one note (the gate's Claude Doc path) must not
    hide each other: an op inserting "```bash\nnpm install" left walk() inside
    the fence, and every string after it went unread. This tracks the fence
    and comment state exactly as walk() does, and nothing else.
    """
    in_fence = in_html = False
    for raw in text.splitlines():
        if FENCE.match(raw):
            in_fence = not in_fence
        elif in_fence:
            continue
        elif in_html:
            in_html = not HTML_CLOSE.search(raw)
        elif HTML_OPEN.search(raw):
            in_html = not HTML_CLOSE.search(raw)
    return text + ("\n```" if in_fence else "") + ("\n-->" if in_html else "")


def prose_lines(text: str) -> list[tuple[int, str, str]]:
    """(1-based line number, masked prose, unmasked prose) per prose line."""
    return [(ln, m, u) for ln, k, m, u in walk(text) if k == "prose"]


def heading_lines(text: str) -> list[tuple[int, str]]:
    """(1-based line number, heading text without its # marks) per heading.
    Headings inside fences, frontmatter and plain blockquotes never appear. One
    inside an Obsidian callout does, with the '>' stripped, because callout content
    is our own prose."""
    return [(ln, m) for ln, k, m, _u in walk(text) if k == "heading"]
