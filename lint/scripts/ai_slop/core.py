"""lint_text / lint_tagged: one document in, one Report out. The order of the
passes is the order the hits are meant to be read in."""
from __future__ import annotations

from .certainty import certainty_hits
from .config import IGNORE_MARKER
from .jobs import job_hits, shared_hits
from .lexicon import em_dash_cap, tier1_hits, tier2_hits
from .names import coined_name_hits
from .prose import walk
from .report import Report
from .rhetoric import rhetoric_hits
from .sentences import thin_sentences
from .structure import heading_hits_tagged, structural_hits

BODY_KINDS = ("prose", "subtext")


def lint_tagged(tagged, cfg: dict, path: str = "<stdin>", job: str = "tell",
                markdown: bool = False, whole_rows: bool = False) -> Report:
    """tagged: (line, kind, masked, unmasked). The prose passes read the body
    kinds; the headings pass reads heading rows; the shared word lists (in the
    jobs each names) and the job rules read every row, so a button and a label
    are graded too. Tier 1
    reads every row too, except a markdown heading outside Show: a section title
    is structure (spec 2026-07-28). A slide title or a docx heading is copy.

    Words counts the body only, which is what the phrase file's density block
    says it counts. A heading's words have never been in the markdown total and
    adding them here would move every density number in the vault.
    """
    rep = Report(path=path)
    # whole_rows: every row is a paragraph of its own (a Word paragraph, a slide's
    # line), so none may join the next the way a hard-wrapped markdown line does.
    # paragraphs() joins rows on consecutive lines, so the rows run as 2, 4, 6 and
    # every hit maps back to its paragraph index or slide number at the end.
    lines = [ln for ln, _k, _m, _u in tagged]
    if whole_rows:
        tagged = [(2 * i, k, m, u) for i, (_ln, k, m, u) in enumerate(tagged, 1)]
    prose = [(ln, m, u) for ln, k, m, u in tagged if k in BODY_KINDS]
    headings = [(ln, m) for ln, k, m, _u in tagged if k == "heading"]
    rep.words = sum(len(m.split()) for _ln, m, _u in prose)
    per_k = (rep.words / 1000.0) or 1e-9

    every = not markdown or job == "show"
    banned = [(ln, m, u) for ln, k, m, u in tagged if every or k in BODY_KINDS]
    tier1_hits(banned, cfg, rep)
    tier2_hits(prose, cfg, rep, per_k)
    rep.hits.extend(structural_hits(prose, cfg))
    rep.hits.extend(heading_hits_tagged(headings, cfg))
    rep.hits.extend(thin_sentences(prose))
    rep.hits.extend(certainty_hits(prose, cfg))
    rep.hits.extend(rhetoric_hits(prose, cfg))
    rep.hits.extend(coined_name_hits(prose, cfg))
    rep.hits.extend(shared_hits(tagged, cfg, job))
    rep.hits.extend(job_hits(tagged, cfg, job))

    # A job's off list names hit labels it does not read: Show drops the sentence
    # rule, Persuade drops it and the closing beat (the author, decision 10). em-dash
    # is the one entry that is not a label, because the cap lands in over_caps.
    off = set(cfg["jobs"][job]["off"])
    if "em-dash" not in off:
        em_dash_cap(prose, cfg, rep, per_k)
    rep.hits = [h for h in rep.hits if h.label not in off]

    if whole_rows:
        for h in rep.hits:
            h.line = lines[h.line // 2 - 1]
    rep.hits.sort(key=lambda h: (h.line, h.kind))
    return rep


def lint_text(text: str, cfg: dict, path: str = "<stdin>", job: str = "tell") -> Report:
    if IGNORE_MARKER in text[:4096]:
        return Report(path=path)
    return lint_tagged(walk(text), cfg, path, job, markdown=True)
