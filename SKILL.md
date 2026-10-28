---
name: resume-builder
description: >
  Job applications end to end: a tailored resume, a cover note, recruiter screening answers, and
  take-home assessments (grammar tests, sample customer replies). Grills the person on facts only
  they know, mines their records, writes in the target field's own words, checks for claims they
  can't defend and employer leaks, and builds an ATS-safe PDF. Triggers: "build my resume",
  "update my resume", "tailor my resume to this job", "switch careers", "write a cover letter",
  "answer these recruiter questions", "help with this job assessment".
argument-hint: '<job ad (link, file or text); optionally resume, cover, screening, assessment, switch>'
version: 2.0.0
---

# Resume Builder

Turn a person's career into an application that gets the interview. The person decides what
only they can know; the skill decides the craft and says which calls it made.

## Every run starts here

1. Read `references/grilling.md` and run its intake: output folder (`<out>`), the job ad saved
   to `<out>/jobs/`, which jobs to do, mode, base material.
2. Read `<out>/profile.md` and `<out>/never-on-resume.txt`. A new person gets both from the
   templates in `references/` during intake.
3. Do the jobs asked for, in this order, each finishing before the next starts:

| Job | Where the steps live | Done when |
|---|---|---|
| Resume | this file, Steps 1 to 6 | `scripts/check_resume.py` passes and the person has seen the PDF |
| Switch mode | `references/career-switch.md`, then the resume steps | the transfer map and gap list are written |
| Cover note, screening answers | `references/applications.md` | every fact matches the finished resume |
| Assessment | `references/assessments.md` | every item answered, every policy assumption listed |

**Grill as needed.** Four decision classes always go to the person the moment they appear:
claims and numbers, titles and who built what, leaks, length and look. Everything else follows
the defaults below and is named in one line of the reply. Rules and question format:
`references/grilling.md`.

## Operating beliefs

1. A resume sells; it is about the employer's needs, not the candidate's wants.
2. Lead with results and business impact, not activities.
3. Quantify wherever honest. Estimate when you must, label it, never fabricate.
4. Prove traits with results ("detail-oriented" proves nothing). No buzzwords, no stuffing.
5. The strongest, most relevant material goes at the top.

## House defaults

| Decision | Default | Surface only if relevant |
|---|---|---|
| **ATS** | A search-and-rank database, not an auto-rejecter. Mirror the job ad's real terms, then write for the human. | About 92% of ATS don't auto-reject; the "75% rejected by bots" figure traces to a 2012 sales pitch. |
| **Length** | ~475–600 words, one page. Page counts are ceilings: the on-target material decides, and nothing is padded to reach one. | Up to two pages for 7+ years of on-target work, senior, federal or academic CVs. Depth mode, up to three, only when the person asks for detail. |
| **Summary** | 3–5 impact bullets, most relevant first. | A 1–2 line paragraph for senior narrative heft. |
| **Scan speed** | The top third decides whether the rest gets read. | Every bullet opens on a bold label and its result. |
| **Skills** | A section titled "Tools and how I use them", one `**Tool:** how I used it` line each, plus the same terms in bullets. | |
| **Interests, portfolio** | Only a specific conversation hook, or a linked proof artifact when the role rewards one. | |
| **No tricks** | No hidden text, stuffing, skill bars, photos or creative section names. | |

## Resume steps

### Step 1: Target lock

Pull the job ad's real keywords: hard skills, tools, certifications and named methods that repeat
or appear early. Keep only terms the person owns; note the ones they lack for the cover note.
Learn the field's own words from practitioners (`references/field-notes.md`, Language).

### Step 2: Raw material

Search every location in the profile's Records section before asking anything. Scratch: grill
one role at a time on what they did, what changed because of it, and the number. Revamp:
diagnose the old resume (activity bullets, no metrics, buzzwords, wrong length, missing terms)
and keep what works. Every number gets its source.

### Step 3: Build

Follow `references/field-notes.md` in its step order: context line per role, labeled result
bullets, Day to day last, progression, side projects only when this employer would care, the
tools section. Sections: contact (in the body, never a header or footer), summary, experience
reverse-chronological, optional side systems, tools, education. Bullet craft: result first, then
the number, then how (`references/frameworks.md`). Kill "responsible for" and any bullet a peer
with the same title could copy.

### Step 4: Tailor

Mirror the job ad's order of duties in the latest role. Every kept keyword appears in the
summary, the tools section and at least one bullet. Position profiles for repeat targets live
in the person's `profile.md` (`references/positioning-and-qa.md`).

### Step 5: Check

1. Provenance and leak review (`references/field-notes.md`). Each finding that needs the person
   goes into the next grilling round.
2. `python3 scripts/check_resume.py <out>/resume-<variant>.md` until it prints PASS.
3. Build: `python3 scripts/resume_pdf.py <out>/resume-<variant>.md` (the PDF is written to `<out>/pdf/`;
   `--theme` picks a look; `bash scripts/resume_theme_check.sh <file>` after any theme change).
4. `pdfinfo` for the page count, `pdftotext` to confirm anything just removed is gone, and
   `pdftoppm -r 70 -png` to look at every page, contact line included.

### Step 6: Hand over

Name the PDF to send, its page count, every inferred line, and every decision made without the
person. Offer the cover note and screening answers next (`references/applications.md`).

## Scripts

| Script | Does |
|---|---|
| `scripts/check_resume.py` | context lines, labels, Day to day, tools format, `never-on-resume.txt` terms, the AI-writing linter when present |
| `scripts/resume_pdf.py` | markdown to an ATS-safe PDF through pandoc and headless Chrome; set `CHROME` if Chrome is not found |
| `scripts/resume_theme_check.sh` | renders every theme and fails one whose text differs from the plain PDF |

Needs: Python 3, pandoc, Chrome or Chromium, poppler (`pdfinfo`, `pdftotext`, `pdftoppm`).

## References

- `references/grilling.md`: intake, the must-ask classes, question format, filling gaps on request.
- `references/field-notes.md`: role structure, language, provenance, leaks, length, styling.
- `references/frameworks.md`: bullet formulas, quantification levers, keyword extraction.
- `references/positioning-and-qa.md`: master and variants, the QA score loop.
- `references/career-switch.md`: switch mode, transfer map, gap list.
- `references/applications.md`: cover notes and recruiter screening answers.
- `references/assessments.md`: grammar tests and sample customer replies.
- `references/maintainer.md`: versions, the self-test, packaging. Read it before editing this skill.
