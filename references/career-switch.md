# Switch mode: a resume for a new field

Use this when the target role sits in a different field from the person's past job titles. The
base workflow still runs; switch mode adds four steps between raw material (Step 2) and the
section build (Step 3), and changes how the summary and experience are framed.

The hard part of a switch is evidence in the new field's language, so most of the work here
happens before any resume text gets written.

## S1 · Lock one target

- One role title in the new field, in the words job posts use ("Product Manager", not "something
  in product"). A second target waits until the first has a resume and 10 applications behind it.
- Get 3 to 5 real job posts for that title. The person pastes them or gives links. With only
  one, proceed and mark the keyword set provisional until more arrive.
- Build the **field keyword set**: terms that appear in 3 or more of the posts. With fewer
  posts, take the terms in each ad's requirements and mark the set provisional. A term in one post
  is that employer's quirk; a term in most of them is the field's vocabulary.
- If they know anyone in the field, suggest one short conversation to check the keyword set and
  the target title.

## S2 · Transfer map

A table in `<out>/switch-map.md`. One row per requirement that repeats across the posts:

| Requirement (field words) | Evidence from the master | Strength |
|---|---|---|
| "prioritize a roadmap" | ran the quarterly menu change for 4 stores, choosing 6 of 20 proposals by sales data | translated |
| "SQL" | none | gap |

Strength is one of three:
- **direct**: the old job did this thing under the same name
- **translated**: the old job did this thing under another name; the row gives the honest
  translation and the number that proves it
- **gap**: no evidence yet

Translation rules: keep the fact, change the vocabulary. "Handled shift handovers for 12 staff"
can become "coordinated handoffs across a 12-person team". It cannot become "led a cross-functional
team" unless they led it. Every translated row cites the master bullet it came from.

## S3 · Gap list

Every `gap` row gets the smallest piece of proof that would close it:

| Gap | Smallest proof | Done when | Date |
|---|---|---|---|
| SQL | answer 3 real questions about a public dataset, written up | a link someone else can open | 2 weeks out |

- Proof beats a certificate. A course counts only if it ends in something another person can see.
- Each proof is small enough to finish in 2 weeks of evenings. Bigger ones get cut down.
- At most 3 gaps open at once. The rest wait in the list.
- Each open gap becomes a task in the tracker, or a line in `<out>/switch-map.md` if there is
  no tracker.
- When a proof is done, add it to the master as a project with its link, and regenerate the
  variant.

**Watch for preparation drift.** A switch invites endless readiness work: another course, another
certificate, a redesigned portfolio. If the gap list keeps growing while no application goes out,
say so once, plainly. Applications and conversations with people in the field are the indicator.

## S4 · Position the variant

Generate `<out>/resume-switch-<target>.md` from the master with these rules on top of the
positioning layer:

- **Summary:** a one-line headline that names the target role in the field's own words and the
  strongest carried-over result, then the usual 3–5 bullets below it. "Operations lead moving into product management; chose and shipped 6 menu
  changes across 4 stores that raised average ticket 9%."
- **Projects above experience** when 2 or more bridge projects exist. Each with a link.
- **Experience bullets in field vocabulary**, from the transfer map's translated rows first.
- **Strip old-field jargon** that a reader in the new field would not know.
- **Titles stay true.** Never rename a past job title. A short function note in parentheses is
  fine: "Store Manager (operations and P&L)".
- **Dates stay visible.** No hiding a timeline to look less like a switcher.
- **Skills:** field keyword set terms the person can show, first; old-field tools only if the
  posts ask for them.

The gap list never appears on the resume. It is the work plan, not a section.

## Outputs

| File | Holds |
|---|---|
| `<out>/resume-master.md` | every verified role, bullet, metric and project, in the person's own field and the new one |
| `<out>/switch-map.md` | target title, the posts used, field keyword set, transfer map, gap list |
| `<out>/resume-switch-<target>.md` | the positioned variant, after the QA loop |

The QA loop scores findability against the field keyword set. Provenance stays a hard gate: a
translated bullet that no longer matches its master fact fails the resume.
