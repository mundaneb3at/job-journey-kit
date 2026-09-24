"""Assert a resume .docx follows a career-advisor template's STRUCTURE, not just its words.

Why this exists: a checker that only greps for the literal string "Highlights" passes on a
document that has the word in a sentence, has its sections in the wrong order, opens with a prose
summary paragraph, or runs to four pages. The complaint that motivated this file was structural,
not lexical ("we don't need paragraphs, we need a bullet-point setup") - and no plain word-grep
could have caught it.

The rules below are meant to be read out of YOUR OWN advisor template (edit TEMPLATE_ORDER,
FORBIDDEN_SECTIONS and the Highlights bullet-count checks in audit() to match it):
  - Highlights (or your template's equivalent opening section) is the FIRST section.
  - There is no Summary / Profile / Objective section anywhere in the template.
  - Section order matches TEMPLATE_ORDER below.
  - The template's own page-count and one-line-per-bullet guidance.

It checks STRUCTURE, not truth. A number or claim can be wrong and still pass here; that is a job
for a separate claims/evidence check. What this catches is the drift case: a resume that stops
looking like the thing the advisor handed over.

Run:  python verify-template.py <resume.docx>   -> report, exit 1 if non-compliant
      python verify-template.py --test          -> self-check + negative control (needs fixtures)
"""
import re
import sys
import zipfile
from pathlib import Path

NS_T = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
NS_P = re.compile(r"<w:p\b.*?</w:p>", re.S)

# Section headings in the order YOUR template presents them. Optional ones may be absent, but any
# that IS present must not appear out of order. Edit this list to match your own template.
TEMPLATE_ORDER = [
    "highlights",
    "education",
    "skills",
    "technical work experience",
    "technical projects",
    "work experience",
    "certifications",
    "trainings",
    "awards",
    "volunteer",
    "additional experience",
    "references",
]
# Sections your template does not contain at all. A resume that has one has drifted back to the
# paragraph-summary shape a bullet-first format replaces.
FORBIDDEN_SECTIONS = ["summary", "profile", "objective", "about me"]

MAX_PAGES = 2

# Bullet line width, measured the same way make-resume.py measures it (installed Calibri metrics
# at the template's body size) rather than guessed from a word count.
BASE_PT = 10
BULLET_W_PT = 512.7


def text_width_pt(text, size=BASE_PT, bold=False):
    """Rendered width in points using the installed Calibri; None if PIL or the font is missing."""
    try:
        from PIL import ImageFont
        path = r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"
        return ImageFont.truetype(path, 100).getlength(text) / 100 * size
    except Exception:
        return None


