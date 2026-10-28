"""Regex hints from the phrase file. Each marks a candidate for the judgment pass."""
from __future__ import annotations

import re

from .lexicon import inflected
from .report import Hit


def structural_hits(lines, cfg: dict) -> list[Hit]:
    out: list[Hit] = []
    for rule in cfg["structural"]["rules"]:
        rx = re.compile(rule["pattern"], re.IGNORECASE)
        for ln, t, _r in lines:
            if rx.search(t):
                out.append(Hit(ln, "STRUCT", rule["id"], t.strip()))
    return out


def heading_hits_tagged(headings, cfg: dict) -> list[Hit]:
    """A heading that sells. From the 9/5 JD session, where the an agency template's
    section names were an agency's pitch. The words are the shared sell list,
    inflected the way shared_hits reads it, in every job: the list's jobs field
    governs the shared hits, not this rule.
    headings: (line, heading text), already stripped of its # marks or its tag."""
    rxs = [inflected(w) for w in cfg["shared"]["sell"]["words"]]
    return [Hit(ln, "STRUCT", "pitch-heading", h) for ln, h in headings
            if any(rx.search(h) for rx in rxs)]
