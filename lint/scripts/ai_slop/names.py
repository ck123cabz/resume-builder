"""Coined names: Title Case phrases ending in a framework word.

From the portfolio guide, 1.4 and 3.3: name a pattern when it is validated, never
when it is exciting. "Social System" appears 42 times in the machine notes and is
not the name of anything the author made. His own project and area names are read
off the vault at run time so the rule follows his folders; product names sit in
the phrase file. A wikilinked name never reaches this rule: masking blanks it.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from .config import REPO
from .report import Hit

WORD = r"[A-Z][A-Za-z]+(?:-[A-Z][A-Za-z]+)?"


def kebab(name: str) -> str:
    return re.sub(r"[\s_]+", "-", name.strip()).lower()


@lru_cache(maxsize=8)
def vault_names(dirs: tuple[str, ...], root: Path = REPO) -> frozenset[str]:
    """Filename stems under each vault dir, lowercased. Cached per (dirs, root)."""
    out: set[str] = set()
    for d in dirs:
        p = root / d
        if p.is_dir():
            out.update(f.stem.lower() for f in p.rglob("*.md"))
    return frozenset(out)


def candidate_re(suffixes: list[str]) -> re.Pattern:
    tail = "|".join(re.escape(s) for s in suffixes)
    return re.compile(
        r"(?<![A-Za-z0-9-])(?:The\s+)?((?:%s\s+){1,3}(?:%s))(?![A-Za-z0-9-])" % (WORD, tail)
    )


def _allowed(name: str, allow: frozenset[str]) -> bool:
    # Right-aligned tails too, so a sentence-opening capital ("Yesterday Meta
    # Layer System") does not hide a vault name behind an extra word.
    words = name.split()
    # The range stops one short: a note called system.md must not exempt every "... System".
    return any(kebab(" ".join(words[i:])) in allow for i in range(len(words) - 1))


def coined_name_hits(lines, cfg: dict, root: Path = REPO) -> list[Hit]:
    cn = cfg["coined_names"]
    rx = candidate_re(cn["suffixes"])
    allow = vault_names(tuple(cn["vault_dirs"]), root) | frozenset(
        kebab(k) for k in cn["known"]
    )
    out: list[Hit] = []
    for ln, t, _r in lines:
        for m in rx.finditer(t):
            name = m.group(1)
            if _allowed(name, allow):
                continue
            out.append(Hit(ln, "STRUCT", "coined-name", name))
    return out
