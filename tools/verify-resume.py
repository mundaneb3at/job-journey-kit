r"""Checks for a resume .docx produced by `make-resume.py`. Self-contained: imports nothing except
its sibling `tools\verify-template.py`.

Probes: banned/required/jargon phrases, structure (availability/term/prose-in-skills), one
rendered line per non-skill bullet, no number restated across the page break, exact heading sets
per page, rendered-PDF page count == 2, every repo/profile link clickable in the PDF, page-1/2
word budgets, the template-structure gate, and every number backed by a
`CLAIMS-EVIDENCE-LEDGER.md` row (at the kit-user root, next to this repo's `tools\` folder).

Negative control: `--old <docx>` (an older/weaker resume of yours) must fail >= 5 probes, or this
gate is reporting itself inert. Without `--old`, that control is UNPROVEN, not failed - there is
no owner-neutral "bad resume" this kit can ship as a default. `--previous` lists every probe that
regressed (fired on the older docx, passes on the new one).

RESULT: PASS|FAIL, exit 1 on failure. A missing rendered PDF fails closed unless `--no-pdf` is
passed (then the PDF-only probes are explicitly SKIPPED, not failed).

Run:  python tools\verify-resume.py <docx> [--pdf <pdf>] [--previous <docx>] [--old <docx>] [--no-pdf]
"""
import argparse
import importlib.util
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent       # <kit-user folder>\tools
ROOT = HERE.parent                           # kit-user root
LEDGER = ROOT / "CLAIMS-EVIDENCE-LEDGER.md"


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


template = _load_module("verify_template", HERE / "verify-template.py")


# ---------------------------------------------------------------- config (edit for yourself)

NAME = "<Your Display Name>"

# Phrases you never want to see in your own resume - AI-voice tells and overclaiming. Edit freely;
# this list is generic writing-quality guidance, not tied to any one person's history.
BANNED = [
    "verified by me", "checked by me", "tested it myself", "I verify", "I built", "I wrote", "I coded",
    "I shipped", "I verified", "myself", "mutation matrix", "proves", "operated", "genuinely good at",
    "responsible for", "helped", "assisted",
    "nothing counts as done until", "can explain every mechanism", "I use SQL regularly", "CI-verified",
]
BANNED_RX = [r"\bI (built|build|wrote|write|coded|code|shipped|ship|verified|verify)\b",
             r"\bdeveloped\b(?! under my direction)"]
# Certifications/phrases from an OLDER version of your own resume that must not silently reappear
# once you've dropped them. Empty by default - populate from your own history.
CERT_BANNED = []
# JARGON is checked over Highlights + project bullets ONLY (probe_jargon skips the Technical
# Skills section, where some of these words can legitimately describe your own methodology).
JARGON = ["oracle", "provenance", "fail-closed", "negative control", "lifecycle event", "doctrine", "load-bearing"]

REQUIRED = [
    NAME,
    "available <term>",
    "linkedin.com/in/",
    "under my direction",
    "expected <grad year>",
    "Still learning:",
    "Highlights",
]

P1_HEADINGS = {"Highlights", "Education", "Technical Skills", "Technical Projects"}
P2_HEADINGS = {"Additional Projects", "Additional Experience", "Extracurricular Activities"}

# no_restated_numbers: broad token pattern (dates/ranges count as one token; years excluded)
NUM = re.compile(r"\b\d{4}-\d\d-\d\d\b|\b\d+-\d+\b|\b\d[\d,]*\b")
NUM_YEAR = re.compile(r"^(19|20)\d\d$")
# Set to your real phone number so its digits aren't flagged as an unbacked claim number. A
# bracketed placeholder (no digits) is harmless here - nothing to strip.
PHONE = "<phone>"

# unbacked_numbers vs the ledger, reimplemented inline (no import from any dated lane folder).
# YEAR excludes 18xx/19xx/20xx. PHONE and (optionally) your LinkedIn profile id are stripped first
# - neither is an evidence claim.
LEDGER_NUMBER = re.compile(r"\b\d[\d,]*\b")
LEDGER_YEAR = re.compile(r"^(1[89]|20)\d\d$")
# Set to the numeric id in your own LinkedIn URL so it isn't flagged as an unbacked claim number.
LINKEDIN_ID = "<linkedin-id>"

# links: any repo/profile URL token found in the docx text must be a clickable PDF annotation
URL_RX = re.compile(
    r"github\.com/[A-Za-z0-9_.\-/]*[A-Za-z0-9_\-]"
    r"|linkedin\.com/in/[A-Za-z0-9\-]+"
    r"|[A-Za-z0-9\-]+\.github\.io"
)


# ---------------------------------------------------------------- readers

