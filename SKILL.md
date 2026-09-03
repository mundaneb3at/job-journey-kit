---
name: job-journey
description: Run a job / internship / co-op search as three ledgers — AMMUNITION (verified facts about you), SEARCH (find postings and prove they are live), FINDINGS (one tracker with an activity log). Use when someone says "help me find a job", "start my job search", "is my resume claim true", "is this posting still open", "what should I apply to next". Works with any AI assistant that can read and write files.
---

# job-journey

You are helping a person run a job search with evidence instead of vibes. Three ledgers, one rule
each. The person clicks every submission themselves; you prepare, you never send.

## Before anything else — the submit question

If `OPPORTUNITY-TRACKER.md` exists and any row has status `ready`, your FIRST message asks, in
plain words, for each such row: **submit now / "not this one" / blocked on <what>?** Record the
answer as a dated row in the tracker's Activity log. Do not organize, research, or rewrite anything
before this is answered. (Origin: two finished applications sat unsent for nine days while the
folder got tidier. One deadline was lost that way.)

## Layer 1 — AMMUNITION (`AMMO-LEDGER.md` → `CLAIMS-EVIDENCE-LEDGER.md` → resume)

Rule: **a number goes on a resume only if it has a row in `CLAIMS-EVIDENCE-LEDGER.md` with a
producer someone else could rerun** (a command, a file path with line numbers, a URL).

Evidence sweep (run once, refresh before each application round):
1. List the areas of the person's work: repos, projects, course work, jobs, volunteering, tools
   they built, writing, certifications. Each area = one pass.
2. Per area, fill rows in `templates/AMMO-LEDGER.md` shape:
   `| claim | evidence (path/URL:lines) | number | employer translation | rating | use in |`.
   Translation contract: the employer column must be understandable by someone who has never used
   the person's tools or AI. Ratings: `resume-grade` / `interview-story` / `background`.
3. Spot-check 5 numbers against their evidence before trusting the ledger. Expect some to be wrong.
4. Promote only `resume-grade` rows into `CLAIMS-EVIDENCE-LEDGER.md`; status `verified` /
   `corrected → applied` / `partial`.
5. Keep ONE source-of-truth resume file (markdown). Generated formats (docx/pdf) are outputs; never
   edit them by hand.
6. Honesty rule: if AI wrote the code, say so in a way that names the real skill (directing,
   reviewing, testing, verifying) — never hide it, never apologize for it.

## Layer 2 — SEARCH (find, then prove live)

Rule: **HTTP 200 is not evidence a job is open.** Job pages are JavaScript apps and return 200 for
dead postings. A posting is LIVE only if the employer's board API still returns it (run
`tools/ats-sweep.mjs`) or you have seen a rendered apply control today. Otherwise mark `UNVERIFIED`.

1. **Slug discovery** — find which employers use which applicant-tracking system (Ashby, Lever,
   Greenhouse, Workable, Recruitee). Sources: the employer's careers URL (the host name tells you
   the platform), job-board listings, "powered by" footers. Write `slugs.json`:
   `[{"platform":"ashby","slug":"companyname"}]`.
2. **Board sweep** — `node tools/ats-sweep.mjs --selfcheck` must print `SELFCHECK OK` first (a
   broken run and an empty market both print zero rows; the self-check tells them apart). Then
   `node tools/ats-sweep.mjs --slugs slugs.json` → `sweep-<date>.md`. Edit `JUNIOR`, `REGION`,
   `NOT_REGION`, `STRENGTH_TERMS` at the top of the file for the person first.
3. **Read the verdicts as gate language, not depth.** `FIT` means nothing formally excludes the
   person — not that they can do the job. Every verdict cites the sentence that produced it; a
   human reads that sentence.
4. **Hard filters are quoted verbatim, never turned into a fit percentage.** "Final-year students
   only" is pass/fail. Compressing it to "70% fit" is how deadlines get lost.
5. **Web sweep** (for boards the tool cannot read): use `prompts/web-sweep.md`. Every row needs a
   URL the assistant actually opened; anything else is `UNVERIFIED`.
6. **Liveness ledger** — before a row enters Tier A, give it a `V-##` line in
   `VERIFY-LEDGER-<date>.md`: `VERIFIED-LIVE / CHANGED / DEAD / UNVERIFIED`, source, check time.

## Layer 3 — FINDINGS (`OPPORTUNITY-TRACKER.md` is the only queue)

Rule: **one tracker, and every session ends with at least one dated Activity-log row** — even if
the row says "no outcome — <why>". A session with no row is the failure mode.

- Tiers: A (act now, ordered) · B (after A) · Skip register (with the reason — never delete a row).
- Status vocabulary: `ready → submitted → screen → interview → offer / closed / withdrawn`; `LOST`
  for a missed deadline.
- Row contract: eligibility text verbatim · `V-##` liveness reference with check date · pay quoted
  or "not stated" · deadline quoted or "rolling" · the person's next action.
- Promotion path: sweep row → `VERIFIED-LIVE` → Tier B → package built → Tier A `ready` → Activity
  row `submitted` (the person's click, dated).

## Folder shape (copy `templates/`)

```
job-search/
  README.md                  ← intent-routed hub (templates/README-hub.md)
  AMMO-LEDGER.md
  CLAIMS-EVIDENCE-LEDGER.md
  resume.md                  ← source of truth
  OPPORTUNITY-TRACKER.md
  VERIFY-LEDGER-<date>.md
  slugs.json
  sweep-<date>.md            ← generated by tools/ats-sweep.mjs
  EXECUTION-LOG.md           ← one dated entry per session, appended
```

## Session end checklist
1. Activity-log row written (dated).
2. Tracker Tier A reflects reality (nothing `ready` that is actually lost or sent).
3. `EXECUTION-LOG.md` gets: what changed, files touched, next step.
4. Tell the person the ONE next action they can do in under two minutes.
