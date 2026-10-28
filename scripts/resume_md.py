"""Resume markdown preprocessing for pandoc: role header rows and list spacing."""
import re

# **Title — Company · Remote · Feb 2026 – Present**  ->  title left, dates right.
# The date range is always the final "·" segment; anything without one is left alone.
ROLE = re.compile(r"^\*\*(.+)\*\*$")
DATEISH = re.compile(r"\b(19|20)\d{2}\b|\bPresent\b")


def split_role(line):
    """Return (title, dates) for a role header line, or None if it isn't one."""
    m = ROLE.match(line.strip())
    if not m:
        return None
    body = m.group(1)
    if "·" not in body:
        return None
    head, _, tail = body.rpartition("·")
    if not DATEISH.search(tail):
        return None
    return head.strip(" ·"), tail.strip()


def preprocess(md):
    """Turn role headers into a flex row, and open a blank line before any list.

    pandoc's markdown treats a list that directly follows a paragraph line as a
    lazy continuation of that paragraph, so a role's italic context line would
    otherwise swallow every bullet under it into one block of prose.
    """
    out = []
    in_kv = False
    for line in md.splitlines():
        role = split_role(line)
        if role:
            head, dates = role
            title, _, org = head.partition(" — " if " — " in head else ", ")
            # Dates stay inline after the org: a right-aligned flex column let
            # pdftotext (and so an ATS) read a role's dates at the end of the page.
            out.append(
                f'<div class="role"><span class="role-title">{title}</span>'
                f'<span class="role-org">, {org}</span>'
                f' <span class="role-sep">·</span> <span class="role-dates">{dates}</span></div>')
            out.append("")  # closes the raw-HTML block
            continue
        stripped = line.lstrip()
        prev = out[-1].lstrip() if out else ""
        # A list, or a "**Label:** ..." skills line, needs a blank line above it
        # or pandoc folds it into the paragraph before it.
        is_kv = stripped.startswith("**") and ":**" in stripped
        opens_block = stripped.startswith("- ") or is_kv
        if opens_block and prev.strip() and not prev.startswith("- "):
            out.append("")
        # Fenced div so the skills block can be styled without a selector that
        # reaches every other paragraph on the page.
        if is_kv and not in_kv:
            out.append("::: kv"); out.append(""); in_kv = True
        elif in_kv and stripped and not is_kv:
            out.append(":::"); out.append(""); in_kv = False
        out.append(line)
    if in_kv:
        out.append(":::")
    return "\n".join(out)
