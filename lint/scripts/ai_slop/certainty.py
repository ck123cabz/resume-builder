"""Certainty words with nothing behind them.

From the portfolio style guide, section 2.3: "proves", "reliably", "clearly" and
their kin are an overclaim when the sentence carries no number, name, quote or
source. Measured 9/7 before gating: clearly 22, proves 16, reliably 11 across 628
machine notes. The gate is the thin-sentence carrier test on the sentence's own
span, so "he clearly sent it at 4:12 am" passes on the time and "this clearly
worked" is the hit.
"""
from __future__ import annotations

import re

from .blocks import _line_at, paragraphs, sentence_spans
from .lexicon import phrase_re
from .mask import _blank
from .report import Hit
from .sentences import backed


def _rx(cfg: dict) -> re.Pattern:
    phrases = cfg["certainty"]["phrases"]
    return re.compile("|".join(phrase_re(p).pattern for p in phrases), re.IGNORECASE)


def _without(text: str, m: re.Match) -> str:
    return text[: m.start()] + _blank(m) + text[m.end():]


def certainty_hits(lines, cfg: dict) -> list[Hit]:
    rx = _rx(cfg)
    out: list[Hit] = []
    for text, raw, starts in paragraphs(lines):
        prev = 0
        for start, sent in sentence_spans(text):
            end = start + len(sent)
            # What the split ate in front of this sentence: masked whitespace,
            # which unmasked is the wikilink or the inline code that opened it.
            # thin_sentences had the same hole and the same repair on 9/18.
            lead, prev = raw[prev:start], end
            m = rx.search(sent)
            if not m:
                continue
            # The word itself must not count as a name when it opens the
            # sentence: "Clearly the run finished" is the hit, not a person
            # called Clearly. Masks are length-preserving, so m's offsets hold
            # against the aligned part of the span and lead goes in front.
            source = lead + _without(raw[start:end], m)
            if backed(_without(sent, m).strip(), source.strip()):
                continue
            out.append(Hit(_line_at(starts, start), "STRUCT", "certainty", sent.strip()))
    return out
