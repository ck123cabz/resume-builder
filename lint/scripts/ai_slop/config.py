"""Paths, thresholds and the phrase file. Shared by every module in the package."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DEFAULT_PHRASES = REPO / "config" / "ai-slop-phrases.json"
IGNORE_MARKER = "ai-slop-lint: ignore-file"

# A rate needs a floor under it. One "scope" in an 80-word note is 12/1000 and
# means nothing; the density rules only fire once there is something to a rate.
MIN_PHRASE = 2
MIN_TOTAL = 3
MIN_EM_DASH = 3

# Other people's words, machine state, and things nobody reads as prose.
SKIP_PARTS = (
    "knowledge/corpus/",
    "archive/",
    "memory/",
    ".claude/",
    ".git/",
    "node_modules/",
    "__pycache__/",
    "04-resources/attachments/",
    ".venv/",
    "graphify-out/",
)


class PhraseFileError(ValueError):
    """A phrase file that parses but has lost a block the rules read."""


# A rule reading a key that is gone used to raise KeyError mid-run and exit 1,
# which every hook reads as "hints found". Missing blocks exit 3 instead.
REQUIRED_KEYS = (
    "tier1", "tier2", "structural", "certainty", "coined_names", "density",
    "rhetoric", "shared", "mention_cues", "jobs", "banned_devices",
)


def load_phrases(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    missing = [k for k in REQUIRED_KEYS if k not in cfg]
    if missing:
        raise PhraseFileError(f"phrase file {path} is missing: {missing}")
    return cfg
