---
job: tell
---

# Field notes

Rules learned from real application sessions, written to work for any role. Each rule says what
to do and why. When a session teaches something new, add it here and bump the version in
`CHANGELOG.md`.

## The steps, in order

Run these on every tailored resume. Each has a section below.

1. Read the job ad for its keywords, its order of duties, and the tools it names.
2. Learn the field's language from people who work in it.
3. Mine the person's own records before asking them anything.
4. For each role, write what the business sold and where the person sat in it.
5. Write labeled result bullets, then one Day to day bullet, per role.
6. Show how each role led to the next.
7. Add side projects and skills only where this employer would care.
8. Build the tools section as "tool: how I used it".
9. Run the provenance and leak checks, then `<skill>/scripts/check_resume.py`.
10. Style, render, and check the pages.
11. Write the cover note last, from the finished CV.

## Language

- **Use the field's own words for bullet labels.** Find them in the job ad and in what
  practitioners publish. For recruiting that would be time-to-fill, pipeline, shortlist; for
  support, queue, CSAT, first response. A label written as a story ("Tested the setup until it
  held") reads as an outsider.
- **Learn the language from practitioners, not guesses.** If the profile names a corpus or notes
  for the field, read them for terms and norms; if not, research two or three practitioners'
  posts or a benchmark report, and cite what you used.
- **First person:** labels and results carry no "I". The steps and the context line may use it
  when the person wants the resume to sound like them speaking; otherwise drop it everywhere.
- **Mirror the job ad's order of duties** in the most recent role's bullets.
- **Write a trade term out in plain words once** when a recruiter may not know it.
- Run `scripts/ai_slop_lint.py` on the markdown after every round.

## Records to mine

Look before asking. The person's `profile.md` lists where their records live (old resumes,
work journals, notes, project folders, repos). Search every location there before asking a
question; use `git log --format=%an` in any repo they worked in to see who built what. Hard
numbers often sit in an old work journal; quote the source when you use one. A location not in
the profile gets added to it once the person names it.

## Role structure

Every role gets the same three parts.

1. **Context line**, in italics: what the business sold and how the role fed it. One sentence
   of how the money moved makes every bullet under it easier to judge.
2. **Result bullets**, each opening on a short bold label, then the result, then the steps that
   produced it. Recruiters skim the top left of each section first (eye-tracking studies put the
   first scan under ten seconds), so the label and result carry the scan and the steps serve
   whoever reads on.
3. **Day to day**, the last bullet of every role, including roles shortened to one or two
   bullets: a normal shift's steps in order, separated by semicolons. When the record has no
   shift detail, write the standard workflow for that title and mark the line as inferred.

**Describe the business at category level** for any employer the leak review covers: "an
outbound lead generation agency", not its niche or its clients. Read `never-on-resume.txt`
before writing a context line. A past incident: test runs leaked an employer's niche through
the context line. **When the business is two-sided**, say who pays and what they get.

**Check the business model itself.** A past incident: a draft had an employer's buyers and
prospects reversed; the employer's own docs corrected it.

**Do not compress steps away.** A version with one bare action per bullet read worse. Keep the
steps; cut the commentary and the selling words.

## Progression

Show how each role led to the next with facts: a promotion and its date, a system that earned
the bigger role, a move from delivering a service to selling it. Put it in the context line or
the last result bullet, never as a separate story.

## Side projects and skills

A section for side systems or learning lists only what this employer would care about. Ask of
each item: would the hiring manager use this skill in the job?

## Tools

- The section is titled "Tools and how I use them", and every line is a bullet,
  `- **Tool:** how I used it`. Group them under plain bold lines (`**Lead sourcing**` on its own
  line), not `###` headings. Example: `- **Spreadsheet, CRM:** tracked every candidate from first
  call to offer.` A comma-separated skills list does not count.
- List only tools the person confirms. When the job ad names a tool they lack, say so in the
  cover note and keep the CV and the note in agreement.

## Provenance checks

- **Mark every inferred line** in the reply, by role and phrase.
- **Tag sources in a master resume** at the start of each bullet: 🟢 confirmed, 🟡 an estimate
  the person approved, 🔴 unverified. A 🔴 line never reaches a variant; strip the tags there.
- **Cut what they cannot defend in an interview.** Ask about any number whose source is not in
  the record.
- **Use the title from the person's record, never the target job's title.**
- **Check who built what**, and use the person's chosen wording; never upgrade or downgrade a
  claim silently.
- **Check tool release dates against role dates.** A tool released last year cannot appear in a
  role that ended three years ago.
- **Check the timeline for gaps** after cutting a role. Keep the role as one line so no months
  sit empty.
- **Do not pull new internal volumes from live systems.** A dated result the person produced
  and already shows may stay; the leak review still asks about it once. Never add a new
  internal figure without asking.
- **Check numbers are defensible as stated:** "more than half" for 53 to 63%, not "about half".

## Leak review

The person's own employers stay in role headers. Remove anything that exposes an employer: client names and niche, exact internal configuration,
internal volumes the person did not produce, methods that work around a vendor's controls,
internal tool names, internal conversion rates. Describe the method and leave out the numbers.
Rounded scale that proves the person's level is their call, so ask. Every term cut goes into
`never-on-resume.txt`.

## Length

Ask how long. Without an answer, use the house default in `SKILL.md`: one page for most people,
up to two for 7+ years of on-target work. Page counts are ceilings; the on-target material
decides, so a switch resume or a thin record stays on one page. Depth mode, up to three pages,
only when the person asks for detail.

## Styling and build

- Looks come from `--theme` (`<skill>/scripts/resume-themes/*.css`). A theme may change fonts, color
  and spacing only. Check it with `pdftotext`: the text must match the unthemed PDF word for word.
- Run `bash <skill>/scripts/resume_theme_check.sh <file>` after any theme change. Two traps it catches:
  letter-spacing above 0.06em on headings made `pdftotext` read "SUMMARY" as "S U M M A RY",
  and an OpenType-CFF font (Inter) embedded as Type 3, which older ATS parsers misread.
- Never right-align dates in a separate column. A past incident: a flex date column made
  `pdftotext` read one role's dates at the end of the page.
- Per-resume spacing and color go in a `<style>` block at the end of the markdown;
  `<skill>/scripts/resume-pdf.css` stays shared.
- Two accents at most, and every colored element also differs in weight or position so the page
  reads in grey.
- For white space, raise body size and line height first; let long roles break between bullets (`.role + p + ul { break-inside: auto; }`).
- Build with `python3 <skill>/scripts/resume_pdf.py <file>`, then check `pdfinfo`
  for pages, `pdftotext` for anything just removed, and `pdftoppm` renders by eye, contact line
  included.
- When content spills onto a new page, cut a repeated line before cutting a fact.
- Finish with `python3 <skill>/scripts/check_resume.py <file>`. It checks context
  lines, labels, Day to day, the tools format, the terms in `never-on-resume.txt`, and the
  linter.
