r"""Gate for cold outreach texts. Read-only except stdout. Exit 1 on any failure.

Reads outreach\*.md (a file starting with "_" is a template and is skipped). File shape: a "#
title" line, then "key: value" header lines (to / subject / source / status) up to the first
blank line, then the body you paste. See `templates\outreach\_TEMPLATE.md`.

Probes, per file:
  banned    - ruled-out wording (see BANNED)
  jargon    - voice-pass words (see JARGON)
  verb      - never first-person built/wrote/shipped/verified; "developed" only under direction.
              "I build with AI coding agents" is a positioning line, allowed by name.
  required  - paid; term/start-date anchors; the honest-positioning line; a closing ask for a
              short call; your expected-availability line; your repo/portfolio link; a "source:"
              header URL for the quoted employer line
  name      - your display name in the signature, never WRONG_NAME
  links     - every link is a plain https URL; no google.com/url, safelinks, lnkd.in, /url?q=
              wrappers (a redirect-wrapped link is a real defect: some mail clients rewrite links
              you paste from a compose window)
  spelling  - Word spell-check (private instance, en-CA 4105); only lowercase misspellings count,
              proper nouns are skipped. Without Word and without --no-spell, this fails closed as
              NOT CHECKED. Pass --no-spell to skip it instead.
  numbers   - every number in the body has a row in CLAIMS-EVIDENCE-LEDGER.md

Negative controls:
  (A) the as-sent set under outreach\before\*.md must FAIL as a set. UNPROVEN (not failed) if that
      folder has no files - there is no owner-neutral "bad outreach" this kit can ship as a default.
  (B) `spelling` must fire on the as-sent set (same UNPROVEN rule).
  (C) planted mutations of a passing body, one per probe the as-sent set cannot trip: links,
      banned, jargon, verb, required, name, numbers. Self-contained; always runs, using either a
      live file that passes or a synthetic built-in body if nothing does.

Run:  python tools\verify-outreach.py [--only <target>] [--dir DIR] [--assent DIR] [--no-spell]
"""
import re
import sys
from pathlib import Path

# ---------- config (edit for yourself; the kit ships placeholders) ----------
ROOT = Path(__file__).resolve().parents[1]                        # kit-user folder
OUTREACH = ROOT / "outreach"
ASSENT = ROOT / "outreach" / "before"
LEDGER = ROOT / "CLAIMS-EVIDENCE-LEDGER.md"
NAME = "<Your Display Name>"
WRONG_NAME = "<a spelling you never want to see>"
REQUIRED = ["paid", "expected <grad year>", "<github.com/yourhandle>"]
REQUIRED_RX = {
    "term": r"\b(\d+|twelve|ten|eight) weeks\b|\b(\d{2,4}|four hundred twenty) hours\b|<term>",
    "start": r"\b(start(ing)?|begin(ning)?) (by|on or before) <date>\b|\bstart(ing)? by\b",
    "positioning": r"do not represent myself as an unassisted hand-coder|my focus is testing what they produce"
                   r"|check(ing)? the result by watching what it does|pushing edge cases",
    "call": r"\b(\d+|fifteen|twenty|short|quick|brief)[- ]minute\b[^.\n]{0,25}\b(call|conversation|chat)\b"
            r"|\ba (short|quick|brief) (call|conversation|chat)\b",
}
BANNED = [WRONG_NAME, "mutation testing", "mutation matrix", "proves", "proving", "I use SQL regularly",
          "can explain every mechanism", "explain every mechanism", "responsible for", "CI-verified", "my working languages",
          "operated"]
JARGON = ["oracle", "provenance", "fail-closed", "negative control", "lifecycle event", "doctrine", "load-bearing"]
VERB_RX = [r"\bI(?: would| will| can| could| have| had|'ve|'d)? (?:built|wrote|write|coded|code|shipped|ship|verified|verify)\b",
           r"\bI(?: would| will| can| could| have| had|'ve|'d)? build\b(?! with (?:AI|agents|coding))",
           r"\bverify the result myself\b", r"\bdeveloped\b(?! under my direction)"]
REDIRECT_RX = re.compile(r"google\.com/url|safelinks\.protection|/url\?q=|lnkd\.in/|bit\.ly/|\bt\.co/", re.I)
URL_RX = re.compile(r"https?://[^\s)>\]]+|\b(?:www\.)?[a-z0-9-]+\.(?:com|ai|ca|io|org|net)(?:/[^\s)>\]]*)?", re.I)
SPELL_LANG = 4105                                 # wdEnglishCanadian; en-US (1033) flags "behaviour", "licence"
SPELL_ALLOW = {"co-op", "github", "agentic", "fintech", "onboarding", "workflows", "workflow", "runbook", "https",
               "linkedin", "ai", "hr", "wk"}
