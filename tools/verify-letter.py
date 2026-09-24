r"""Gate for cover letters produced by `tools\make-letter.py`. Exit 1 on any failure. Self-
contained: reads files (postings, before\ copies, an optional resume PDF, the claims ledger) but
imports nothing beyond the standard library and this repo's own docx/Word bindings.

Probes, per letter:
  banned     - verb rule / voice-pass jargon / ruled-out wording (see BANNED)
  jargon     - voice-pass jargon list (see JARGON)
  verb       - first-person build/ship/write/code/verify (see VERB_RX)
  required   - COMMON_REQUIRED + the letter's own `required:` anchors
  date       - letter date == submit date (default today; override with --date)
  name       - your display name in header and signature, never WRONG_NAME
  quotes     - every quoted span of 4+ words appears verbatim in the resolved posting text
  resume_dup - no 8-word run shared with page 1 of your resume, except LOCKED phrases
               (needs --resume-pdf; without it this probe reports NOT CHECKED, not a failure)
  numbers    - every number in the letter traces to a CLAIMS-EVIDENCE-LEDGER.md row
  mirror     - the .md mirror's body == the .docx body
  page       - Word COM ComputeStatistics(2) == 1 (private DispatchEx instance; needs Word +
               pywin32). Without Word and without --no-page, this fails closed as NOT CHECKED.
               Pass --no-page to skip it instead of failing.

Negative controls, run for every target this invocation covers:
  A - each letter's `before:` copy must FAIL (at least one probe fires). Skipped per-letter when
      no `before:` file is given.
  B - banned/jargon/verb/page must each fire on at least one before\ copy, across all targets.
      UNPROVEN (not failed) if no target supplied a `before:` file at all.
  C - a planted mutation fires each of date/name/quotes/resume_dup/numbers/mirror on the NEW text.
      Self-contained; always runs.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # kit-user folder

# ---------------------------------------------------------------- config (edit for yourself)
NAME = "<Your Display Name>"
WRONG_NAME = "<a spelling you never want to see>"
COMMON_REQUIRED = ["available <term>", "start by <date>", "<github.com/yourhandle>", "<Your City>", "Sincerely,"]
BANNED = [
    WRONG_NAME, "mutation matrix", "proves", "proving", "operated", "can explain every mechanism",
    "explain every mechanism", "I use SQL regularly", "CI-verified", "responsible for", "I directly reran",
    "my working languages",
]
JARGON = ["oracle", "provenance", "fail-closed", "negative control", "lifecycle event", "doctrine", "load-bearing"]
VERB_RX = [r"\bI(?: would| will| can| could| have| had|'ve|'d)? (?:built|build|wrote|write|coded|code|shipped|ship|"
           r"verified|verify)\b", r"\bdeveloped\b(?! under my direction)"]
# Phrases lifted straight from your own resume that a letter must never repeat verbatim - populate
# from your own text (leave empty if you have none you're worried about yet).
LOCKED = []
SHINGLE = 8
PAGE_BUDGET_WORDS = 490
LEDGER = ROOT / "CLAIMS-EVIDENCE-LEDGER.md"

HEADER_RX = re.compile(r"^([a-z]+):\s*(.*)$")

# ---------------------------------------------------------------- number-vs-ledger check
YEAR = re.compile(r"^(1[89]|20)\d\d$")
PHONE = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")
NUMBER = re.compile(r"\b\d[\d,]*\b")


def numbers_in(text):
    text = PHONE.sub(" ", text)
    out = []
    for m in NUMBER.finditer(text):
        tok = m.group(0)
        if YEAR.match(tok.replace(",", "")):
            continue
        out.append(tok)
    return out


def ledger_numbers():
    nums = set(numbers_in(LEDGER.read_text(encoding="utf-8")))
    return nums | {n.replace(",", "") for n in nums}


def unbacked_numbers(text, ledger_nums):
    """-> [(number, sentence)] for every number in `text` not backed by ledger_nums."""
    out = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        for num in numbers_in(sentence):
            if num in ledger_nums or num.replace(",", "") in ledger_nums:
                continue
            out.append((num, sentence.strip()[:160]))
    return out


# ---------------------------------------------------------------- content-file header/body reader
def read_content(path):
    raw = path.read_text(encoding="utf-8")
    head, rest = re.split(r"\n\s*\n", raw, maxsplit=1)
    cfg = {}
    for ln in head.splitlines():
        m = HEADER_RX.match(ln.strip())
        if m:
            cfg[m.group(1)] = m.group(2).strip()
    cfg["required"] = [r.strip() for r in cfg.get("required", "").split("|") if r.strip()]
    before = cfg.get("before", "none")
    cfg["before"] = None if before.lower() == "none" else before
    cfg["body"] = [" ".join(block.split()) for block in re.split(r"\n\s*\n", rest.strip()) if block.strip()]
    return cfg


# ---------------------------------------------------------------- docx / md readers
def read_docx(path):
    import docx
    ps = [p.text for p in docx.Document(str(path)).paragraphs if p.text.strip()]
    return dict(date=ps[2], header=ps[0], signature=ps[-1], body=ps[4:-2], text="\n".join(ps))


def read_md(path):
    raw = re.sub(r"<!--.*?-->", " ", path.read_text(encoding="utf-8"), flags=re.S)
    date, lines = None, []
    for ln in raw.splitlines():
        s = ln.strip()
        if s.startswith("**Date:**"):
            date = s[len("**Date:**"):].strip()
        elif s and not s.startswith((">", "#", "**Subject:**")):
            lines.append(" ".join(s.split()))
    return dict(date=date, header=None, signature=lines[-1], body=lines[:-2], text="\n".join(lines))


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    return " ".join(s.lower().split())


def words(s):
    return re.sub(r"[^a-z0-9]+", " ", norm(s)).split()


# ---------------------------------------------------------------- probes: [] = pass
def p_banned(t):
    return [b for b in BANNED if b.lower() in t.lower()]


def p_jargon(t):
    return [j for j in JARGON if re.search(r"\b" + j, t, re.I)]


def p_verb(t):
    return [m.group(0) for rx in VERB_RX for m in re.finditer(rx, t)]


def p_required(t, extra):
    return [r for r in COMMON_REQUIRED + extra if r not in t]


def p_date(d, want):
    try:
        got = datetime.datetime.strptime(d or "", "%B %d, %Y").date()
    except ValueError:
        return ["unparseable letter date %r" % d]
    return [] if got == want else ["letter date %s != submit date %s" % (got, want)]


def p_name(L):
    out = []
    if L["header"] is not None and L["header"] != NAME: out.append("header name %r" % L["header"])
    if L["signature"] != NAME: out.append("signature %r" % L["signature"])
    if WRONG_NAME in L["text"]: out.append("%r in text" % WRONG_NAME)
    return out


QUOTE_RX = re.compile(r"[\"“](.+?)[\"”]")


def posting_text(key, content_dir):
    for ext in (".paste.md", ".api.txt"):
        p = content_dir / "postings" / (key + ext)
        if p.exists():
            return p.read_text(encoding="utf-8")
    raise FileNotFoundError("no posting file for %r under %s" % (key, content_dir / "postings"))


def p_quotes(t, key, content_dir):
    post = norm(re.sub(r"(?m)^\s*-\s+", "", posting_text(key, content_dir)))
    bad = []
    for q in QUOTE_RX.findall(t):
        q = norm(q).rstrip(" .,;:…")
        if q.endswith("..."):
            q = q[:-3]
        if len(q.split()) >= 4 and q not in post:
            bad.append(q[:80])
    return bad


_resume_shingles = None
_resume_shingles_path = None


def resume_shingles(resume_pdf):
    global _resume_shingles, _resume_shingles_path
    if _resume_shingles is None or _resume_shingles_path != resume_pdf:
        import fitz
        with fitz.open(str(resume_pdf)) as f:
            w = words(f[0].get_text())
        _resume_shingles = {tuple(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1)}
        _resume_shingles_path = resume_pdf
    return _resume_shingles


def p_resume_dup(t, resume_pdf):
    if not resume_pdf or not Path(resume_pdf).exists():
        return ["NOT CHECKED (no --resume-pdf given)"]
    for lock in LOCKED:
        t = re.sub(re.escape(lock), " | ", t, flags=re.I)
    w = words(t)
    shingles = resume_shingles(resume_pdf)
    hits = [" ".join(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1)
            if tuple(w[i:i + SHINGLE]) in shingles]
    return hits


def p_numbers(t, ledger_nums):
    return ["%s in: %s" % (n, s) for n, s in unbacked_numbers(t, ledger_nums)]


def p_mirror(docx_L, md_L):
    return [] if docx_L["body"] == md_L["body"] else ["md mirror body differs from docx body"]


_word = None
_word_unavailable = None


def p_page(path, no_page):
    global _word, _word_unavailable
    if no_page:
        return ["SKIPPED (--no-page)"]
    if _word_unavailable:
        return ["NOT CHECKED (no Word)"]
    try:
        import win32com.client
        if _word is None:
            _word = win32com.client.DispatchEx("Word.Application")
            _word.Visible = False
    except Exception:
        _word_unavailable = True
        return ["NOT CHECKED (no Word)"]
    d = _word.Documents.Open(str(Path(path).resolve()), ReadOnly=True, AddToRecentFiles=False)
    try:
        pages, wc = d.ComputeStatistics(2), d.ComputeStatistics(0)
    finally:
        d.Close(False)
    print("  page %s: %d page(s), %d Word-words (drafting budget %d)" % (Path(path).name, pages, wc, PAGE_BUDGET_WORDS))
    return [] if pages == 1 else ["%d pages (%d Word-words)" % (pages, wc)]


def text_probes(L, cfg, want_date, content_dir, ledger_nums, resume_pdf):
    return {
        "banned": p_banned(L["text"]), "jargon": p_jargon(L["text"]), "verb": p_verb(L["text"]),
        "required": p_required(L["text"], cfg["required"]), "date": p_date(L["date"], want_date),
        "name": p_name(L), "quotes": p_quotes(L["text"], cfg["posting"], content_dir),
        "resume_dup": p_resume_dup("\n".join(L["body"]), resume_pdf),
        "numbers": p_numbers("\n".join(L["body"]), ledger_nums),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--dir", default=None, help="where the docx/md live, default the kit-user root")
    ap.add_argument("--content-dir", default=None, help="where <target>.md content files live, default ROOT\\letters")
    ap.add_argument("--resume-pdf", default=None, help="your resume PDF, for the resume_dup probe; default none (NOT CHECKED)")
    ap.add_argument("--no-page", action="store_true", help="skip the Word page-count probe instead of failing closed")
    a = ap.parse_args()

    want = datetime.date.today()
    if a.date:
        want = datetime.datetime.strptime(a.date, "%B %d, %Y").date()
    print("submit date checked against:", want)

    content_dir = Path(a.content_dir) if a.content_dir else (ROOT / "letters")
    targets = sorted(p.stem for p in content_dir.glob("*.md") if not p.stem.startswith("_"))
    if a.only:
        targets = [t for t in targets if t == a.only]
    if not targets:
        print("no content files matched under %s" % content_dir)
        sys.exit(2)

    ledger_nums = ledger_numbers()
    fails, fired, any_before = [], set(), False
    for target in targets:
        cfg = read_content(content_dir / (target + ".md"))
        stem = cfg["stem"]
        if a.dir:
            letter_dir = Path(a.dir)
        elif cfg.get("dir"):
            letter_dir = ROOT / cfg["dir"]
        else:
            letter_dir = ROOT

        docx_p, md_p = letter_dir / (stem + ".docx"), letter_dir / (stem + ".md")
        print("\n=== %s" % target)
        L = read_docx(docx_p)
        r = text_probes(L, cfg, want, content_dir, ledger_nums, a.resume_pdf)
        r["mirror"] = p_mirror(L, read_md(md_p)) if md_p.exists() else ["no .md mirror"]
        r["page"] = p_page(docx_p, a.no_page)
        for k, v in r.items():
            print("  NEW  %-10s %s" % (k, v or "ok"))
            if v and not str(v[0]).startswith(("NOT CHECKED", "SKIPPED")):
                fails.append("%s %s: %s" % (target, k, v))

        # A: the before\ copy must fail (per-letter; UNPROVEN when no before: file is given)
        if cfg["before"] is None:
            print("  (no before: file for %s - negative control A: UNPROVEN, not failed)" % target)
        else:
            any_before = True
            b_path = ROOT / cfg["before"]
            B = read_docx(b_path) if b_path.suffix == ".docx" else read_md(b_path)
            rb = text_probes(B, cfg, want, content_dir, ledger_nums, a.resume_pdf)
            if b_path.suffix == ".docx":
                rb["page"] = p_page(b_path, a.no_page)
            hit = {k for k, v in rb.items() if v and not str(v[0]).startswith(("NOT CHECKED", "SKIPPED"))}
            fired |= hit
            print("  OLD  probes firing on %s: %s" % (b_path.name, {k: rb[k] for k in sorted(hit)} or "NONE"))
            if not hit: fails.append("negative control A: %s passes every probe" % b_path.name)

        # C: planted mutations, one per probe the before\ set cannot reliably trip. Self-contained.
        ref = L["body"]
        plants = {
            "date": p_date("September 4, 2001", want),
            "name": p_name(dict(L, signature=WRONG_NAME)),
            "quotes": p_quotes('Your posting asks for "someone who writes flawless code on the first try".',
                               cfg["posting"], content_dir),
            "resume_dup": None,
            "numbers": p_numbers("I directed 999999 logged agent runs, a figure in no ledger row at all.",
                                 ledger_nums),
            "mirror": p_mirror(L, dict(L, body=ref[:-1] + [ref[-1] + " Extra sentence."])),
        }
        if a.resume_pdf and Path(a.resume_pdf).exists():
            shingle = next(iter(resume_shingles(a.resume_pdf)), None)
            if shingle:
                plants["resume_dup"] = p_resume_dup(" ".join(shingle), a.resume_pdf)
        inert = [k for k, v in plants.items() if v is not None and not v]
        skipped = [k for k, v in plants.items() if v is None]
        print("  CTRL planted mutations inert:", inert or "none", ("(skipped, no --resume-pdf: %s)" % skipped if skipped else ""))
        if inert: fails.append("negative control C (%s): %s did not fire" % (target, inert))

    must_fire = {"banned", "jargon", "verb", "page"}
    print("\nnegative control B - probes that fired on before\\ set:", sorted(fired))
    if a.only:
        print("  (--only %s: negative control B needs the full battery, not enforced this run)" % a.only)
    elif not any_before:
        print("  UNPROVEN: no target supplied a before: file - provide letters\\before\\ copies to prove this control")
    elif must_fire - fired:
        fails.append("negative control B: %s never fired on before\\" % sorted(must_fire - fired))

    if _word is not None:
        _word.Quit()

    print("\nRESULT:", "PASS" if not fails else "FAIL\n  " + "\n  ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
