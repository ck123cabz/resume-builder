# Resume Builder — Positioning Layer & QA Loop

Two capabilities that sit on top of the base `resume-builder` workflow. The **positioning layer** turns one master resume into any number of angled variants. The **QA loop** scores a draft against the methodology and iterates until it clears a confidence threshold.

---

## 1. Positioning layer

**Principle:** content and positioning are separate concerns. Maintain ONE master resume that holds every verified role, bullet, metric, skill, and project. A *position* is a selection + reordering + re-emphasis of that master, plus a tuned summary and keyword set. Never invent content per position — only choose and frame what already exists in the master.

### Artifacts
- **`<out>/resume-master.md`** — the source of truth. Everything, provenance-tagged. Never trimmed for length; this is the well you draw from.
- **`<out>/resume-{position}.md`** — a generated variant (length-disciplined, ATS-clean).

### Position profiles
Each profile defines four levers: the summary angle, which experience to foreground, which to
compress, and the keyword bias. The kit ships two; add one per target role the person pursues, in their profile.md.

| Profile | Foregrounds | Compresses | Summary angle |
|---|---|---|---|
| `hybrid` (default) | the person's two or three strongest threads, balanced | early or off-target roles | one line naming the combination |
| `{jd-tailored}` | whatever the JD's real keywords demand (per `frameworks.md`, keyword extraction) | everything off-target | mirror the JD's framing |
| `<your-profile>` | the roles and results that prove this angle | what this employer will not use | one line in the target field's own words |

A JD-tailored variant always beats a generic profile when a real posting exists.

### Generating a variant
1. Start from the master.
2. Apply the profile's foreground/compress rules; reorder so the most on-target role/bullets sit highest.
3. Swap the summary to the profile's angle; bias the skills order and keyword phrasing.
4. Enforce length (1–2 pages).
5. Run it through the QA loop below before it's "done."

---

## 2. QA loop (iterative scoring → revision → re-score)

A ralph-style loop: score the draft, revise the weakest dimensions, re-score, repeat until the confidence score clears the threshold or max iterations hit. Stop early if a dimension can't improve without a fact the human must supply (escalate instead of inventing).

### Scorecard (0–100 weighted confidence)

| # | Dimension | Weight | Passing bar | What it checks |
|---|---|---|---|---|
| 1 | **Impact & evidence** | 25 | ≥85 | Every experience bullet leads with a result/outcome, not a duty; quantified wherever honest. No "responsible for". |
| 2 | **Provenance integrity** | 20 | **100 (hard gate)** | Every claim traces to the confirmed record (🟢) or an approved 🟡. Zero 🔴 unverified/fabricated claims. This gate cannot be traded off. |
| 3 | **Findability / keywords** | 20 | ≥80 | Relevant role keywords present and natural. With a JD: term-match ≥ target (aim 75–80%). |
| 4 | **Concision & length** | 15 | ≥85 | Within 1–2 pages; bullets ≤2 lines; no redundant phrasing or filler. |
| 5 | **Clarity & voice** | 10 | ≥85 | Strong action verbs; no buzzwords/cliches/first-person "I"; consistent tense; passes the project AI-writing filter. |
| 6 | **Structure & ATS-parseability** | 10 | ≥90 | Reverse-chron, standard section headers, contact in body, single-column, no tables/graphics. |

**Confidence score** = weighted average. **Ideal threshold = 90**, AND dimension 2 must be exactly 100 (a single unverified claim fails the whole resume regardless of the average).

### Loop protocol
1. **Score** the draft across all six dimensions; write a scorecard (dimension, score, the specific gaps found).
2. **Check the gate:** if provenance < 100, list each 🔴 claim and either remove it or flag it for human confirmation — do not proceed past this with unverified claims.
3. **Revise** the lowest-scoring dimensions (one pass, targeted edits — don't rewrite what already passes).
4. **Re-score.** Record the delta.
5. **Repeat** until confidence ≥ 90 with provenance = 100, or until 4 iterations, or until the only remaining gaps need a human fact (then escalate with a specific question).
6. **Output:** the final resume + the final scorecard (so the human sees what was checked and why it passed).

### Notes
- The loop revises *wording and selection*, never facts. If a higher score would require a claim that isn't in the master/confirmed record, that's an escalation, not an edit.
- For a positioned variant, dimension 3 (findability) and the summary angle are scored against *that position's* target, not generically.
- Keep each iteration's scorecard so the progression is auditable (the human-review feedback loop).
