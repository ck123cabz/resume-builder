"""Hits, the per-file report, exit codes, and the two output formats."""
from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Hit:
    line: int
    kind: str  # TIER1 | TIER2 | STRUCT
    label: str
    text: str


@dataclass
class Report:
    path: str
    words: int = 0
    hits: list[Hit] = field(default_factory=list)
    tier2_counts: dict[str, int] = field(default_factory=dict)
    em_dashes: int = 0
    over_caps: list[str] = field(default_factory=list)

    @property
    def tier1(self) -> list[Hit]:
        return [h for h in self.hits if h.kind == "TIER1"]

    @property
    def struct(self) -> list[Hit]:
        return [h for h in self.hits if h.kind == "STRUCT"]

    def exit_code(self) -> int:
        if self.tier1:
            return 2
        if self.over_caps or self.struct:
            return 1
        return 0


def fmt_text(rep: Report, quiet: bool) -> str:
    lines = []
    if not quiet:
        for h in rep.hits:
            snippet = h.text if len(h.text) <= 96 else h.text[:93] + "..."
            lines.append(f"{rep.path}:{h.line}  {h.kind:<6} {h.label}  | {snippet}")
    t1, t2, st = len(rep.tier1), len(rep.tier2_counts), len(rep.struct)
    total2 = sum(rep.tier2_counts.values())
    per_k = (rep.words / 1000.0) or 1e-9
    if rep.tier1:
        verdict = "FAIL"
    elif rep.over_caps or rep.struct:
        verdict = "WARN"
    elif rep.hits:
        verdict = "NOTE"  # hits present, all under cap
    else:
        verdict = "CLEAN"
    lines.append(
        f"{rep.path}: {verdict} — {len(rep.tier1)} tier1, {total2} tier2 "
        f"({total2 / per_k:.1f}/1000) across {t2} phrases, {st} structural, "
        f"em-dash {rep.em_dashes / per_k:.1f}/1000, {rep.words} words"
    )
    for c in rep.over_caps:
        lines.append(f"  over cap: {c}")
    return "\n".join(lines)


def to_json(reports: list[Report], errors: list[tuple[str, str]] = ()) -> str:
    """One entry per report, then {"path", "error"} per file that could not be read."""
    return json.dumps(
        [
            {
                "path": r.path,
                "words": r.words,
                "exit": r.exit_code(),
                "over_caps": r.over_caps,
                "em_dashes": r.em_dashes,
                "hits": [
                    {"line": h.line, "kind": h.kind, "label": h.label, "text": h.text}
                    for h in r.hits
                ],
            }
            for r in reports
        ] + [{"path": path, "error": error} for path, error in errors],
        indent=2,
    )
