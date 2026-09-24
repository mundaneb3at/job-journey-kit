# GATES — from a lead to one verdict (v1)

The verdict ruler every lane cites: `protocols/SEARCH.md`, `RESUME.md`, `LETTERS.md`,
`OUTREACH.md`. Not a queue — `OPPORTUNITY-TRACKER.md` is the queue; this file only says what a row
becomes. Stop at the FIRST failing gate; that gate names the verdict.

## Producer of record

| artifact | producer | lands at |
|---|---|---|
| A verdict | you (or your assistant) walking G0–G9 in order over one lead | the tracker row's status field |
| A gate change | a hand edit to this file, dated in its own change log | this file |

## Rules — the gates, one line each

| gate | question | pass rule |
|---|---|---|
| G0 — live | is it confirmed open today? | board API, or a rendered apply control you've actually seen — HTTP 200 alone is not evidence. No → `DEAD`. |
| G1 — place | does the work location match what you'll actually accept? | on-site in your region, or remote in your country, per your own standing rule. No → `DEAD-by-ruling`; revisit only if you change that rule yourself. |
| G2 — clock | can the term start by `<start-by date>` and run the hours/weeks you need? | No → `DEAD`. The posting's own dates are unstated → `BLOCKED_ON_YOU` — that's a question for you, not a guess. |
| G3 — gate text | does a verbatim-quoted eligibility line exclude you? | Yes → `DEAD`. Ambiguous wording ("currently enrolled", work-authorization) → `BLOCKED_ON_YOU`, your answer only. |
| G4 — paid | is it paid? | No, and you haven't decided unpaid work counts for you → `DEAD`. Pay unstated → `BLOCKED_ON_YOU` (ask before building anything). |
| G5 — skill bar + honesty | does every stated requirement pass the 10-minute-call test — could you defend it out loud, unscripted, for ten minutes? | No → `DEAD`, not a gap to argue past. Unsure → `BLOCKED_ON_YOU`, name the one requirement. |
| G6 — route + actor | is there a real, working route (form/email/portal/program), and are **you** the one who clicks it? | No named route → `DEAD`. |
| G7 — package | letter states real gaps, claim-check clean, right résumé file, date current? | No → `READY_TO_PACKAGE` (build it). Yes → `READY_PACKAGED`. |
| G8 — order | which READY rows go first? | rank fit × clock × effort, then your own location preference, then nearest deadline, then fit. |
| G9 — argument | is every claim in the package one you've actually confirmed, not just drafted in a session? | Unconfirmed → `HOLD` (`BLOCKED_ON_YOU`). |

## Gate order

Walk G0 → G9 in sequence over one lead; the first gate that fails ends the walk and names the
verdict. A lead that clears G0–G6 moves to packaging (G7); G8 only ranks leads that already cleared
G7; G9 gates the final send, not the earlier research.

## Verdict words and where they land

| word | lands at |
|---|---|
| `READY_PACKAGED` / `READY_TO_PACKAGE` | tracker `ready` (Tier A/B) |
| `BLOCKED_ON_YOU` | one open question in your notes, recommendation first |
| `DEAD` / `DEAD-by-ruling` | tracker `closed` + a Skip register row naming the gate that failed |
| `SUBMITTED` | only via an Activity-log row — your click, timestamped, confirmed where you have confirmation |
| `HOLD` | package built, not sent — waiting on G9 |

A row is never "applied" because a file exists.

## Adding the next one

A new gate axis earns a permanent line here only once it's fired more than once — a single miss is
a lesson for your own notes, not a new gate. Add it between the two gates it logically sits between
(most new axes fit near G2 or G5), keep the one-line shape, and note the addition with a date in a
change log at the bottom of this file so a flipped ruling shows both the old and new line.

## Origins

Distilled from one owner's lane, 2026-09; incidents generalised.
