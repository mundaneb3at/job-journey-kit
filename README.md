# job-journey-kit

A method for running a job / internship / co-op search with evidence instead of vibes. Three
ledgers, one rule each, and a small tool that proves a posting is actually open. Works with any AI
assistant that can read and write files (Claude Code, Codex CLI, Cursor, or paste `SKILL.md` into a
chat). No accounts, no keys, no dependencies beyond Node 18+ for the sweep tool.

## The three rules

| Layer | File | The rule |
|---|---|---|
| **Ammunition** — what you can truthfully say about yourself | `AMMO-LEDGER.md` → `CLAIMS-EVIDENCE-LEDGER.md` → `resume.md` | A number reaches your resume only with an evidence row someone else could re-check. |
| **Search** — finding postings and proving they are open | `slugs.json` + `tools/ats-sweep.mjs` → `VERIFY-LEDGER-<date>.md` | HTTP 200 is not evidence a job is open. Live = the employer's board API still returns it. Hard filters are quoted verbatim, never turned into a fit %. |
| **Findings** — where everything lands | `OPPORTUNITY-TRACKER.md` | One tracker. Every session ends with a dated Activity-log row. You click every submission yourself. |

And the rule above all three: **if an application is built and unsent, the first thing your
assistant does is ask you "submit, not this one, or blocked on what?"** Tidying the folder is not
progress.

## Start in 10 minutes

1. Copy `templates/` into a new folder, e.g. `job-search/`. Rename `README-hub.md` → `README.md`.
2. Give your AI assistant `SKILL.md` (install it as a skill, or paste it as the first message).
3. Say: *"Run the evidence sweep over my repos / projects / work history and fill AMMO-LEDGER.md."*
   Then spot-check five numbers yourself. Some will be wrong. That is the point.
4. Write `resume.md` from `CLAIMS-EVIDENCE-LEDGER.md` rows only.
5. Build `slugs.json` (which employers use which applicant-tracking system — the careers-page host
   name tells you: `jobs.ashbyhq.com/<slug>`, `jobs.lever.co/<slug>`, `boards.greenhouse.io/<slug>`,
   `apply.workable.com/<slug>`, `<slug>.recruitee.com`).
6. `node tools/ats-sweep.mjs --selfcheck` → must print `SELFCHECK OK`. Then
   `node tools/ats-sweep.mjs --slugs slugs.json` → read `sweep-<date>.md`. Edit the regexes at the
   top of the tool for your level, region, and strengths first.
7. Move rows you will act on into `OPPORTUNITY-TRACKER.md` Tier B, verify each is live, promote to
   Tier A, build the package, submit it yourself, log the row.

## What is in here

```
SKILL.md                         the method, written as instructions to an AI assistant
README.md                        this file
templates/
  README-hub.md                  intent-routed hub for your search folder ("I want to apply now" → file)
  AMMO-LEDGER.md                 evidence bank schema + example rows
  CLAIMS-EVIDENCE-LEDGER.md      the resume-number gate
  OPPORTUNITY-TRACKER.md         tiers, skip register, activity log
prompts/
  evidence-sweep.md              the prompt that fills AMMO-LEDGER.md from your own files
  web-sweep.md                   the prompt for a web search of postings, with the verbatim-filter rule
tools/
  ats-sweep.mjs                  board-API liveness + eligibility sweep (Node 18+, zero deps)
```

## Why these rules exist (each one cost someone something)

- **"HTTP 200 ≠ open":** seven roles were confidently reported open on one day and were all dead —
  the pages loaded fine.
- **"Quote the hard filter verbatim":** a "final-year students only" line got compressed into a
  fit score; the application was built and the deadline passed on a role that could never be won.
- **"One tracker, one dated row per session":** the tracker's activity log had a single row after
  nine days of sessions. Work happened; outcomes did not.
- **"Ask the submit question first":** two complete packages sat unsent for nine days while the
  folder grew.
- **"Numbers need an evidence row":** the same person's own documents claimed 3, 9, and 10 public
  repos. The true count was measured, and it was none of those.

## Adapting it

Everything specific to one person lives in three places: the regexes at the top of
`tools/ats-sweep.mjs` (level, region, strengths), the example rows in `templates/`, and the
profile block in `prompts/web-sweep.md`. Change those; keep the rules.

License: CC0 — copy, edit, share.