NOTE_RX = re.compile(r"^\[as-sent defect.*$", re.M)        # an as-sent metadata line, never body text
NUMBER = re.compile(r"\b\d[\d,]*\b")
YEAR = re.compile(r"^(1[89]|20)\d\d$")
PHONE = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")


# ---------- readers ----------
def read(path):
    """-> dict(title, header{k: v}, body, text). Header = key: value lines before the first blank line."""
    raw = NOTE_RX.sub("", path.read_text(encoding="utf-8")).replace("\r\n", "\n")
    lines = raw.split("\n")
    title = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("#") else ""
    i, header = 1 if title else 0, {}
    while i < len(lines) and lines[i].strip():
        k, _, v = lines[i].partition(":")
        if _: header[k.strip().lower()] = v.strip()
        i += 1
    body = "\n".join(lines[i:]).strip()
    return dict(title=title, header=header, body=body, text=body)


def numbers_in(text):
    text = PHONE.sub(" ", text)
    return [t for t in NUMBER.findall(text) if not YEAR.match(t.replace(",", ""))]


_ledger_nums = None


def ledger_numbers():
    global _ledger_nums
    if _ledger_nums is None:
        n = set(numbers_in(LEDGER.read_text(encoding="utf-8")))
        _ledger_nums = n | {x.replace(",", "") for x in n}
    return _ledger_nums


# ---------- probes: each returns a list of problems, [] = pass ----------
def p_banned(t):
    return [b for b in BANNED if b.lower() in t.lower()]


def p_jargon(t):
    return [j for j in JARGON if re.search(r"\b" + re.escape(j), t, re.I)]


def p_verb(t):
    return [m.group(0) for rx in VERB_RX for m in re.finditer(rx, t)]


def p_required(t):
    out = [r for r in REQUIRED if r.lower() not in t.lower()]
    out += ["no %s line" % k for k, rx in REQUIRED_RX.items() if not re.search(rx, t, re.I)]
    return out


def p_header(L):
    """outreach\\<target>.md header shape (live files only; before\\ copies may use a bare shape)."""
    h = L["header"]
    out = ["no %s:" % k for k in ("to", "subject", "status") if not h.get(k)]
    src = h.get("source", "")
    if not src.startswith("https://"): out.append("source: is not an https URL (%r)" % src[:40])
    return out


def p_name(t):
    out = []
    if WRONG_NAME in t: out.append("%r in text" % WRONG_NAME)
    if NAME not in t: out.append("signature lacks %r" % NAME)
    return out


def p_links(t):
    out = [m.group(0) for m in REDIRECT_RX.finditer(t)]
    out += ["not https: " + u for u in URL_RX.findall(t) if u.lower().startswith("http://")]
    return out


_word = None
_word_unavailable = None


def p_spelling(t, spell):
    """Lowercase misspellings per Word (en-CA). Private Word process; your own open Word is never
    touched. Without Word and without --no-spell, this fails closed as NOT CHECKED."""
    global _word, _word_unavailable
    if not spell:
        return ["SKIPPED (--no-spell)"]
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
    d = _word.Documents.Add()
    try:
        d.Content.Text = t
        d.Content.LanguageID = SPELL_LANG
        errs = [e.Text for e in d.SpellingErrors]
    finally:
        d.Close(False)
    return sorted({e for e in errs if e[:1].islower() and e.lower() not in SPELL_ALLOW})


def p_numbers(t):
    return ["%s in: %s" % (n, s.strip()[:70]) for s in re.split(r"(?<=[.!?])\s+", t)
            for n in numbers_in(s) if n not in ledger_numbers() and n.replace(",", "") not in ledger_numbers()]


def probes(L, spell):
    t = L["text"]
    r = {"banned": p_banned(t), "jargon": p_jargon(t), "verb": p_verb(t), "required": p_required(t),
         "name": p_name(t), "links": p_links(t), "numbers": p_numbers(t)}
    if "status" in L["header"]: r["header"] = p_header(L)      # outreach\ shape; before\ copies may lack status:
    r["spelling"] = p_spelling(t, spell)
    return r


