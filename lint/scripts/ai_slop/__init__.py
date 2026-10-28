"""Deterministic detector for AI writing tells. Usage: scripts/ai_slop_lint.py."""
from .blocks import paragraphs
from .cli import collect, lint_text_path, main, skipped, wanted
from .config import (
    DEFAULT_PHRASES, IGNORE_MARKER, REPO, SKIP_PARTS, PhraseFileError, load_phrases,
)
from .core import lint_tagged, lint_text
from .prose import prose_lines
from .readers import SUFFIXES, read_tagged
from .report import Hit, Report

__all__ = [
    "DEFAULT_PHRASES", "Hit", "IGNORE_MARKER", "PhraseFileError", "REPO", "Report",
    "SKIP_PARTS", "SUFFIXES",
    "collect", "lint_tagged", "lint_text", "lint_text_path", "load_phrases", "main",
    "paragraphs", "prose_lines", "read_tagged", "skipped", "wanted",
]
