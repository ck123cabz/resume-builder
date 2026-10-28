"""Check a tailored resume against the field-notes rules a machine can verify.

    python3 <skill>/scripts/check_resume.py <person-dir>/resume-<variant>.md

Exit 0 when every check passes, 1 otherwise. Rules: references/field-notes.md.
Terms that must never appear: never-on-resume.txt in the person's folder, beside
the resume. The AI-writing linter runs when found: the packaged copy in <skill>/lint/,
else scripts/ai_slop_lint.py in a repo above the resume; otherwise the check says so.
"""
import pathlib
import re
import subprocess
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
ROLE = re.compile(r"^\*\*[^*\n]+·[^*\n]*\b(19|20)\d\d\b[^*\n]*\*\*$", re.M)
LABEL = re.compile(r"^\*\*[^*]{2,80}:\*\*")


def never_terms(person_dir):
    out = []
    f = person_dir / "never-on-resume.txt"
    for line in (f.read_text().splitlines() if f.exists() else []):
        m = re.match(r"\[(leak|claim)\]\s+(.+)", line.strip())
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def roles(body):
    heads = list(ROLE.finditer(body))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        block = body[h.end():end].split("\n## ")[0]
        yield h.group(0).strip("*").split(" · ")[0], block


def find_linter(src):
    packaged = SKILL / "lint" / "scripts" / "ai_slop_lint.py"
    if packaged.exists():
        return packaged
    for d in list(src.resolve().parents) + [SKILL.parent.parent]:
        if (d / "scripts" / "ai_slop_lint.py").exists():
            return d / "scripts" / "ai_slop_lint.py"
    return None


def check(path):
    src = pathlib.Path(path)
    if src.stem.startswith("resume-master"):
        print(f"{path}: skipped, a master holds source tags and is never sent; check its variants")
        return True
    body = src.read_text().split("<style>")[0]
    fails = []
    rs = list(roles(body))
    for name, block in rs:
        first = block.strip().splitlines()[0] if block.strip() else ""
        bullets = re.findall(r"^- (.+)$", block, re.M)
        if not (first.startswith("*") and not first.startswith("**")):
            fails.append(f"{name}: no italic context line under the header")
        unlabeled = [b for b in bullets if not LABEL.match(b)]
        if unlabeled:
            fails.append(f"{name}: {len(unlabeled)} bullet(s) without a bold label")
        if not bullets or not bullets[-1].lower().startswith("**day to day"):
            fails.append(f"{name}: last bullet is not Day to day")
    tools = re.search(r"\n## [^\n]*(Tool|Skill)[^\n]*\n(.*?)(?=\n## |\Z)", body, re.S)
    lines = re.findall(r"^- (.+)$", tools.group(2), re.M) if tools else []
    if not lines or any(not LABEL.match(t) for t in lines):
        fails.append("tools: every line must read '**Tool:** how I used it'")
    low = body.lower()
    if not (src.parent / "never-on-resume.txt").exists():
        fails.append(f"no never-on-resume.txt in {src.parent}; create it, even if empty")
    for kind, term in never_terms(src.parent):
        if re.search(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", low):
            fails.append(f"{kind}: '{term}' appears")
    linter = find_linter(src)
    lint_note = "lint skipped: no linter found" if not linter else "lint run"
    if linter:
        lint = subprocess.run([sys.executable, str(linter), str(src.resolve())], capture_output=True, text=True)
        if lint.returncode == 2:
            fails.append(f"lint: banned phrase present (run {linter})")
    pdf = next((c for c in (src.parent / "pdf" / (src.stem + ".pdf"), src.with_suffix(".pdf")) if c.exists()), src.with_suffix(".pdf"))
    pages = "no PDF"
    if pdf.exists():
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        pages = re.search(r"Pages:\s+(\d+)", info).group(1) + " pages"
    print(f"{path}: {len(rs)} roles, {pages}, {lint_note}")
    for f in fails:
        print(f"  FAIL {f}")
    print("  PASS" if not fails else f"  {len(fails)} failing check(s)")
    return not fails


if __name__ == "__main__":
    ok = all([check(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
