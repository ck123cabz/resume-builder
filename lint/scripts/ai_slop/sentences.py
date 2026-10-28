"""Thin sentences: no person, time, number or quote."""
from __future__ import annotations

import re

from .blocks import _line_at, paragraphs, sentence_spans
from .report import Hit

# A sentence carrying no person, no time, no number and no quote is commentary.
# People talking face to face say names, times, amounts, and what someone said.
# Short declaratives are speech-like and exempt; the target is the medium-length
# abstract sentence that sounds written.

# "nine hours later" carries a time as surely as "9 hours" does. Bare "one" is
# excluded: it is a pronoun far more often than a count in this prose.
NUMBER_WORD = re.compile(
    r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen"
    r"|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty"
    r"|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|dozen|twice"
    r"|half|first|third)\b",
    re.IGNORECASE,
)
CARRIES = re.compile(
    r"\d"                                  # a number or a clock time
    r"|\[\[[^\]]+\]\]"                     # a wikilink names a thing
    r"|\[[A-Z][A-Za-z:*-]*\]"               # a provenance or knowledge-type marker
    r"|[\"\u201c\u201d]"                     # a quote
    r"|`[^`]+`"                             # inline code names a file, a command, a key
)
MIN_SENTENCE_WORDS = 10

# Capitalised words that read as grammar rather than as names, wherever they sit
# in a sentence. Anything capitalised and not on this list reads as a name.
# They live in code, not in config/ai-slop-phrases.json, because that file holds
# phrases the linter bans and these are words it has to know to ban nothing.
# 25 joined on 9/18, "various" among them: "Various improvements were made to
# ensure reliability" is the commit body this rule exists to catch, and it was
# clearing itself on its own first word.
SENTENCE_OPENERS = frozenset("""
a an and as at both but by each every for from he her here his how i if in into
it its more most no nobody not nothing now of on once one only or our over she
so some still such than that the their then there these they this those to two
under until up we what when where which who why with without you your yesterday
today after before during also however meanwhile because since about across
various several many overall additionally furthermore moreover recently while
although despite instead rather perhaps given together ultimately notably
importantly everything anyone someone sometimes often usually
""".split())


def _has_name(text: str) -> bool:
    """A capitalised word that is not a common opener reads as a name."""
    for w in text.split():
        bare = w.strip("*_`'\"“”‘’(),.:;!?-")
        if not bare[:1].isalpha() or not bare[:1].isupper():
            continue
        if bare.lower() in SENTENCE_OPENERS:
            continue
        return True
    return False


def backed(sentence: str, source: str) -> bool:
    """A number, a quote, a wikilink, a marker, a number word, or a name,
    in the sentence or its unmasked source."""
    return bool(
        CARRIES.search(sentence)
        or CARRIES.search(source)
        or NUMBER_WORD.search(sentence)
        or _has_name(sentence)
        or _has_name(source)
    )


def thin_sentences(lines):
    """Flag sentences with no person, time, number or quote in them.

    A hint, not a verdict. The rule the author set on 2026-07-29: a sentence
    people would say to each other face to face carries a name, a time, an
    amount, or something somebody said. One with none of those is commentary.

    Carriers are checked against the UNMASKED slice of the same sentence, because
    prose_lines masks inline code and that is where the [M:author] markers live.
    """
    out = []
    for text, raw, starts in paragraphs(lines):
        prev = 0
        for start, sent in sentence_spans(text):
            end = start + len(sent)
            s = sent.strip()
            # The unmasked span for this sentence, from where the last one ended.
            # Masks are length-preserving, so the span holds the same characters
            # with the code and links restored. Reading the whole block let one
            # name clear every sentence beside it: on 9/18 "the author" at the
            # start of a brief backed "clearly made progress" three sentences
            # later. Starting at `start` lost the other end. A construct opening
            # a sentence masks to spaces, the split reads those as the gap
            # between two sentences, and the offset comes back past it, so
            # "[[proof-of-demand]] is the note" was judged on "is the note".
            source = raw[prev:end]
            prev = end
            if len(s.split()) < MIN_SENTENCE_WORDS:
                continue
            # A name counts anywhere, including at the start. "Doris says X" is
            # exactly the face-to-face form the rule is meant to reward.
            if backed(s, source):
                continue
            # Report the line the sentence starts on, not the line the block does.
            out.append(Hit(_line_at(starts, start), "STRUCT", "thin-sentence", s))
    return out
