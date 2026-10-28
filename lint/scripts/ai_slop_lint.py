#!/usr/bin/env python3
"""Deterministic detector for AI writing tells.

Entry point only. The code lives in scripts/ai_slop/, one concern per file; this
file keeps the path every hook, skill and test already calls.

Phrases and thresholds are data (config/ai-slop-phrases.json). Adding a phrase is
a data edit. Do not move phrases into the package.

Design: docs/superpowers/specs/2026-07-28-ai-slop-filter-design.md and
docs/superpowers/specs/2026-09-07-ai-slop-linter-v2-design.md

Usage:
    ai_slop_lint.py [PATH ...]           # files or dirs; stdin when no paths
    ai_slop_lint.py --format json FILE
    ai_slop_lint.py --quiet FILE         # summary lines only

Exit: 2 if any file holds a tier-1 phrase · else 3 if a file or the phrase file
was unreadable (json lists each) · else 1 for caps or structural hints · else 0.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ai_slop import *  # noqa: E402,F401,F403
from ai_slop.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
