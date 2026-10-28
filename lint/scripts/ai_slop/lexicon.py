"""Lexicon: tier-1 bans, tier-2 density caps, and the em-dash count."""
from __future__ import annotations

import re

from .config import MIN_EM_DASH, MIN_PHRASE, MIN_TOTAL
from .report import Hit, Report


def phrase_re(phrase: str) -> re.Pattern:
    """Whole-phrase match. Lookarounds rather than \\b so trailing punctuation
    ('and honestly?') anchors correctly, and hyphen is excluded on both sides so
    'register' does not fire inside 'gap-register'. An apostrophe in the phrase
    also matches the curly one Word and PowerPoint type, so "you’re all set" in
    a pptx is the same phrase as "you're all set"."""
    return re.compile(
        r"(?<![A-Za-z0-9-])" + re.escape(phrase).replace("'", "['\u2019]")
        + r"(?![A-Za-z0-9-])",
        re.IGNORECASE,
    )


def inflected(word: str) -> re.Pattern:
    """'leverage' also catches leverages, leveraged, leveraging. An adjective
    ending in -less, -ful or -ive also takes -ly: seamlessly, powerfully,
    comprehensively. Only those: "potentially" is a hedge, not a pitch.

    An e-final stem drops the e before -ing and -ed, so the suffixes hang off
    two different stems. Gluing them all to the whole word asked for
    'leverageing', and every -ing in the selling list went unseen.
    """
    w = re.escape(word)
    ly = "|ly" if word.endswith(("less", "ful", "ive")) else ""
    body = (f"{w}(?:s|d{ly})?|{re.escape(word[:-1])}(?:ing|ed)" if word.endswith("e")
            else f"{w}(?:s|es|ed|ing{ly})?")
    return re.compile(rf"(?<![A-Za-z0-9-])(?:{body})(?![A-Za-z0-9-])", re.IGNORECASE)


# A labelled entry — "**8:18 am** — the Dana note", "- [Title](f.md) — hook".
# The dash separates a label from its content, which is layout rather than the
# dramatic pause the rule is aimed at. Only the leading one is exempt.
#
# The link form was added after the hook flagged MEMORY.md at 32 em dashes per
# 1000 words on its first real run. Every one was an index entry.
#
# The wikilink form is the '## Related' block the vault audit writes:
# '- [[path|Title]] — why it relates'. It only anchors on the UNMASKED line,
# because a wikilink masks down to its bare display text and leaves no brackets
# behind. All 5 dashes in 03-areas/making-money.md are this separator and every
# one of them counted as prose, which tripped the cap on 2026-07-30.
LABEL_DASH = re.compile(
    r"^\s*(?:[-*+]\s*)?"
    r"(?:\*\*[^*]+\*\*|`[^`]+`|__[^_]+__|\[\[[^\]]+\]\]|\[[^\]]+\]|\*[^*]+\*"
    r'|"[^"]+"|“[^”]+”)'
    r"\s+—\s"
)


def count_em_dashes(lines) -> int:
    total = 0
    for _, text, raw in lines:
        n = text.count("—")
        # Either form: the markdown-link label only survives masking, the
        # wikilink label only survives in the raw line.
        if n and (LABEL_DASH.match(text) or LABEL_DASH.match(raw)):
            n -= 1
        total += n
    return total


def tier1_hits(lines, cfg: dict, rep: Report) -> None:
    """Tier-1 hits onto rep, over whichever rows the caller hands in: every row
    but a markdown section title outside Show (core.lint_tagged). A phrase with
    a `literal` entry is spared when that regex matches the text after it: the
    beam is load-bearing, the sentence is not."""
    literal = cfg["tier1"].get("literal", {})
    for phrase in cfg["tier1"]["phrases"]:
        rx = phrase_re(phrase)
        spare = re.compile(literal[phrase], re.IGNORECASE) if phrase in literal else None
        for ln, t, _r in lines:
            for m in rx.finditer(t):
                if not (spare and spare.match(t, m.end())):
                    rep.hits.append(Hit(ln, "TIER1", phrase, t.strip()))


def tier2_hits(lines, cfg: dict, rep: Report, per_k: float) -> None:
    """Tier-2 hits and counts, and the two tier-2 caps, onto rep. Body rows only,
    because the caps are a density over the body's words."""
    t2 = cfg["tier2"]
    for phrase in t2["phrases"]:
        rx = phrase_re(phrase)
        n = 0
        for ln, t, _r in lines:
            for _ in rx.finditer(t):
                n += 1
                rep.hits.append(Hit(ln, "TIER2", phrase, t.strip()))
        if n:
            rep.tier2_counts[phrase] = n
            if n >= MIN_PHRASE and n / per_k > t2["per_phrase_per_1000"]:
                rep.over_caps.append(
                    f"{phrase} {n / per_k:.1f}/1000 (cap {t2['per_phrase_per_1000']})"
                )

    total2 = sum(rep.tier2_counts.values())
    if total2 >= MIN_TOTAL and total2 / per_k > t2["total_per_1000"]:
        rep.over_caps.append(
            f"tier2 total {total2 / per_k:.1f}/1000 (cap {t2['total_per_1000']})"
        )


def em_dash_cap(lines, cfg: dict, rep: Report, per_k: float) -> None:
    rep.em_dashes = count_em_dashes(lines)
    cap = cfg["density"]["em_dash_per_1000"]
    if rep.em_dashes >= MIN_EM_DASH and rep.em_dashes / per_k > cap:
        rep.over_caps.append(f"em dashes {rep.em_dashes / per_k:.1f}/1000 (cap {cap})")
