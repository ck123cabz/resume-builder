"""The four prose jobs, plus the claim rule every job reads. Claims: a claim
needs a citation or a reference back to cited studies in its own sentence, or
outside Prove a link. Persuade: Bonnier's direct form (50 words, 3 seconds,
2 you per we), run once per document. Reply: a reply to a prospect reads
Persuade's lists and the claim rule, without Persuade's document shape, which
a two-line answer to a question cannot carry. Tell: the sentence rule and
12-hour time. The thread (the author's 9/18 Ana update is the reference) is
judgment in the output style: its regex, tell/no-thread, was right about 1 hit
in 5 on the feed and came out on 9/19.

The four regexes below are grammar and shape, not vocabulary, so they stay in
code the way NUMBER_WORD does in sentences.py. Every phrase is in the JSON.
"""
from __future__ import annotations

import re

from .blocks import _line_at, paragraphs, sentence_spans
from .report import Hit

YOU = re.compile(r"\b(?:you|your|you're|yours)\b", re.IGNORECASE)
WE = re.compile(r"\b(?:we|our|us|we're|i|me|my|i'm)\b", re.IGNORECASE)
# Outside Prove only an anonymous group is a claim: "fresh evidence" and "the
# research skill found" are nouns in a brief, measured 9/27 over the feed.
PEOPLE = frozenset(("studies", "researchers", "experts", "scholars", "critics",
                    "observers", "analysts", "commentators"))
# A link, or the bold "**Transluce:**" label a news bullet names its source with.
SOURCE = re.compile(r"\]\(|https?://|\[\[|\*\*[^*]{2,40}:\*\*")
OPINION = re.compile(r"^(?:I think|I read|It seems|Seems like|My read)\b", re.IGNORECASE)
# The second lookahead is the range whose meridiem sits at the end: 4:00-9:00 pm
# reads 12-hour and the first half carries no am. 83 of the feed's 642 hits on
# 2026-09-18 were that shape. 22:05 to 23:00, with no meridiem anywhere, still fires.
TIME24 = re.compile(r"(?<![\dT:])(?:[01]?\d|2[0-3]):[0-5]\d(?![\d:])"
                    r"(?!\s*(?:[-–—]|to|and)\s*\d{1,2}:[0-5]\d\s*[ap]m)(?!\s*[ap]m)(?![+-]\d)")


def claim_hits(prose, cfg: dict, job: str) -> list[Hit]:
    """A claim clears on a citation, or on a reference back to studies already
    cited ("The eleven studies agree"). A bare number or year does not clear it:
    "Research suggests a 40% improvement" is the claim this rule is for.
    the author, decision 11, 9/18.

    "Already cited" is read in document order: a reference back counts only
    once some earlier sentence carried a citation. In a piece that cites
    nothing, "The studies show" is the same claim as "Studies show".

    Every job reads it since 9/27: "Experts say" has no source in a brief
    either (Bronsdon's avoid-ai-writing fires it in every register). Outside
    Prove a link in the sentence also clears it, because a note cites by link.
    A name elsewhere in the sentence does not: the experts stay anonymous.
    """
    p = cfg["jobs"]["prove"]
    label = "prove/claim-without-citation" if job == "prove" else "claim-without-source"
    claim, cite = re.compile(p["claim"], re.IGNORECASE), re.compile(p["citation"])
    back = re.compile(p["reference_back"], re.IGNORECASE)
    cited = False
    out: list[Hit] = []
    for text, raw, starts in paragraphs(prose):
        prev = 0
        for st, sent in sentence_spans(text):
            s = sent.strip()
            # From where the last sentence ended: a news bullet's link masks to
            # spaces the split walks past, and the link is the bullet's source.
            source, prev = raw[prev:st + len(sent)], st + len(sent)
            m = claim.search(s)
            own = bool(cite.search(s)) or (job != "prove" and bool(SOURCE.search(source)))
            if job != "prove" and m and (m.group(1) or "").lower() not in PEOPLE:
                m = None
            if (m and not own and not (cited and back.match(s))
                    and not OPINION.match(s)):
                out.append(Hit(_line_at(starts, st), "STRUCT", label, s))
            cited = cited or own
    return out


def persuade_hits(tagged, cfg: dict) -> list[Hit]:
    """The reader-facing three run once for the whole document: a pricing page
    carries its number in a label, and judging every row on its own would ask
    each button to hold one."""
    p = cfg["jobs"]["persuade"]
    all_text = " ".join(u.strip() for _ln, _k, _m, u in tagged)
    # Any kind, because a deck's title slide is tagged heading and "31 meetings in
    # 60 days" is the opening line Persuade exists to check. A one-word row is a
    # section label for what follows, not an opening line: the 9/18 pricing page
    # opens on "Pricing" with the number in the row under it.
    first = next((u.strip() for _ln, _k, _m, u in tagged if len(u.split()) > 1), "")
    ln = tagged[0][0] if tagged else 1
    out: list[Hit] = []
    for l, k, _m, u in tagged:
        n = len(u.split())
        if k in ("prose", "subtext") and n > p["max_words"]:
            out.append(Hit(l, "STRUCT", "persuade/words",
                           f"{n} words, cap {p['max_words']}: {u.strip()[:60]}"))
    you, we = len(YOU.findall(all_text)), len(WE.findall(all_text))
    if we and you < p["you_per_we"] * we:
        out.append(Hit(ln, "STRUCT", "persuade/pronouns", f"you:{you} we:{we}, want {p['you_per_we']}:1"))
    if first and not (re.search(r"\d", first) or YOU.search(first)):
        out.append(Hit(ln, "STRUCT", "persuade/first-line", first))
    if not re.search(r"\d", all_text):
        out.append(Hit(ln, "STRUCT", "persuade/no-number", "no tangible number anywhere in the piece"))
    return out


def tell_hits(prose) -> list[Hit]:
    """A clock time with no am or pm, which CLAUDE.md's time rule bans."""
    out: list[Hit] = []
    for text, _raw, starts in paragraphs(prose):
        for m in TIME24.finditer(text):
            out.append(Hit(_line_at(starts, m.start()), "STRUCT", "tell/no-am-pm", m.group(0)))
    return out


def prose_job_hits(tagged, cfg: dict, job: str) -> list[Hit]:
    prose = [(ln, m, u) for ln, k, m, u in tagged if k in ("prose", "subtext")]
    claims = claim_hits(prose, cfg, job)
    if job in ("prove", "reply"):
        return claims
    if job == "persuade":
        return claims + persuade_hits(tagged, cfg)
    return claims + tell_hits(prose)