def is_control_finding(v):
    return bool(v) and str(v[0]).startswith(("NOT CHECKED", "SKIPPED"))


SYNTHETIC_BASE = {"header": {}, "text": (
    "Hi <Employer> team,\n\n"
    "I'm a student looking for a paid co-op placement this fall, available <term>, "
    "start by <date>.\n\n"
    "Your <page> says \"a sentence quoted verbatim from the source URL above,\" and that's the "
    "kind of system I like working on. I build with AI coding agents, and my focus is testing "
    "what they produce: pushing edge cases, checking outputs against clear expected results, and "
    "leaving an evidence trail someone can review before a release. You can see my work at "
    "<github.com/yourhandle>.\n\n"
    "I'd be glad to help your team test and verify <what they build> this term. Would you be "
    "open to a short call this or next week?\n\n"
    "Thanks,\n<Your Display Name>\n<school> (expected <grad year>) · <phone> · <github.com/yourhandle>"
)}


def main():
    args = sys.argv[1:]
    only = args[args.index("--only") + 1] if "--only" in args else None
    src = Path(args[args.index("--dir") + 1]) if "--dir" in args else OUTREACH
    assent = Path(args[args.index("--assent") + 1]) if "--assent" in args else ASSENT
    spell = "--no-spell" not in args
    fails, fired = [], set()
    files = sorted(p for p in src.glob("*.md") if not p.name.startswith("_") and (only is None or p.stem == only))
    if not files and only: fails.append("--only %s: no such file under %s" % (only, src))
    print("live outreach texts under %s: %d %s" % (src, len(files), "(none to check; controls still run)" if not files else ""))
    passing = None
    for p in files:
        L = read(p)
        print("\n=== %s  (to: %s | status: %s)" % (p.stem, L["header"].get("to", "?"), L["header"].get("status", "?")))
        r = probes(L, spell)
        for k, v in r.items():
            print("  NEW  %-9s %s" % (k, v or "ok"))
            if v and not is_control_finding(v): fails.append("%s %s: %s" % (p.stem, k, v))
        if not any(v for v in r.values() if not is_control_finding(v)) and passing is None: passing = L

    # A/B: the as-sent set must fail as a set, and spelling must fire on it. UNPROVEN if absent.
    as_sent = sorted(assent.glob("*.md")) if assent.exists() else []
    set_failed = False
    for p in as_sent:
        L = read(p)
        r = probes(L, spell)
        hit = {k for k, v in r.items() if v and not is_control_finding(v)}
        fired |= hit; set_failed |= bool(hit)
        print("  OLD  as-sent %-14s firing: %s" % (p.stem, {k: r[k] for k in sorted(hit)} or "NONE"))
    if as_sent and not set_failed: fails.append("negative control A: every as-sent body passes every probe")
    if not as_sent: print("negative control A/B: UNPROVEN - no files under %s to prove this gate isn't inert" % assent)
    elif spell and "spelling" not in fired: fails.append("negative control B: spelling never fired on the as-sent set")

    # C: planted mutations of a passing body, one per probe the as-sent set cannot trip. Self-
    # contained: falls back to a synthetic body if nothing real passes, so it always runs.
    base = passing or (read(as_sent[0]) if as_sent else None) or SYNTHETIC_BASE
    b = base["text"]
    plants = {
        "links": p_links(b + "\nMy work: https://www.google.com/url?q=https://example.com"),
        "banned": p_banned(b + "\nWe used mutation testing throughout."),
        "jargon": p_jargon(b + "\nAn oracle checks the provenance."),
        "verb": p_verb(b + "\nI built the checker and I verify each run."),
        "required": p_required(re.sub(REQUIRED_RX["term"], "some time", b, flags=re.I)),
        "header": p_header(dict(base, header=dict(base.get("header", {}), source="see site"))),
        "name": p_name(b.replace(NAME, WRONG_NAME)),
        "numbers": p_numbers(b + "\nI directed 999999 logged agent runs, a figure in no ledger row at all."),
    }
    inert = [k for k, v in plants.items() if not v]
    print("\n  CTRL planted mutations inert:", inert or "none")
    if inert: fails.append("negative control C: %s did not fire" % inert)
    print("\nnegative control B - probes that fired on the as-sent set:", sorted(fired))

    if _word is not None:
        _word.Quit()
    print("\nRESULT:", "PASS" if not fails else "FAIL\n  " + "\n  ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        sys.stdout.buffer.write((__doc__ + "\n").encode("utf-8")); sys.exit(0)
    main()
