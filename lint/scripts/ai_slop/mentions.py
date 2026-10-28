"""Quoted spans that are mentions, so the shared word lists skip them.

CLAUDE.md: other people's words are never filtered. A quote is someone's
speech, a title, or a word being talked about ("the word 'synergy'"). Scare
quotes around a lone selling word ('Our "seamless" onboarding') are none of
those, so a quote only counts as a mention when it holds two or more words,
or one word with a cue from the phrase file's mention_cues within three
words in front of it.

The regexes are shape, not vocabulary: the cue words live in the JSON.
"""
from __future__ import annotations

import re

DOUBLE = re.compile(r'"[^"\n]*"|“[^”\n]*”')
# A single quote pair, straight or curly, with no space just inside either mark
# and a non-word character just outside it. That keeps an apostrophe inside a
# word ("don't", "Ana's") from opening or closing a span. One at a word's edge
# still can: the plural possessive in "clients'" closes a span, and the one in
# "'90s" opens one. SINGLE_MAX_WORDS is what stops such a span from running
# across a sentence: "the '90s ... our clients'" is over six words and skipped.
SINGLE = re.compile(r"(?<!\w)'(?=\S)[^\n]*?(?<=\S)'(?!\w)"
                    r"|‘(?=\S)[^\n]*?(?<=\S)’(?!\w)")
SINGLE_MAX_WORDS = 6
EDGE = ".,;:!?()\"'“”‘’"


def _cued(before: str, cues: set[str]) -> bool:
    return any(w.strip(EDGE).lower() in cues for w in before.split()[-3:])


def mention_spans(text: str, cues: list[str]) -> list[tuple[int, int]]:
    """(start, end) of every quoted span in text that is a mention."""
    cue_set = set(cues)
    out: list[tuple[int, int]] = []
    for rx, cap in ((DOUBLE, None), (SINGLE, SINGLE_MAX_WORDS)):
        for q in rx.finditer(text):
            n = len(q.group()[1:-1].split())
            if cap is not None and n > cap:
                continue
            if n >= 2 or _cued(text[:q.start()], cue_set):
                out.append(q.span())
    return out
