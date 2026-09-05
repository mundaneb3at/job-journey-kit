# Prompt — interview prep (defend what you already put on paper)

Run this once a stage is booked. It builds a prep pack for **one stage of one application** — a
phone screen and a final round are different documents, and a pack written for the wrong stage is
worse than none because it spends your preparation on the wrong questions.

**The one rule here, quoted from the project this method came from:** *"no claim in the room that
isn't on the paper, and every claim on the paper must be defensible in depth."*
(— `MadsLorentzen/ai-job-search`, MIT; see `THIRD-PARTY.md`.)

Inputs: the submitted `applications/<company>-<role>/` files, `evaluations/<company>-<role>.md`,
`OPPORTUNITY-TRACKER.md` (the row and its activity log), `AMMO-LEDGER.md`.
Output: `applications/<company>-<role>/interview-prep-<stage>.md`.

---

Today is `<YYYY-MM-DD>`. Prepare me for ONE interview stage.

Stage: `<phone screen | technical | panel | final | other>`. Interviewers, if known: `<names>`.

## 0. Ground yourself first

Read what was actually submitted — not `resume.md`, but the tailored files in
`applications/<company>-<role>/`. That is what the interviewer read. Then read the evaluation's
requirement matrix and the tracker row's activity log (anything flagged at an earlier stage).

Research the employer only from its own pages, plus coverage you open and read. Every specific that
reaches the pack must be independently confirmed — a search snippet is a lead, not a source. An
unverified "fact" delivered confidently in an interview is worse than saying nothing.

If interviewer names are known, note the likely angle from public professional information only: a
hiring manager probes motivation and team fit, a senior practitioner probes technical depth, HR
probes the timeline on the résumé. Do not speculate past what is public.

## 1. Likely questions — derived in this priority order

1. **Anything flagged, doubted or left unresolved at an earlier stage** (the tracker's activity
   log). It comes back. It always comes back.
2. **The evaluation's `critical` and `high` gaps.** The requirements where I am weakest are the
   likeliest probes. Each gets a bridge answer: acknowledge → adjacent experience → what I am doing
   about it. **Never prepare an answer that invents experience.**
3. **The posting's stated requirements**, one at a time.
4. **The stage.** Screens get motivation, availability and timeline. Technical rounds get the
   posting's stack. Final rounds get values, pay, and "any reservations about us?"

## 2. STAR mapping, grounded in the ledger

For each likely question, map a STAR answer (Situation / Task / Action / Result) built **only** from
rows in `AMMO-LEDGER.md`. Ledger facts arranged into S/T/A/R — not embellished, not rounded up. If a
question has no ledger row behind it, say so and tell me what to go verify, rather than writing a
story I cannot defend.

Mark any answer whose Result number is not `verified` in `CLAIMS-EVIDENCE-LEDGER.md`: those are the
ones to soften into what I can prove, before I say them out loud.

## 3. Consistency brief

List the specific claims the **submitted** résumé and letter make — achievements, numbers, skills
emphasized — that the interviewer is most likely to probe, with the evidence row behind each. This
is the section I read in the ten minutes before the call.

Flag anything the documents claim that I could not defend for two minutes under follow-up. That is
not a prep gap, it is a document problem, and it is better to know now.

## 4. Tough questions, this employer

The uncomfortable ones, answered for *this* application, not in general: why this employer
specifically (use the verified specifics from §0 — never a generic line), the gap from §1.2, the
timeline question the résumé invites, pay expectations if the stage warrants it, and why I am
leaving or available.

## 5. Questions I ask them

Four to six, matched to the stage: role and team at a screen, technical practice and growth at a
technical round, culture and leadership at the final round — the last chance to catch a
deal-breaker before it becomes my problem.

**Cut any question the research already answers publicly.** Asking it signals I did not look.

## 6. Logistics

Format, date, time and time zone, joining link or address, interviewer names, what to bring, and
what to have open on a second screen.

## Output

Write `applications/<company>-<role>/interview-prep-<stage>.md` (one file per stage — earlier packs
stay as history) and give me the consistency brief in chat.

Then offer a mock: play the interviewer for this stage, warm-up first, then the role's technical
questions, one or two behavioural questions tied to the posting, and one curveball. After each
answer say what worked, what to tighten, and which STAR story from §2 would have served better.

**Afterwards:** write a dated row in `OPPORTUNITY-TRACKER.md`'s activity log with the stage, how it
went, and anything the interviewer flagged — that row is input 1 for the next stage's prep. And any
fact I surfaced while preparing that is not yet in `AMMO-LEDGER.md` goes into the ledger in the same
turn, with its evidence. A fact that lives only in a prep pack will be treated as unsupported by the
next drafting session and stripped out.
