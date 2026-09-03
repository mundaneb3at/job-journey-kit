# Resume claims — evidence ledger (sweep <YYYY-MM-DD HH:MM>)

Every quantified resume claim re-derived from a primary source. Statuses: `verified` (re-derived,
producer named) · `corrected → applied` (was wrong or stale; resume fixed in the same sitting) ·
`partial` (true with a caveat, noted). **Producer commands must be rerunnable by an outsider.**

**Gate: a number without a row here does not go on the resume.**

| # | Claim (as written in resume.md) | Status | Evidence / producer |
|---|---|---|---|
| 1 | "52 automated test cases" | verified | `cd <repo> && python -m pytest -q` → `52 passed` on `<date>` |
| 2 | "4 public repositories" | corrected → applied | `gh repo list <you> --json visibility,isFork` → 5 public, 1 is a fork → resume now says "4 own + 1 fork" |
| 3 | "onboarded 4 new members from my setup guide" | partial | 4 people confirmed by chat log `<path>`; the guide is one of two they used — resume says "co-authored" |
| | | | |

## Prohibited claims (things the evidence does not back — keep the list, it is the honesty guard)
- <e.g. "proficient in cloud platforms" — no artifact exists; do not claim>
