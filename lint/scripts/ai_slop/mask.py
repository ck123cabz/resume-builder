"""Markdown masking. Length-preserving: masked[a:b] is the same span as unmasked[a:b]."""
from __future__ import annotations

import re

INLINE_CODE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+|obsidian://\S+")
WIKILINK = re.compile(r"\[\[([^\]|]*\|)?([^\]]*)\]\]")
MDLINK = re.compile(r"\]\([^)]*\)")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
FENCE = re.compile(r"^\s*(```|~~~)")
CALLOUT = re.compile(r"^\s*>+\s*\[!")
HTML_OPEN = re.compile(r"<!--")
HTML_CLOSE = re.compile(r"-->")

# Formats a skill is required to emit, which nobody reads as prose.
#
# The provenance footer is named in skills/cron-manager/references/delivery-contract.md:
# "panels, tables, and provenance lines are structured fields, exempt". It cites gap
# ids, so it carries the tier-2 word 'register' on every long-form file the fleet
# writes — 11 of the fleet's tier-2 hits on 2026-07-30 came from this one line.
PROVENANCE = re.compile(r"^\s*[*_]{0,2}Provenance:\s", re.IGNORECASE)

# A citation at the end of a line: "— *The Mom Test*", "— *Shape Up*". The title is
# somebody else's words and the dash in front of it is layout. project-ship.md scored
# 6 tier-2 hits on 'shape' this way, all of them the book called Shape Up.
ATTRIBUTION = re.compile(r"\s+—\s+[*_]{1,2}[^*_]+[*_]{1,2}\s*$")


def _blank(m: re.Match) -> str:
    return " " * (m.end() - m.start())


def _fit(text: str, width: int) -> str:
    """Pad a replacement out to the span it replaced.

    Masking has to be length-preserving so that a sentence found at masked[a:b]
    is the same characters as unmasked[a:b]. thin_sentences relies on that to
    check carriers against the unmasked text one sentence at a time instead of
    one paragraph at a time.
    """
    return text.ljust(width)[:width] if len(text) <= width else text[:width]
