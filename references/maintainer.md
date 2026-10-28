---
job: tell
---

# Maintaining the skill

For whoever edits this skill. A normal resume run never reads this file.

## Versions

The version lives in `SKILL.md` front matter and each release has an entry in `CHANGELOG.md`.

- **Patch** (2.0.1): a clarification or a fixed contradiction between two files.
- **Minor** (2.1.0): a new rule in `field-notes.md`, a new house default, a new reference file.
- **Major** (3.0.0): a workflow step added, removed or reordered, or a changed folder layout.

## Self-test before every version bump

Rules are tested on agents that know only the skill. Run this after any change to `SKILL.md`
or a reference file, and bump the version only when it passes.

1. Copy `tests/fixture-person/` to a scratch folder; that copy is `<out>` for the run.
2. Start one fresh subagent per job ad in `tests/jobs/`. Each gets only: the path to this
   skill, the scratch `<out>`, the job ad, and "run non-interactively: write every grilling
   question with your recommended answer into a Questions list, and ask nothing". Pick the
   model per your routing rules; the October 2026 runs used Opus.
3. When the change touches `field-notes.md`, add one control run told not to open it, so the gap between the two runs shows what the notes add.
4. Grade every result with `python3 scripts/check_resume.py <out>/resume-*.md` (the checker
   skips a master resume, which carries source tags in place of labels).
5. A rule that fails in two or more runs is badly worded, not badly followed. Rewrite the rule,
   then run again.
6. Read each run's Questions list. Questions that two runs both raised point at a missing rule
   or a contradiction between files.
7. Record the runs and their check counts in the changelog entry.

The fixture person is fictional on purpose: the skill is public, and a real person's employers
or claims must never appear in `tests/`.

## Packaging and publishing

The repo keeps one copy of every script. `scripts/package.sh <dest>` builds a shareable copy:
the skill files, plus the AI-writing linter and its phrase file in `<dest>/lint/` when the source
repo has them. It then scans `<dest>` for every term in every `never-on-resume.txt` it is told
about (`--scan <dir>`, repeatable) and fails on a match.

Publish only from a passing package, with the version tag `vX.Y.Z` matching `SKILL.md`.
