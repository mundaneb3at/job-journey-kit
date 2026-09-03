# <Season> job search — project home

Routed by **what you want to do**, not by folder. Last substantive update: **<date>**.

## "I want to apply to something right now"
→ `OPPORTUNITY-TRACKER.md` Tier A. `ready` means the package exists and only your click is missing.
**If anything is `ready`, do that before reading further.**

## "What's actually open? / is this posting still live?"
→ `node tools/ats-sweep.mjs --selfcheck` (must print `SELFCHECK OK`), then
`node tools/ats-sweep.mjs --slugs slugs.json` → `sweep-<date>.md`.
→ `VERIFY-LEDGER-<date>.md` — every row's liveness verdict with the check time.
**Do not trust a job URL that merely loads.** Board pages return 200 for closed postings.

## "Is this claim on my resume actually true?"
→ `CLAIMS-EVIDENCE-LEDGER.md` — nothing goes in an application that isn't backed here.
→ `AMMO-LEDGER.md` — the wider evidence bank the ledger draws from.
→ `resume.md` is the source of truth; generated docx/pdf are outputs, never edited by hand.

## "I have an interview / what are my gaps?"
→ `<interview-prep file>` — likely questions with answers tied to real artifacts.

## "What happened, and what did we learn?"
→ `EXECUTION-LOG.md` — one dated entry per session.

## Standing rules
1. An eligibility line is pass/fail, quoted verbatim — never a fit percentage.
2. HTTP 200 is not evidence a job is open. Board API, or a rendered apply control, or `UNVERIFIED`.
3. Resolve aggregators (Indeed, LinkedIn copies) to the employer's own posting — aggregator copies
   carry wrong deadlines.
4. Never claim a skill the evidence ledger doesn't back. Stating a gap plainly is a strategy.
5. Nothing is submitted by anyone but you.
6. Every session ends with a dated Activity-log row in the tracker.
