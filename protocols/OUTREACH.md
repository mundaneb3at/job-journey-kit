# OUTREACH PROTOCOL — cold messages to an employer with no live posting (v1)

This lane produces cold outreach to an employer with **no live posting** — proposal emails,
LinkedIn messages, follow-ups. Not a portal cover letter (`protocols/LETTERS.md`); an emailed
application to a live posting is a letter by email (LETTERS rule 12). Gate:
`python tools/verify-outreach.py [--only <target>]` over `outreach/*.md`, self-proving against a
negative-control set of past sends. Findings land in that target's `status:` field and
`OPPORTUNITY-TRACKER.md` § Activity log — both flip to `sent` only on your word.

## Producer of record

| artifact | producer (exact command) | you get | mirror |
|---|---|---|---|
| `outreach/<target>.md` (header `to:` / `subject:` / `source:` / `status:` + body) | you paste the body yourself; an assistant may write a mail **draft**, never send it | the message + résumé attachment | none — the `.md` file is the only record |
| `outreach/_TEMPLATE.md` | the starting shape; leading underscore = not gated | n/a | n/a |

`status:` flips `draft` → `sent` only on your word, confirmed however you check your own sent mail.
No assistant flips it on its own read of a draft.

## Rules (each with its source)

| # | rule | source |
|---|---|---|
| 1 | State pay and term plainly if you know them; if you don't, that's a question to ask before sending, not to omit. | an unstated term reads as an unfinished message |
| 2 | Closing ask for a short call, on every cold message. | a message with no ask has no next step for the reader to take |
| 3 | One verified, employer-specific quote from a page opened live that day; its URL goes in `source:`. | a generic message reads as a mail-merge, not outreach |
| 4 | Verb rule: never first-person build/ship/verify (unqualified) for AI-assisted work — name what you actually directed, reviewed, or tested. | RESUME.md rule 7, LETTERS.md rule 3 |
| 5 | Honest-positioning line about how you actually use AI in your own work, stated once, in your own words. | an unstated AI-assistance gap discovered later costs more trust than a stated one |
| 6 | No jargon from your own tooling — plain synonyms throughout. | a reader outside your tooling reads jargon as noise |
| 7 | Your display name consistent in body and signature. | RESUME.md rule 9 |
| 8 | Plain `https://` links only, never a redirect-wrapper link. | a link-shortener or tracking-wrapped link has gone out unnoticed before |
| 9 | Zero spelling errors. | a misspelling in a cold message has gone out unnoticed before |
| 10 | Every number → an evidence-ledger row before it enters prose. | RESUME.md rule 6, LETTERS.md rule 2 |
| 11 | One route per target; no unpaid trial, no take-home, no free baseline; `sent` flips only on your word. | a second, unplanned route to the same employer creates conflicting messages |

## Gate order

1. Copy `outreach/_TEMPLATE.md` → `outreach/<target>.md`; fill `to:` / `subject:` / `source:` / `status: draft`.
2. Open the employer's page live today; quote one verified, specific line (rule 3) into the body; put its URL in `source:`.
3. `python tools/verify-outreach.py --only <target>` → exit 0. Probes run in order: banned, jargon, verb, required, name, links, spelling, numbers — the first failing probe names the verdict.
4. Self-proving, same run: a negative-control set of past sends must fail as a set; planted mutations must trip every probe the negative-control set alone doesn't reach.
5. Optional: write a mail **draft** with plain `https://` links, never send it.
6. You paste the body (or open the draft), attach your current résumé, and click Send. No assistant sends.
7. Activity-log row only on your word ("sent X"); confirm however you check your own sent mail; `outreach/<target>.md` `status:` flips to `sent`.

## Adding the next one

Copy `outreach/_TEMPLATE.md` → `outreach/<target>.md` with header `to: / subject: / source: /
status: draft` and a body → open the target's page live and quote one verified line into `source:`
(step 2) → `python tools/verify-outreach.py --only <target>` → exit 0 (step 3, controls must hold)
→ gate order steps 5–7.

## Origins

Distilled from one owner's lane, 2026-09; incidents generalised.