def rendered_lines(text):
    """How many lines this bullet occupies, or None if the font could not be measured."""
    w = text_width_pt(text)
    return None if w is None else max(1, -(-int(w) // int(BULLET_W_PT)))


def paragraphs(docx_path):
    """[(is_bullet, is_heading, text)] for every non-empty paragraph, in document order."""
    xml = zipfile.ZipFile(docx_path).read("word/document.xml").decode("utf-8")
    out = []
    for m in NS_P.finditer(xml):
        blk = m.group(0)
        text = "".join(NS_T.findall(blk))
        text = (
            text.replace("&amp;", "&").replace("&quot;", '"')
            .replace("&lt;", "<").replace("&gt;", ">")
            .replace("&#8217;", "\u2019")
        )
        text = text.strip()
        if not text:
            continue
        # Bullets: python-docx's "List Bullet" style, Word's numbered list markup, or a literal
        # glyph. All three must count.
        style = re.search(r'<w:pStyle w:val="([^"]+)"', blk)
        style = style.group(1) if style else ""
        bullet = (
            "<w:numPr>" in blk
            or style.startswith(("ListBullet", "ListParagraph"))
            or text.startswith(("\u2022", "\u00b7 "))
        )
        # Section headings are short, bold, and either underlined or ALL CAPS. Accepting both is
        # what lets a negative control be judged on its structure instead of passing for lack of
        # detection.
        bold = "<w:b/>" in blk or "<w:b " in blk
        underlined = "<w:u " in blk
        allcaps = text == text.upper() and any(c.isalpha() for c in text)
        heading = (
            (not bullet) and bold and (underlined or allcaps)
            and len(text.split()) <= 6 and not text.endswith(".")
        )
        out.append((bullet, heading, text))
    return out


def page_count(docx_path):
    """Pages: the larger of app.xml's count and 1 + explicit page breaks.

    Taking the max matters: python-docx ships a default app.xml that says <Pages>1</Pages> and
    never updates it, so trusting app.xml alone silently reports a document with a real page 2 as
    one page.
    """
    z = zipfile.ZipFile(docx_path)
    declared = 0
    if "docProps/app.xml" in z.namelist():
        m = re.search(r"<Pages>(\d+)</Pages>", z.read("docProps/app.xml").decode("utf-8"))
        if m:
            declared = int(m.group(1))
    xml = z.read("word/document.xml").decode("utf-8")
    # ponytail: explicit breaks only - a document that overflows onto another page purely by
    # reflow is not counted. Render to PDF and count pages there if that case starts mattering.
    from_breaks = 1 + len(re.findall(r'w:type="page"', xml))
    return max(declared, from_breaks)


def audit(docx_path):
    """-> (findings, info). findings is a list of strings; empty means compliant."""
    paras = paragraphs(docx_path)
    findings = []
    info = {}

    # The name line is bold and sits above every section, so it would otherwise read as the first
    # heading. The name/contact block is the first two non-bullet paragraphs by convention.
    name_block = [i for i, (b, h, t) in enumerate(paras) if not b][:2]
    headings = [(i, t) for i, (b, h, t) in enumerate(paras) if h and i not in name_block]
    info["headings"] = [t for _, t in headings]
    info["name_block"] = [paras[i][2][:40] for i in name_block]

    def find_heading(name):
        for i, t in headings:
            if name in t.lower():
                return i
        return None

    # 1. Highlights exists, is a real section heading, and is the first section.
    hi = find_heading("highlights")
    if hi is None:
        findings.append(
            "NO HIGHLIGHTS SECTION. The template opens with Highlights ('In 2 or 3 bullet "
            "points'); this resume has no such heading."
        )
    elif headings and headings[0][0] != hi:
        findings.append(
            "HIGHLIGHTS IS NOT THE FIRST SECTION. First heading is %r." % headings[0][1]
        )

    # 2. Nothing but the name/contact block may precede the first section, and none of it may be
    #    prose. This is the exact defect this file exists to catch: an opening summary paragraph.
    #    Checked against the first section heading, NOT against Highlights - a resume with no
    #    Highlights section at all is precisely the one most likely to have the paragraph.
    first_section = headings[0][0] if headings else len(paras)
    preamble = [t for (b, h, t) in paras[:first_section] if not h]
    for t in preamble[2:]:  # first two non-headings are name + contact line
        if len(t.split()) > 12:
            findings.append(
                "PROSE PARAGRAPH BEFORE THE FIRST SECTION (%d words): %r... The template has no "
                "summary/profile/objective paragraph - that content belongs in Highlights bullets."
                % (len(t.split()), t[:80])
            )

    # 3. Highlights content: 2-3 bullets, one line each.
    if hi is not None:
        nxt = next((i for i, _ in headings if i > hi), len(paras))
        body = paras[hi + 1:nxt]
        bullets = [t for (b, h, t) in body if b]
        nonbullets = [t for (b, h, t) in body if not b and not h]
        if not bullets:
            findings.append(
                "HIGHLIGHTS HAS NO BULLETS (%d non-bullet lines). Template: 'In 2 or 3 bullet "
                "points'." % len(nonbullets)
            )
        elif not 2 <= len(bullets) <= 3:
            findings.append(
                "HIGHLIGHTS HAS %d BULLETS, template says 2 or 3." % len(bullets)
            )
        for t in bullets:
            lines = rendered_lines(t)
            if lines is None:
                info["width_unmeasured"] = True
            elif lines > 1:
                findings.append(
                    "HIGHLIGHT BULLET WRAPS TO %d LINES (%d pt > %d pt at 10pt Calibri), "
                    "template says one: %r"
                    % (lines, round(text_width_pt(t)), BULLET_W_PT, t[:70])
                )
        info["highlight_bullets"] = len(bullets)

    # 4. No section the template does not have.
    for bad in FORBIDDEN_SECTIONS:
        j = find_heading(bad)
        if j is not None:
            findings.append(
                "SECTION %r IS NOT IN THE TEMPLATE. A bullet-first format replaces it with "
                "Highlights bullets." % paras[j][2]
            )

    # 5. Present sections appear in template order.
    seen = [(i, TEMPLATE_ORDER.index(k)) for k in TEMPLATE_ORDER
            for i, t in headings if k in t.lower()]
    seen.sort()
    ranks = [r for _, r in seen]
    if ranks != sorted(ranks):
        order = [paras[i][2] for i, _ in seen]
        findings.append("SECTIONS OUT OF TEMPLATE ORDER: %s" % " -> ".join(order))

    # 6. Page count.
    pages = page_count(docx_path)
    info["pages"] = pages
    if pages > MAX_PAGES:
        findings.append("%d PAGES; the template says no more than %d." % (pages, MAX_PAGES))

    return findings, info


def _test():
    """Self-check against fixture files, plus a negative control that must fail.

    The kit ships no fixtures (they'd be someone's real resume drafts). Point FIXTURE_GOOD /
    FIXTURE_BAD at your own docx files - a compliant one and a known-non-compliant one - to run
    this. Without them, --test skips cleanly rather than failing.
    """
    here = Path(__file__).parent
    good = here / "FIXTURE-good.docx"
    bad = here / "FIXTURE-bad.docx"

    if not good.exists() or not bad.exists():
        print("no fixtures: skipped (expected %s and %s)" % (good.name, bad.name))
        return 0

    f, info = audit(good)
    print("SELF-CHECK good fixture: %d finding(s), %d highlight bullets, %d page(s)"
          % (len(f), info.get("highlight_bullets", 0), info["pages"]))
    for x in f:
        print("   -", x)
    assert not f, "good fixture should be compliant"

    # Negative control: a known non-compliant fixture. If this ever passes, the checker has
    # stopped checking.
    f2, _ = audit(bad)
    assert f2, "NEGATIVE CONTROL PASSED - the checker is not checking anything"
    print("NEGATIVE CONTROL: %d finding(s) on %s (expected)" % (len(f2), bad.name))
    print("\nSELF-TEST PASS")
    return 0


def main():
    args = sys.argv[1:]
    if args and args[0] == "--test":
        return _test()
    if not args or args[0] in ("--help", "-h"):
        print(__doc__.strip().splitlines()[-2].strip())
        return 0 if args and args[0] in ("--help", "-h") else 2
    target = Path(args[0])
    if not target.exists():
        print("FAIL - no such file: %s" % target)
        return 1
    findings, info = audit(target)
    print("%s - %d page(s), %d section(s): %s"
          % (target.name, info["pages"], len(info["headings"]), ", ".join(info["headings"])))
    if not findings:
        print("\nPASS - follows the template structure")
        return 0
    print("\nFAIL - %d template deviation(s):" % len(findings))
    for x in findings:
        print("  * %s" % x)
    return 1


if __name__ == "__main__":
    sys.exit(main())
