# Prompt — web sweep for live postings (for boards the sweep tool cannot read)

Give this to an AI assistant that can browse the web. Fill the profile block honestly; it is the
only thing about you that leaves your machine. Keep it public-safe (no phone, no address, no
financial or health details).

---

Today is <YYYY-MM-DD (Day)>. Web search enabled. No prior conversation visible.

## Candidate profile (honest, fixed — do not embellish)
<Name or "the candidate">, <program/year, e.g. 2nd-year engineering undergrad — NOT final year>,
expected graduation <year>. Based in <city/region>. Strengths, with proof: <3–5 lines naming what
you can show — repos, projects, work — and what you cannot (e.g. "no unassisted hand-coding;
strength is directing and verifying AI-built systems")>. Seeking <paid / unpaid>, <term dates>,
<on-site region / remote-<country>>.

## One goal
Find ≥<N> LIVE, currently-accepting roles this profile can realistically win.

## One request
Search job boards (<list: LinkedIn, Indeed, Glassdoor, your school's co-op board, company career
pages, regional tech boards>) for: <role keywords>. Write EXACTLY ONE file: `<output path>`.

A table, one row per role: company · title · location/remote · pay (quoted or "not stated") ·
deadline (quoted or "rolling") · direct apply URL · **eligibility hard-filters QUOTED VERBATIM**
(especially year-of-study / degree / citizenship requirements — never summarize these) · fit reason
(1 line vs the profile above) · screen risk (live coding? year filter?) · tier (A = apply now / B =
stretch / C = long shot). Sort tier A first.

## Rules
- Every row needs a real URL you actually opened; a role you could not open is marked UNVERIFIED.
- A role requiring final-year / graduated status never goes in tier A — quote that line, tier it C.
- No fabricated pay or deadlines: quote or say "not stated". Write only the one output file.
- Aggregator copies (Indeed, LinkedIn) are not the source: resolve to the employer's own posting.

## After the sweep (the human's job)
Every tier-A/B row gets a liveness check (`tools/ats-sweep.mjs` or a rendered apply control seen
today) before it enters `OPPORTUNITY-TRACKER.md`. The sweep is DRAFT until then.
