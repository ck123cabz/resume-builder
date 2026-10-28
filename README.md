---
job: tell
---

# resume-builder

A Claude Code skill for job applications: a tailored resume, a cover note, answers to a
recruiter's screening questions, and take-home tests. It asks you only what you know (your
titles, your numbers, what you can defend in an interview), mines your own notes for the rest,
writes in your target field's words, and builds an ATS-safe PDF.

## Install

```bash
git clone https://github.com/ck123cabz/resume-builder ~/.claude/skills/resume-builder
```

Then, in Claude Code, say "build my resume for this job" and paste the job ad.

Needs Python 3, pandoc, Chrome or Chromium, and poppler:

```bash
brew install pandoc poppler          # macOS
sudo apt install pandoc poppler-utils chromium   # Debian or Ubuntu
```

Set `CHROME=/path/to/chrome` if the PDF step cannot find your browser.

## What a run looks like

1. **Intake.** Where to save your files, the job ad, which pieces you want, and where your old
   resumes and notes live. Your answers go into `profile.md` in your folder, so the next run
   asks less.
2. **Mining.** It reads every source you named before asking anything else.
3. **Questions as they come up.** Claims and numbers, titles and who built what, anything that
   could expose an employer, and length and look always come to you as multiple-choice
   questions with a recommended answer.
4. **Build and check.** `scripts/check_resume.py` checks the structure, your never-on-resume
   list and the writing. `scripts/resume_pdf.py` makes the PDF; you see every page.

Your folder holds `profile.md`, `never-on-resume.txt`, the job ads, each resume and its PDF.
Nothing in it is shared.

## Layout

- `SKILL.md`: the steps Claude follows.
- `references/`: the rules, one file per job (applications, assessments, career switch) and the
  shared field notes.
- `scripts/`: the checker, the PDF builder, themes, and the packager.
- `lint/`: the AI-writing linter and its phrase list.
- `tests/`: a fictional person and two job ads used to test the skill after every change.

Version history: `CHANGELOG.md`. Editing the skill: `references/maintainer.md`.
