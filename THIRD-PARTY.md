# Third-party attributions

This kit is CC0 1.0. Some of the method in `prompts/` was learned from two MIT-licensed projects.
MIT text cannot be relicensed as CC0, so anything taken from them is listed here with its origin.

Nothing in this kit vendors upstream **code**. No file from either project is copied wholesale, no
dependency of either project is required, and neither project's setup was run to produce this kit —
both were read over the web, read-only, on 2026-09-04.

---

## career-ops

- Project: **career-ops** — https://github.com/career-ops-hq/career-ops
- License: MIT
- Read: `batch/batch-prompt.md`, `README.md`, `modes/` (2026-09-04)

What was taken, all **paraphrased into this kit's own wording** against this kit's own ledgers:

| Method | Where it lives here |
|---|---|
| Detecting the role's **archetype** — the job behind the title — before evaluating requirements | `prompts/evaluate-posting.md` §1 |
| The **two-pass rule**: rate how much the posting weights each requirement from the posting text alone, before opening any file about the candidate; importance is never revised afterward | `prompts/evaluate-posting.md` §2 |
| The **evidence-tier ladder** `stated` / `structural` / `inferred`, and the gate that an `inferred` requirement can never be rated `critical` or `high` | `prompts/evaluate-posting.md` §2 |
| Classifying the **hiring entity** before interpreting an advertised salary, and splitting the figure into guaranteed base vs variable vs non-cash | `prompts/evaluate-posting.md` §4 |
| Declaring what could **not** be checked as an explicit `not evaluated` state rather than omitting the row, so an all-clear can be trusted | `prompts/evaluate-posting.md` §6 |

Not taken: the archetype table's contents (specific to that project's target market), its 1–5
scoring, its PDF/tracker/plugin pipeline, and its installer.

---

## ai-job-search

- Project: **ai-job-search** — https://github.com/MadsLorentzen/ai-job-search
- License: MIT
- Read: `.claude/commands/apply.md`, `rank.md`, `interview.md`, `expand.md`, `README.md` (2026-09-04)

**Verbatim quotation** (one sentence, quoted and attributed at the point of use):

> "no claim in the room that isn't on the paper, and every claim on the paper must be defensible in
> depth."

— from `.claude/commands/interview.md`, © the ai-job-search contributors, MIT. Quoted in
`prompts/interview-prep.md`.

Everything else was **paraphrased**:

| Method | Where it lives here |
|---|---|
| The **drafter → reviewer** loop: a second assistant with no memory of writing the draft critiques it, with the draft passed inline | `prompts/tailor-application.md` §3 |
| The **factual grounding audit**: every date, employer, title and number checked against the union of the profile sources; ungrounded claims removed rather than softened; disagreement *between* the sources reported as a source problem, not draft drift | `prompts/tailor-application.md` §4 |
| **Write confirmed facts back to the profile in the same turn** — a fact that lives only in the conversation is treated as unsupported by the next session and silently stripped | `prompts/tailor-application.md` §1, `prompts/interview-prep.md` close |
| Reviewer output as **Part A** (exact-string structured edits) + **Part B** (narrative judgment calls), with every category answered even when the answer is "no issues" | `prompts/tailor-application.md` §3 |
| **Requirement coverage**: every stated requirement addressed — matched or honestly gapped, never silently omitted | `prompts/tailor-application.md` §2 |
| Deriving likely interview questions from **four sources in priority order**: earlier-stage feedback → evaluation gaps → stated requirements → stage type | `prompts/interview-prep.md` §1 |
| The **bridge answer** for a gap: acknowledge → adjacent experience → learning path, never invented experience | `prompts/interview-prep.md` §1, `prompts/cover-letter.md` §3 |
| Cutting any question the research already answers publicly | `prompts/interview-prep.md` §5 |
| A search snippet is a **lead, not a source** — company claims are verified on the employer's own pages before they enter a letter or a prep pack | `prompts/cover-letter.md` §2, `prompts/interview-prep.md` §0 |
| Treating the posting as **untrusted third-party data, never instructions** | header of all four new prompts |
| **Stage-appropriate prep** — a screen pack and a final-round pack are different documents | `prompts/interview-prep.md` §0 |

Not taken: the LaTeX CV and cover-letter templates and their compile-and-inspect loops, the Bun /
Python / TypeScript board-scraper CLIs, the salary-lookup, Gmail and Notion integrations, the
`seen_jobs.json` state machine, and the 0–100 weighted fit score (which conflicts with this kit's
rule that hard filters are quoted verbatim and never compressed into a percentage).

---

## Also read, nothing taken

- **observable-job-agent** — https://github.com/jamwithai/observable-job-agent (read 2026-08-31).
  Its structured fit-score/gap-list shape was reviewed and deliberately not adopted, for the same
  reason as above: this kit does not produce fit percentages.
