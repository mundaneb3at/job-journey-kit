# LETTERS PROTOCOL — cover letters for a named posting, portal or email (v1)

This lane produces one cover letter per posting: a one-page portal file, or (rule 12) a plain-email
body to a live posting with no separate document. A cold message with no posting is
`protocols/OUTREACH.md`'s, not this lane's. Gate: `tools/verify-letter.py` for every letter
(self-proving, exit 0 required). Findings land in a recheck note per target (gate step 5).

## Producer of record

| artifact | producer (exact command) | you get | mirror |
|---|---|---|---|
| any letter, target `<target>` | `python tools/make-letter.py <target> [--date "Month D, YYYY"] [--out DIR]`, reads `letters/<target>.md` | `<Name>-Cover-Letter-<Stem>.docx` | `.md` mirror alongside it |

Edit only the content file: `letters/<target>.md`. Never hand-edit a letter's generated file — the
next regen erases it, the same way a hand-edit on a résumé once fell outside its own gates. Close
your word processor before a regen; a permission error on write means it still has the file open.

## Rules (each with its source)

| # | rule | source |
|---|---|---|
| 1 | **One page**, measured by your word processor's own page-count call, not eyeballed. A target word count is not a measurement — set a drafting budget for your layout and gate against the rendered page count instead. | a letter was called "ready" while actually running two pages against a one-page target |
| 2 | **Every number → an evidence-ledger row before it enters prose.** A claim-checking pass must PASS. It can't see dates, spelled-out numbers, or a small number that happens to equal a ledger row id — list those by hand in your own audit notes. | an unbacked number in a letter is the same failure as one on a résumé |
| 3 | **Verb rule.** Never first-person build/ship/write/code/verify (unqualified) for AI-assisted work; never "explain every mechanism" — name what you actually did instead. | RESUME.md rule 7, same failure mode in letter prose |
| 4 | **Posting quotes are verbatim** against a saved posting file, never memory or paraphrase. Every body paragraph answers a named posting line. | a paraphrased quote can silently drift from what the posting actually said |
| 5 | **Required lines:** your availability window and start-by date, stated plainly; your display name consistent in header and signature (filenames can differ from the display form). | a letter that doesn't answer "when can you start" gets read as a mismatch |
| 6 | **Letter date = the day it is submitted.** The gate checks against today by default, so a letter left on an old date fails on submit day — rerun the producer on submit day (defaults to today; pass an explicit date for a planned day). | a stale date on a submitted letter reads as a template nobody finished |
| 7 | **No jargon from the voice pass:** swap any term from your own tooling or process for its plain-language equivalent. | jargon meant for a technical peer reads as noise to an employer-facing reader |
| 8 | **Don't restate résumé page 1.** No long run of words shared with the résumé's headline page, except a short list of phrases you've deliberately locked in place. The résumé lists; the letter tells the story behind one or two items and ties it to the posting. | a letter that just repeats the résumé wastes the reader's second look |
| 9 | **Honest gaps stated once**, plainly, in one place — no gap hidden, none invented. | a hidden gap discovered later costs more trust than a stated one ever would |
| 10 | **Defensible in a 10-minute call.** Every sentence is one you could walk through without notes. | GATES.md G5, applied to the letter itself |
| 11 | The closing ask for a short call belongs to a cold email or proposal (`protocols/OUTREACH.md`), **not** a portal letter. | a call-to-action in a formal application reads as out of place |
| 12 | **A letter emailed to a live posting** follows rules 1–11 minus rule 1's page count and the mirror file; the email body **is** the letter; every link in the body is a plain `https://` URL, never a shortened or wrapped one. | a link-shortener or a mail client's tracking-wrapped link has gone out unnoticed before |

## Gate order

1. New number? Add its ledger row first (rule 2).
2. Edit the content file (`letters/<target>.md`) → close your word processor → run the producer.
3. Run your claim-checking pass, test mode then real mode → PASS.
4. `python tools/verify-letter.py [--date "Month D, YYYY"] [--only <target>]` → exit 0. Self-proving: the `before:` file (an earlier draft) must fail, and every probe an old copy can't trip fires on a planted mutation of the new text.
5. Blind recheck: a fresh AI context with no memory of writing it → fix or rebut every row; rerun step 4.
6. Read the generated file (or, rule 12, the email body) once as the recruiter would (60 seconds) and click Submit / Send yourself. No assistant submits or sends.

## Submitting (a portal form walk, if your platform needs one)

Fill plain fields directly; attach files through the actual file-input control, not a button that
opens a native picker your assistant can't see; custom dropdowns usually need a click, then
type-to-filter, then a click on the rendered option. Only you answer any field carrying a standing
rule of your own (work-authorization status, for example) — leave it blank and name it, never fill
it from a guess. Before you click Submit, re-open the live posting if more than a few minutes
passed since you last checked it. A filled form is not a submission.

## Adding the next one

Content-file header (`letters/<target>.md`), verbatim shape:
```
# <Title line, free>
stem: <Name>-Cover-Letter-<Stem>
posting: <key>                      # letters/postings/<key>.paste.md or .api.txt
subject: <subject line, verbatim>
required: <anchor> | <anchor> | <anchor>
before: <path to an earlier draft, or none>

Dear …,

<paragraph>
```
1. Save the posting to `letters/postings/<key>.api.txt` (or your own paste as `.paste.md`).
2. Write `letters/<target>.md` with the header above + body paragraphs (blank-line separated).
3. Snapshot any earlier draft as `letters/before/<Stem>.md` and name that path in the `before:`
   header, so the self-proving control has something to fire on.
4. `python tools/make-letter.py <target>` → generated file + mirror.
5. Run the gate order (steps 3–6 above).

## Origins

Distilled from one owner's lane, 2026-09; incidents generalised.
