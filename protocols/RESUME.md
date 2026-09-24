# RÉSUMÉ PROTOCOL — one résumé for every send, producer → gate → blind recheck (v1)

This lane produces the one résumé every application sends; there is no per-target version —
tailoring for a specific posting lives in `protocols/LETTERS.md`, not here. Gate:
`tools/verify-resume.py` (template structure, banned/required strings, rendered-line and
page-split probes, unbacked numbers, PDF links). Findings from a version's blind recheck land in
that version's own dated notes; keep one line somewhere pointing at whichever version is live.

## Producer of record

| artifact | producer (exact command) | you get | mirror |
|---|---|---|---|
| A résumé version | `python tools/make-resume.py --version vN --date YYYY-MM-DD [--out DIR] [--content FILE] [--render]`; content = `resume-content.py` | `<Name>-Resume-<version>-<date>.docx` (+ `.pdf`, page renders with `--render`) | none |
| Content | `resume-content.py` at the root of your search folder (the folder that holds `tools/`): copy `templates/resume-content.example.py` there under that name once, then edit it directly | feeds the producer above | — |

## Rules (each with its source)

| # | rule | source |
|---|---|---|
| 1 | **ONE résumé for every send.** Per-target tailoring lives in the cover letter, not here. | one résumé is the only version you have to keep consistent |
| 2 | Template structure: a highlights section first, 2–3 one-line bullets, no summary/objective paragraph, a consistent section order, ≤ 2 pages. | a scannable page beats a dense one |
| 3 | Page 1 carries everything a skim-reader needs; nothing on a later page restates a page-1 claim. | a restated claim wastes the reader's second look |
| 4 | Every non-skill bullet renders as one line; skill lines stay short too. | a bullet that wraps reads as clutter, not content |
| 5 | Set a page budget in words and hold to it — a line count with no budget just drifts longer over time. | budgets that aren't measured become targets nobody hits |
| 6 | Every number needs an evidence row before it enters prose; a claim-checking pass over the ledger must pass. | a number nobody can re-check is not a fact, it's a guess labelled as one |
| 7 | **Verb rule:** if AI wrote the code, name what you actually did — directed, reviewed, tested — never first-person built/shipped/verified. | a first-person "I built" claim for AI-written work misrepresents the actual skill exercised |
| 8 | Keep a banned-phrase list for claims you've decided never to make again — a line cut once should stay cut. | a cut claim that quietly comes back defeats the reason it was cut |
| 9 | Your name is consistent everywhere it appears — the display form in text and the form used in filenames can differ from each other, but each stays constant across every document. | inconsistent name forms read as sloppy or, worse, as two different people |
| 10 | Term line stated verbatim, e.g. `<your term dates>, start by <start-by date>, <your region>`. | vague availability gets a posting silently discarded by a filter, not read past |
| 11 | Your professional links (LinkedIn, portfolio, etc.) verbatim and current. | a stale or wrong link is worse than no link |
| 12 | No jargon from your own tooling in employer-facing text — plain language outside a dedicated skills section. | a reader who doesn't share your tooling reads jargon as noise, not signal |
| 13 | Every repo / portfolio link is a real, clickable hyperlink in the rendered PDF, not just styled text. | a link that isn't a link doesn't get clicked |
| 14 | **Never hand-edit the generated file.** The moment it happens, it falls outside every gate below. | a hand-edited file that skipped the gate shipped with an error the gate would have caught |
| 15 | Read the page count and page split from the **rendered PDF**, never the source document — the source's own page count only sees explicit breaks. | a docx page count lies about what actually prints |

## Gate order

1. New number → add its evidence-ledger row first.
2. Edit `resume-content.py`.
3. `python tools/make-resume.py --version vN --date <today> --render` (close your word processor first — an open file blocks the write).
4. `python tools/verify-resume.py <docx> [--previous <docx>]` → **exit 0**. Negative control: must **FAIL** against an old/unedited version; with `--previous`, every changed probe must fire on the previous version too.
5. Run your claim-checking pass over the ledger → **exit 0**.
6. Blind recheck: hand the résumé to a fresh AI context with no memory of writing it → fix or rebut every row it raises → rerun step 4.
7. Read the rendered PDF once yourself; update wherever you keep the "current résumé" pointer.

## Adding the next one

No copy. Bump `--version`. The producer writes a dated folder holding the docx, pdf, renders and
recheck notes together. The producer and the gate stay the shared tools in `tools/`, never a
per-version script.

## Origins

Distilled from one owner's lane, 2026-09; incidents generalised.
