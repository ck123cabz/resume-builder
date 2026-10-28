---
job: tell
---

# Grilling: when to stop and ask

The skill decides craft and asks the person about facts and taste. Every question goes out as a
grilling round: the AskUserQuestion tool, 2 to 4 options per question, your recommendation first
with "(Recommended)" on its label, and the facts they need inside the question. Up to 4
questions per call; send a second call in the same round when more are open. Without the tool,
ask the same questions as a numbered list, each with your pick.

Ask as needed, not on a fixed schedule: the moment a must-ask decision appears, batch it with
any other open ones into the next round, then keep building what does not depend on the answer.

## Intake, before anything is written

Ask whatever the person has not already said:

1. **Output folder.** Ask every run. Offer the person's existing folder first if one exists
   (a folder holding their `profile.md`), then `./resumes/<name>/` in the current directory.
   This folder is `<out>` everywhere else in the skill.
2. **The job.** A pasted job ad, link or file. Save it as `<out>/jobs/<company-role>.md` (just
   `<role>` when the ad names no company; the same rule names the cover and screening files) so
   later steps and the cover note read the same text.
3. **What to make.** Any of: resume, cover note, screening answers, assessment. Default: resume.
4. **Mode.** Scratch, revamp or switch (`references/career-switch.md`).
5. **Base material.** The resume to revamp, a LinkedIn PDF, or none.

When `<out>/profile.md` is missing, copy `references/profile.template.md` there, then add a
round for its Records section: where their old resumes, work journals, notes and repos live.
Copy `references/never-on-resume.template.txt` to `<out>/never-on-resume.txt` at the same time.

## Must-ask: stop the moment one appears

These four classes always go to the person. Never decide them silently.

| Class | Examples | Where the answer is kept |
|---|---|---|
| **Claims and numbers** | a metric not in the record; a claim they may not defend in an interview; a rate or percentage worded more strongly than its source; a promise about the future, such as how fast they will learn a tool | a cut claim → `[claim]` line in `never-on-resume.txt` |
| **Titles and who built what** | their title at each employer; built, ran, tuned or helped with a system | `profile.md` → Facts |
| **Leaks** | client names, a client niche, internal volumes, internal tool names, methods that work around a vendor's controls, rounded scale like "10,000+ mailboxes" | a cut term → `[leak]` line in `never-on-resume.txt` |
| **Length and look** | page count, first person or not, colors, theme, white space | `profile.md` → Preferences |

The person's own employers and titles always stay in role headers; a leak is what those employers
would not want public. Answers that will hold for the next resume go into the profile, so the
next run asks less.

## Everything else: decide and say so

Bullet order, wording, which result leads, labels and section order follow the house defaults
and `references/field-notes.md`. Name each unstated decision in one line of the reply and keep
going.

## After a draft

The next round carries every inferred line by role and phrase ("support agent day to day:
inferred from the standard ticket workflow"), and any claim the leak or provenance checks flagged.
Findings go into the round itself, never into a separate review file.

## When the person asks you to fill gaps

Some people say "fill in the blanks, make it believable", for a screening story or a day-to-day
line. Write it from the roles they really held, then list every invented detail by answer and
phrase in the same reply, and tell them an interviewer may ask about it. Invented numbers never
go in; a story keeps the person's real numbers or none.
