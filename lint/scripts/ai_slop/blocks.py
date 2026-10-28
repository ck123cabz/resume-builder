"""Group prose lines into blocks so a hard-wrapped sentence is judged whole."""
from __future__ import annotations

import re

from .mask import _blank

LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
# "Sung et al. (2016) found" is one sentence. The lookbehind has to be fixed-width,
# so it names the six characters of "et al." rather than every abbreviation.
SENT_SPLIT = re.compile(r"(?<=[.!?])(?<!\bet al\.)\s+")
BOLD = re.compile(r"\*\*[^*]+\*\*")


def paragraphs(lines):
    """Group prose lines into blocks, so a sentence that wraps stays one sentence.

    Every markdown file in this repo is hard-wrapped near 95 characters. Splitting
    sentences inside a single line judged each half separately, and a name or a
    time sitting on the other half did not count: 58 of the rule's 68 hits on
    2026-07-30 were fragments, 47 of them starting lowercase.

    A block ends where prose_lines dropped a line (a gap in the numbering, which
    is a blank line, a heading or a table) and at the start of a new list item,
    so two bullets never merge into one sentence.
    """
    blocks = []  # (joined masked, joined unmasked, [(char offset, line number)])
    prev_ln = 0
    masked: list[str] = []
    unmasked: list[str] = []
    starts: list[tuple[int, int]] = []
    width = 0

    def flush():
        if masked:
            blocks.append((" ".join(masked), " ".join(unmasked), starts))

    for ln, m, u in lines:
        if masked and (ln != prev_ln + 1 or LIST_ITEM.match(m)):
            flush()
            masked, unmasked, starts, width = [], [], [], 0
        # Trim both by the UNMASKED line's bounds. Stripping each on its own
        # breaks the alignment the length-preserving masks exist to hold: a line
        # ending in `inline code` masks to trailing spaces and strips shorter.
        lead, tail = len(u) - len(u.lstrip()), len(u.rstrip())
        starts.append((width, ln))
        masked.append(m[lead:tail])
        unmasked.append(u[lead:tail])
        width += (tail - lead) + 1  # the joining space
        prev_ln = ln

    flush()
    return blocks


def _line_at(starts: list[tuple[int, int]], offset: int) -> int:
    """Which source line a character offset inside a joined block came from."""
    ln = starts[0][1]
    for start, n in starts:
        if start > offset:
            break
        ln = n
    return ln


def sentence_spans(text: str):
    """Yield (offset, sentence) for each sentence in a joined block.

    Bold lead-in labels are layout rather than sentences and are blanked in
    place, so the offsets stay valid in both the masked and unmasked text.
    """
    body = BOLD.sub(_blank, text)
    pos = 0
    for sent in SENT_SPLIT.split(body):
        start = body.find(sent, pos)
        if start < 0:
            start = pos
        pos = start + len(sent)
        yield start, sent
