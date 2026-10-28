---
job: tell
---

# resume-builder changelog

The version lives in `SKILL.md` front matter. Bump the minor number when a session adds rules to `references/field-notes.md` or changes a house default, and the major number when the workflow steps change.

## 2.0.0, 28 October 2026

Rebuilt so anyone can run it, after a grilling round on 28 October. Merges an October 15 fork
that had scrubbed references, a career-switch mode, PDF themes and an ATS-safe date layout.

- `SKILL.md` is a router for four jobs: resume, cover note, screening answers, assessments.
- New `references/grilling.md`: intake (output folder asked every run, job ad saved to
  `<out>/jobs/`), and four classes that always go to the person: claims and numbers, titles and
  who built what, leaks, length and look.
- New `references/applications.md` and `references/assessments.md`.
- Each person keeps `profile.md` and `never-on-resume.txt` in their own folder; templates ship in
  `references/`. The checker reads the list beside the resume and finds the linter wherever it is.
- The PDF builder, CSS and seven themes live in `scripts/`; PDFs go to `<out>/pdf/`; Chrome is
  found on macOS and Linux or through `CHROME`.
- `scripts/package.sh` builds the shareable copy with the linter and fails on any leak term.
- New `references/maintainer.md` and `tests/` (a fictional person, two job ads) for the self-test.
- Self-test, 3 blind Opus runs on the package: operations PASS, talent sourcer (switch mode,
  cover note) PASS, control without field notes PASS but unsure on leaks and context lines.
  Eight rule fixes followed: page counts are ceilings, own employers stay in headers, the tools
  bullet format, switch summary headline, where cover and screening files are saved, master
  provenance tags, one job ad enough to start a switch, a stale CSS comment.

## 1.2.1, 4 October 2026

Clarifications from the verification run (the operations resume rebuilt on 1.2.0 passed every check).

- Length: `SKILL.md` and the field notes now agree, two pages for 7+ years.
- First person: no "I" in labels or results; steps may use it when the person wants their own voice.
- The tools section is the skills section, titled "Tools and how I use them".
- Internal figures: a dated result the person produced may stay; never add a new one without asking.
- Titles come from the person's record, never from the target job.

## 1.2.0, 4 October 2026

From an experiment the same day: three fresh agents built resumes for an operations role (with and without the field notes) and a recruiting role, all graded by the same checker.

- Added `scripts/check_resume.py` and `references/never-on-resume.txt`; Step 5 now runs the checker first.
- Field notes made role-agnostic, with an 11-step order. New rules: describe employers at category level, Day to day on every role (inferred when the record is thin), the exact tools format with an example, no fresh internal volumes, two-sided businesses, a length section, and research fallback when no corpus exists.

## 1.1.0, 4 October 2026

From a two-day session tailoring an outbound agency resume, 3 and 4 October.

- Added `references/field-notes.md`: the three-part role structure (context line, labeled results, Day to day last), voice rules for field vocabulary, provenance sources and checks, leak review, per-resume styling, and build checks.
- Length default now names a depth mode of up to 3 pages, used when the person asks for detail.
- Architecture diagram replaced by a one-line step list to bring `SKILL.md` under 150 lines.
- `scripts/resume_pdf.py` deletes the old PDF before rendering, so a rebuild can no longer keep stale text.

## 1.0.0, 27 May 2026

First version, synthesized from Jeff Su, Madeline Mann, Andrew LaCivita and Austin Belcak plus recruiter-survey research.
