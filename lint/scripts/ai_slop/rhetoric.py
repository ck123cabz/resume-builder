"""Rhetoric hints that need a paragraph: the fragment list, the isocolon pair,
the closing beat, and the antithesis the carrier test has to gate. the author's
9/18 bans; the line-level ones (litotes, tricolon, apophasis, aposiopesis, the
attribution flourish) are plain regexes in the phrase file. Inventory and
frequencies: skills/ai-filter/references/rhetoric-inventory.md.
"""
from __future__ import annotations

import re

from .blocks import _line_at, paragraphs, sentence_spans
from .report import Hit
from .sentences import CARRIES, _has_name, backed

# A finite verb somewhere in the piece means it is a clause, not a fragment. The
# irregular pasts are listed because "-ed" never reaches them: "he went, she left".
VERBISH = re.compile(
    r"\b(?:is|are|was|were|be|been|has|have|had|do|does|did|can|will|would|should|"
    r"could|may|might|must|went|sent|left|made|said|told|took|got|came|found|gave|"
    r"kept|ran|saw|wrote|began|brought|thought|felt|held|[a-z]{3,}(?:s|ed|ing))\b",
    re.IGNORECASE,
)
LABEL_ROW = re.compile(r"^[^:]{1,30}:\s*\S")
SHORT = 9        # isocolon: both sentences under this many words
BEAT = 8         # closing beat: last sentence under this many words
OPENER = 5       # fragment opener: first sentence at most this many words
# A pronoun subject or a negated verb makes it a clause VERBISH cannot see: "I don't know."
SUBJECT = re.compile(r"\b(?:I|you|we|he|she|they|it)\b|n['’]t\b", re.IGNORECASE)
STATUS = re.compile(r"(?:No|Nothing|Not)\b")


def _carried(source: str) -> bool:
    """A digit, a quote, a wikilink, a marker or a name in the unmasked slice.

    Narrower than backed(), which also counts a spelled number word. The list
    the rule is named for is "One rule, three people, no answer", where "three"
    is the rhythm and not a count; a fragment list that carries a real number
    is a stat row and keeps its commas.
    """
    return bool(CARRIES.search(source) or _has_name(source))


def _words(s: str) -> list[str]:
    return [w for w in re.split(r"\s+", s.strip()) if w]


def _frame(s: str) -> str:
    """The first word plus the part of speech guess of the second, as a crude frame."""
    w = _words(s)
    return (w[0].lower() + " " + ("V" if VERBISH.fullmatch(w[1]) else "N")) if len(w) > 1 else ""


def fragment_list(sent: str) -> bool:
    """Two or more comma pieces, none of them a clause. Reads the unmasked
    slice: inline code and wikilinks mask to spaces, and a piece that shrinks
    under the 4-word ceiling makes a fragment list out of a full sentence."""
    pieces = [p.strip() for p in sent.rstrip(".;!?").split(",")]
    if len(pieces) < 2 or LABEL_ROW.match(sent.strip()):
        return False
    return all(p and not VERBISH.search(p) and len(_words(p)) <= 4 for p in pieces)


def _sentences(text: str, raw: str):
    """(offset, sentence, unmasked source) per sentence in a joined block.

    The source runs from where the last sentence ended, the way thin_sentences
    reads it: masks are length-preserving, so a wikilink or an inline marker
    opening the sentence is in the slice even though the split walked past it.
    """
    out, prev = [], 0
    for start, sent in sentence_spans(text):
        end = start + len(sent)
        source, prev = raw[prev:end], end
        if sent.strip():
            out.append((start, sent.strip(), source))
    return out


def _isocolon(sents, starts) -> list[Hit]:
    """Consecutive short sentences sharing an opening word or a frame.

    Both need 2 words. A one-word sentence has no frame, and two empty frames
    compared equal, so "Ana. Ben." and the "3. 4." a numbered list leaves
    behind read as a pair. The shared opener has to start with a letter for
    the same reason: a mask can leave a comma where the first word was.
    """
    out: list[Hit] = []
    for (_st1, a, sa), (st2, b, sb) in zip(sents, sents[1:]):
        wa, wb = _words(a), _words(b)
        if not (2 <= len(wa) < SHORT and 2 <= len(wb) < SHORT):
            continue
        fa, fb = _frame(a), _frame(b)
        same = (wa[0].lower() == wb[0].lower() and wa[0][:1].isalpha()) or (fa and fa == fb)
        if same and not (_carried(sa) or _carried(sb)):
            out.append(Hit(_line_at(starts, st2), "STRUCT", "isocolon-pair", a + " " + b))
    return out


def rhetoric_hits(lines, cfg: dict) -> list[Hit]:
    anti = re.compile(cfg["rhetoric"]["antithesis"], re.IGNORECASE)
    out: list[Hit] = []
    for text, raw, starts in paragraphs(lines):
        sents = _sentences(text, raw)
        for st, s, source in sents:
            if fragment_list(source) and not _carried(source):
                out.append(Hit(_line_at(starts, st), "STRUCT", "fragment-list", s))
            # "Rai is his son, not his daughter" is a correction and keeps its
            # X-not-Y; "a clean open, not a verdict" states nothing and loses it.
            if anti.search(s) and not backed(s, source):
                out.append(Hit(_line_at(starts, st), "STRUCT", "antithesis", s))
        out.extend(_isocolon(sents, starts))
        if len(sents) >= 2:
            st, last, source = sents[-1]
            if len(_words(last)) < BEAT and not _residue(last) and not backed(last, source):
                out.append(Hit(_line_at(starts, st), "STRUCT", "closing-beat", last))
            st, first, source = sents[0]
            if _fragment_opener(first, source):
                out.append(Hit(_line_at(starts, st), "STRUCT", "fragment-opener", first))
    return out


def _fragment_opener(first: str, source: str) -> bool:
    """The closing beat's twin at the other end: "One correction." or "Then the
    other half." naming a topic the next sentence is about. Roxby's Style Patch
    (2026) bans it; 9 in the feed on 9/27, 8 of them this shape. Merge it into
    the sentence it introduces."""
    return (len(_words(first)) <= OPENER and not VERBISH.search(first)
            and not SUBJECT.search(first) and not _residue(first) and not _carried(source))


def _residue(last: str) -> bool:
    """Not a sentence a writer ended on: what a mask left behind (it opens on a
    bracket or punctuation, or keeps fewer than two words of letters), a line
    ending in a colon, which introduces what follows it, or a status line: "No
    campaign is paused." opens on No, Nothing or Not and reports a state."""
    words = [w for w in last.split() if re.search(r"[A-Za-z]", w)]
    return (not last[:1].isalnum() or len(words) < 2 or last.endswith(":")
            or bool(STATUS.match(last)))