def paragraphs(docx):
    """[(text, is_bullet, is_pagebreak, is_heading, is_italic)] per paragraph, document order."""
    x = zipfile.ZipFile(docx).read("word/document.xml").decode("utf8")
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, flags=re.S):
        t = "".join(m or "\t" for m in re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>|<w:tab/>", p, flags=re.S))
        t = t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        bullet = ("w:numPr" in p) or ("ListBullet" in p)
        heading = (not bullet) and ("<w:b/>" in p) and ('<w:u w:val="single"' in p) and len(t.split()) <= 6
        out.append((t, bullet, "w:br w:type=\"page\"" in p, heading, "<w:i/>" in p))
    return out


def hits(text, phrases, rxs=()):
    found = [b for b in phrases if b.lower() in text.lower()]
    found += [rx for rx in rxs if re.search(rx, text)]
    return found


def split_pages(paras):
    """(page1, page2) at the first explicit page break."""
    i = next((i for i, r in enumerate(paras) if r[2]), len(paras))
    return paras[:i], paras[i:]


def structure(paras):
    """-> dict of structural facts, computed the same way for any docx."""
    page1, _ = split_pages(paras)
    texts = [t for t, *_ in page1]
    courses = next((t for t in texts if t.startswith("Relevant courses")), "")
    first_heading = next((i for i, r in enumerate(page1) if r[3]), len(page1))
    contact = [t for t, b, _, h, _ in page1[:first_heading] if t.strip() and not h]
    skills_i = next((i for i, r in enumerate(page1) if r[3] and "skills" in r[0].lower()), None)
    prose_in_skills = []
    if skills_i is not None:
        for t, b, _, h, it in page1[skills_i + 1:]:
            if h: break
            if t.strip() and not b: prose_in_skills.append(t[:60])
    return {
        "availability_in_courses": "Available" in courses,
        "term_in_contact_block": any("available" in t.lower() and "co-op" in t.lower() for t in contact)
                                  or any("term" in t.lower() for t in contact),
        "prose_in_skills": prose_in_skills,
    }


def numbers(paras):
    """Every number token per page (for the no-restated-numbers probe); years excluded."""
    toks = set()
    for t, *_ in paras:
        toks |= {n.rstrip(",") for n in NUM.findall(t.replace(PHONE, ""))}
    return {n for n in toks if not NUM_YEAR.match(n)}


def probe_one_line(paras):
    """Every bullet except Technical Skills lines renders on one line; skill lines on at most two."""
    bad, in_skills = [], False
    for t, b, _, h, _ in paras:
        if h: in_skills = "skills" in t.lower()
        if not b: continue
        lines = template.rendered_lines(t)
        if lines is None: return ["width unmeasured (PIL/Calibri missing)"]
        if lines > (2 if in_skills else 1): bad.append("%d lines: %s" % (lines, t[:50]))
    return bad


def probe_no_restated_numbers(paras):
    p1, p2 = split_pages(paras)
    return sorted(numbers(p1) & numbers(p2))


def probe_headings(paras):
    p1, p2 = split_pages(paras)
    h1 = {t for t, _, _, h, _ in p1 if h}; h2 = {t for t, _, _, h, _ in p2 if h}
    out = []
    if h1 != P1_HEADINGS: out.append("page 1 headings %s" % sorted(h1))
    if h2 != P2_HEADINGS: out.append("page 2 headings %s" % sorted(h2))
    return out


def probe_rendered_split(pdf):
    """Rendered PDF: exactly 2 pages; a page-2 heading must not land on page 1 and vice versa."""
    import fitz
    with fitz.open(pdf) as f:
        if f.page_count != 2: return ["rendered pages = %d" % f.page_count]
        p1, p2 = f[0].get_text(), f[1].get_text()
    out = []
    for h in P2_HEADINGS:
        if h in p1: out.append("page 1 contains a page-2 heading (reflow?): %s" % h)
    for h in P1_HEADINGS:
        if h in p2: out.append("page 2 contains a page-1 heading (spillover?): %s" % h)
    return out


def pdf_links(pdf):
    """Every external URI annotation in the PDF, or None if PyMuPDF is missing."""
    try:
        import fitz
    except ImportError:
        return None
    uris = []
    with fitz.open(pdf) as f:
        for page in f:
            uris += [l.get("uri") for l in page.get_links() if l.get("uri")]
    return uris


# ---------------------------------------------------------------- probes

def probe_jargon(paras):
    """JARGON over Highlights + project bullets, i.e. everything except inside Technical Skills."""
    bad, in_skills = [], False
    for t, b, _, h, _ in paras:
        if h: in_skills = "skills" in t.lower()
        if in_skills: continue
        found = hits(t, JARGON)
        if found: bad.append("%s: %s" % (found, t[:60]))
    return bad


def probe_budgets(paras):
    p1, p2 = split_pages(paras)
    p1_bullet_words = sum(len(t.split()) for t, b, *_ in p1 if b)
    p2_words = sum(len(t.split()) for t, *_ in p2)
    out = []
    if p1_bullet_words > 600: out.append("page 1 bullet words %d > 600" % p1_bullet_words)
    if p2_words > 130: out.append("page 2 words %d > 130" % p2_words)
    return out


def probe_pdf_pages(pdf):
    import fitz
    with fitz.open(pdf) as f:
        n = f.page_count
    return [] if n == 2 else ["rendered pages = %d" % n]


def expected_links(text):
    return {"https://" + m for m in URL_RX.findall(text)}


def probe_links(text, pdf):
    uris = pdf_links(pdf)
    if uris is None:
        return ["PyMuPDF missing, links unchecked"]
    uris = {u.rstrip("/") for u in uris}
    missing = sorted(expected_links(text) - uris)
    return ["not clickable in PDF: %s" % missing] if missing else []


def claim_numbers_in(text):
    """Every claim-style number in text: PHONE and the LinkedIn profile id stripped first, years
    excluded."""
    text = text.replace(PHONE, " ").replace(LINKEDIN_ID, " ")
    out = []
    for m in LEDGER_NUMBER.finditer(text):
        tok = m.group(0)
        if LEDGER_YEAR.match(tok.replace(",", "")):
            continue
        out.append(tok)
    return out


def unbacked_numbers(paras):
    """Every number in every paragraph that traces to no CLAIMS-EVIDENCE-LEDGER.md row."""
    ledger_text = LEDGER.read_text(encoding="utf-8")
    ledger_nums = set(claim_numbers_in(ledger_text))
    ledger_nums |= {n.replace(",", "") for n in ledger_nums}
    out = []
    for t, *_ in paras:
        if not t.strip(): continue
        for num in claim_numbers_in(t):
            if num in ledger_nums or num.replace(",", "") in ledger_nums:
                continue
            out.append((num, t.strip()[:160]))
    return out


# ---------------------------------------------------------------- gate

def run_probes(docx, pdf):
    """-> {name: findings-list}. pdf may be None/missing: pdf-only probes report NOT CHECKED."""
    paras = paragraphs(docx)
    text = "\n".join(t for t, *_ in paras)
    findings = {}
    findings["banned"] = hits(text, BANNED, BANNED_RX)
    findings["cert"] = hits(text, CERT_BANNED)
    findings["required"] = [r for r in REQUIRED if r not in text]
    findings["jargon"] = probe_jargon(paras)
    s = structure(paras)
    st = []
    if s["availability_in_courses"]: st.append("availability still in the courses line")
    if not s["term_in_contact_block"]: st.append("term line not in the contact block")
    if s["prose_in_skills"]: st.append("prose paragraph inside Technical Skills: %s" % s["prose_in_skills"])
    findings["structure"] = st
    findings["one_line_bullets"] = probe_one_line(paras)
    findings["no_restated_numbers"] = probe_no_restated_numbers(paras)
    findings["heading_sets"] = probe_headings(paras)
    t_findings, _ = template.audit(docx)
    findings["template"] = t_findings
    findings["budgets"] = probe_budgets(paras)
    findings["unbacked_numbers"] = unbacked_numbers(paras)
    if pdf and Path(pdf).exists():
        findings["pdf_pages"] = probe_pdf_pages(pdf)
        findings["rendered_split"] = probe_rendered_split(pdf)
        findings["links"] = probe_links(text, pdf)
    else:
        findings["pdf_pages"] = ["NOT CHECKED (no PDF)"]
        findings["rendered_split"] = ["NOT CHECKED (no PDF)"]
        findings["links"] = ["NOT CHECKED (no PDF)"]
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx")
    ap.add_argument("--pdf", help="default: <docx> with .pdf suffix")
    ap.add_argument("--previous", help="older docx; probes that fired on it but pass now are listed")
    ap.add_argument("--old", help="negative control docx; default: none (control reported UNPROVEN)")
    ap.add_argument("--no-pdf", action="store_true", help="skip the PDF-only probes instead of failing closed")
    args = ap.parse_args()

    docx = Path(args.docx)
    pdf = Path(args.pdf) if args.pdf else docx.with_suffix(".pdf")

    fails = []

    print("== probes:", docx)
    probes = run_probes(docx, pdf)
    for name, f in probes.items():
        if args.no_pdf and name in ("pdf_pages", "rendered_split", "links") and not pdf.exists():
            print("  %-18s SKIPPED (--no-pdf)" % name)
            continue
        print("  %-18s %s" % (name, f or "ok"))
        if f: fails.append(name)
    if not pdf.exists() and not args.no_pdf:
        print("PDF: NOT CHECKED (%s missing) - fails closed; pass --no-pdf to skip instead" % pdf)
        if "pdf_missing" not in fails: fails.append("pdf_missing")

    if args.old:
        old = Path(args.old)
        print("== negative control --old:", old)
        old_probes = run_probes(old, None)
        old_fail_count = sum(1 for f in old_probes.values() if f)
        print("  %d/%d probes fire on --old" % (old_fail_count, len(old_probes)))
        if old_fail_count < 5:
            print("GATE INERT: fewer than 5 probes fire on --old, this gate is not checking anything")
            fails.append("gate_inert")
    else:
        print("== negative control --old: UNPROVEN (not given) - provide an older/weaker resume docx to prove this gate isn't inert")

    if args.previous:
        prev = Path(args.previous)
        print("== regression check --previous:", prev)
        prev_probes = run_probes(prev, None)
        fired_on_previous = [name for name in probes if prev_probes.get(name) and not probes[name]]
        if fired_on_previous:
            print("  fired on previous, passes now:", fired_on_previous)
        else:
            print("  WARNING: no probe differs between --previous and the new docx")

    print("RESULT:", "PASS" if not fails else "FAIL " + " | ".join(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
