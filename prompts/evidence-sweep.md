# Prompt — evidence sweep (fills AMMO-LEDGER.md from your own files)

Give this to your AI assistant with access to your files. Run it once per AREA (repos, course
projects, jobs, volunteering, tools you built, writing). If the assistant can run sub-tasks in
parallel, one per area.

---

Today is <YYYY-MM-DD>. You are compiling evidence about MY work for a job search. You may only
report what you can point to in a file, a command output, or a URL you opened. Nothing inferred,
nothing rounded up.

AREA for this pass: <e.g. my GitHub repositories under <path or URL>>

For every distinct thing I did in this area, write ONE row in this exact shape:

| claim | evidence (path or URL, lines) | number | employer translation | rating | use in |

Rules:
1. **evidence** = the file path with line numbers, the command you ran and its output, or the URL
   you opened. If you cannot cite it, do not write the row.
2. **number** = a count, size, date, pass/fail result, or "none" — never an adjective. Say how it
   was measured ("`ls | wc -l` → 14 files on <date>").
3. **employer translation** = one sentence a hiring manager who has never used my tools or an AI
   assistant would understand. No jargon. If AI wrote the code, the translation names what I
   actually did (directed, reviewed, tested, verified) — do not hide it, do not apologize for it.
4. **rating** = `resume-grade` (a checkable number an employer would care about) ·
   `interview-story` (a good 2-minute answer) · `background` (context only).
5. **use in** = where this would appear: resume bullet, cover letter, a specific interview question.
6. When two of my files disagree about a number, print BOTH and mark the row `CONFLICT` — do not
   pick one.
7. Cap at 15 rows per area; prefer fewer verified rows over many weak ones.

Output: append the rows under `## area: <name>` in `AMMO-LEDGER.md`. Then list the 5 rows whose
numbers you are LEAST sure of, so I can spot-check them myself.
