---
job: tell
---

# Applications: cover notes and screening answers

Write these last, from the finished resume and the saved job ad in `<out>/jobs/`. Every fact in
them must also be on the resume; read the two side by side before handing either over.

## Cover note

Short email body, under 150 words, in four parts:

1. The role and that the resume is attached.
2. Two proofs that match the job ad's top asks, each with a number from the resume.
3. Any tool the ad names that the person lacks, said plainly, with how fast they would be up
   on it (their call, a must-ask) and what they used for the same job. The resume never lists a tool the note says they
   lack, and the note never claims one the resume leaves out.
4. One next step: a call, or a small test task.

Give a subject line. Save it as `<out>/cover-<company-role>.txt`, plain text ready to paste into
an email client.

## Screening answers

Recruiters often send a list of questions before a call. Read each for what it tests, then
answer every one, numbered to match their list. Save the set as
`<out>/screening-<company-role>.txt`.

- **Experience questions** ("walk us through a time you..."): one real case in order. What was
  wrong, what the person did themselves, how they confirmed it was fixed, how it ended. Use the
  person's numbers from the resume or none.
- **How-do-you questions** (prioritization, missing information, checking AI output): describe
  the method in steps, then tie it to one real example. When the person works from frameworks
  (80/20, urgency against impact, need before want, testing before deciding, trade-offs said
  out loud, fixing the system behind a repeat problem), name the ones they use.
- **Categorize long answers** with a short bold heading per group (by role, or "What I've used"
  and "How I verify"), so a recruiter can skim it like the resume.
- **Personal facts are must-ask** (`references/grilling.md`): target rate, reason for leaving,
  location, availability, weekend coverage, language self-rating. Never guess these.
- **Gaps:** say "I have not used Mindbody" and name the closest tool used, never imply.

## Checks before handing over

- Every number appears on the resume; every claim passed the provenance checks.
- `never-on-resume.txt` terms are absent (`grep -i -f` against the file works for a quick pass).
- Run the AI-writing linter on the text if one is available (`check_resume.py` says where).
- Strip markdown from anything meant for an email or form: bold and bullets will show as
  asterisks. Keep numbered answers and blank lines between them.
- Tell the person which resume file to attach and its page count.
