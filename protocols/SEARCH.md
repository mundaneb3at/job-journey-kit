# SEARCH PROTOCOL — find a posting, prove it live, verdict it (v1)

This lane turns a channel sweep or a manual search into one tracker row; nothing else counts as a
finding. Gate: `protocols/GATES.md` G0–G9, first failing gate names the verdict. Findings land in
`OPPORTUNITY-TRACKER.md` (Tier A/B, Skip register, Activity log) — the single queue; nothing gets
tracked twice in a second file.

## Producer of record

| artifact | producer (exact command) | lands at | mirror / origin |
|---|---|---|---|
| Sweep output | `node tools/ats-sweep.mjs --slugs slugs.json` | `sweep-<date>.json/.md` | raw machine output, no mirror |
| Liveness verdicts | your live check of each candidate (step 3 below) | `VERIFY-LEDGER-<date>.md`, one `V-##` line per row: `VERIFIED-LIVE / CHANGED / DEAD / UNVERIFIED`, source, check time | the tracker row cites its `V-##` |
| Channel list | hand-maintained — the boards, ATS platforms, and search queries you know to check | `slugs.json` (ATS platforms), plus any other channel list you keep | your own research |
| Manual search | a search-engine pass, or a browser walk, for boards the tool can't read | a dated note of what you searched and what came back | none |
| Verdict | `protocols/GATES.md` G0–G9, first failing gate names it | the tracker row | — |
| Finding | no producer — your own judgement, or a human read your assistant does for you | `OPPORTUNITY-TRACKER.md` Tier A/B, Skip register, Activity log | — |

## Rules (each with its source)

| # | rule | source |
|---|---|---|
| 1 | Sweep channels in the order your own yield data ranks them — ATS board APIs first; they're the only repeatable, receipted sweep. | measured, not guessed |
| 2 | A channel counts as swept only when a dated file shows what was queried and what came back. | an unreproducible sweep is not evidence |
| 3 | Never rely on a `--selfcheck` (or equivalent test) flag for today's real sweep — a self-check that overwrites the same dated output file as the real run has clobbered a finished sweep before. | a smoke-test mode reusing the real output path erased a day's work |
| 4 | If the sweep tool's internal clock runs UTC, name the dated file by your own local date, not the tool's — a run late at night can get named for tomorrow. | UTC/local date mismatch mis-named a sweep |
| 5 | A verdict like "fits" means nothing formally excludes you from the role — not that you can do the job. Read the gate language, not the perceived depth of the match; a human pass is still mandatory. | an automated classifier's plain-language false positives were caught only by hand |
| 6 | Widen your search terms before concluding nothing exists — adjacent titles turn up postings the obvious title misses. | narrow titles undercount a real market |
| 7 | Anything an AI recalls from memory with no live web access is unverified until a live URL check confirms it. | a model without web access invented a company domain that didn't exist |
| 8 | LIVE iff the employer's own board API returns the posting today, or you see a rendered apply control; HTTP 200 alone is never evidence. | several roles reported "open" on a 200 response were all dead |
| 9 | Record `first-seen: <date>` the first time a row appears. | dates the finding, not just the verdict |
| 10 | Compute any deadline or term-end date with a real date function, never in your head. | manual date arithmetic is unreliable even when the current date is in view |
| 11 | Quote every eligibility/exclusion line verbatim — never compress it to a fit percentage. | a hard filter compressed to a percentage is how a deadline gets lost |
| 12 | Resolve aggregator hits (job-board copies of a posting) to the employer's own board before trusting them. | an aggregator's copy of a posting had its deadline wrong against the employer's own listing |
| 13 | Tracker row contract: verbatim eligibility text, a liveness reference with a check date, pay quoted or "not stated", deadline quoted or "rolling", your own next action; no liveness date, no ready row. | an unreferenced "live" claim can't be re-checked |
| 14 | Promotion path: sweep row → verified-live → Tier B → package built → Tier A `ready` → Activity-log `submitted` (your click, dated). Status only advances via a new Activity-log row. | a status field with no log entry drifts from reality |
| 15 | Status vocabulary: `ready → submitted → screen → interview → offer / closed / withdrawn`; `LOST` = a missed deadline. | one shared vocabulary, not a dialect per session |
| 16 | Dead or expired rows go to the Skip register with a reason, never silently deleted; skipped targets aren't re-proposed without new evidence. | a deleted row gets re-discovered and re-worked from zero |
| 17 | One Activity-log row per sweep batch, even "no outcome — <why>". | a log with gaps looks like nothing happened on the missing days |
| 18 | Owner-only, never done by an assistant: portal login, account creation, anything that commits you to a person or an organization. | an assistant acting as you is a different kind of mistake than a wrong fact |

## Gate order

1. A channel is on your list — else add one first (see "Adding the next one").
2. Sweep it: `node tools/ats-sweep.mjs --slugs slugs.json` (or a manual search, dated) → a dated file.
3. Live-check every candidate (G0): board API answers today, or a rendered apply control is seen. Record each verdict as a `V-##` line in `VERIFY-LEDGER-<date>.md` (the sweep file is raw rows; this ledger is what the tracker cites).
4. Run `protocols/GATES.md` G0 through G9 in order; the first failing gate names the verdict.
5. Append the tracker row (quoted gate text, `first-seen`, its `V-##` liveness reference) or move it to the Skip register with its reason.
6. Write one Activity-log row for the sweep batch.
7. Any owner-only step (login, account creation) stays listed in the row, never done by an assistant.
8. Coverage check: before calling a sweep complete, have your assistant try to find anything eligible missing from the tracker, working only from your channel list and `protocols/GATES.md`.

## Adding the next one

Add a channel to your list: exact query, auth needed, cost, coverage, which tool reads it. Sweep it
once with a dated file and note what it yielded. A slug found inside a posting (a sibling employer
on the same ATS) goes into `slugs.json` the same day you find it.

## Origins

Distilled from one owner's lane, 2026-09; incidents generalised.
