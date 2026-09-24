r"""Content constants for a resume: name, contact, links, term line, Education, Highlights,
Skills, Technical Projects, Jobs, Additional Projects, Extracurricular - every string an employer
reads. Layout (measurements, python-docx helpers, build/render) lives in `tools\make-resume.py`,
which imports this file; nothing here writes a docx. Every number below needs a row in
`CLAIMS-EVIDENCE-LEDGER.md` (checked by `tools\verify-resume.py`). Don't hand-edit the produced
`.docx`/`.pdf` - edit this file and rerun the producer instead, or your gate and your resume will
silently drift apart.

Copy this file to `resume-content.py` at your kit-user root and replace every <bracket> and every
placeholder number/claim with your own, real, ledger-backed facts.
"""

NAME = "<Your Display Name>"
LINKEDIN = "linkedin.com/in/<your-handle>"
GITHUB = "github.com/<your-handle>"
PORTFOLIO = "<your-handle>.github.io"
LINKS = (LINKEDIN, GITHUB, PORTFOLIO)   # header links line, in this order

CONTACT_LINE = "<Your City, Province/State> | <your email> | <phone>"
# Role + term on one short contact-block line (<= 12 words: verify-template.py reads a longer
# non-bullet line before the first section as a summary paragraph, which this format forbids).
TERM_LINE = "<Role> co-op, available <term>, start by <date>, <your region> or remote"
P2_HEADER_CONTACT = "\t<phone> | <your email>"   # template p2 header, right-tabbed

# (title, rest, date) for the Education entry() call.
EDUCATION = (
    "<Degree>, <University>",
    " (<intended major>)",
    "expected <grad year>",
)

HIGHLIGHTS = [
    "<One line: the kind of work you do and how, e.g. what you build and who directs it.>",
    "<One line: a concrete result with a real number, backed by a CLAIMS-EVIDENCE-LEDGER.md row.>",
    "<One line: a third concrete result - public repos, tests passing, something checkable.>",
]

SKILLS = [
    ("AI-directed code: ",
     "the projects below were written by AI coding agents under my direction; I set the design, "
     "the tests and what counts as done, then check the result by running it, watching what it "
     "does and pushing edge cases at it"),
    ("Programming: ",
     "<languages, frameworks and tools you actually read, run and test - be specific>"),
    ("Still learning: ", "<skills you're honestly still building, named plainly>"),
]

# (title, one-line purpose, repo link, date, bullets). Technologies sit inside the bullets.
PROJECTS = [
    ("<Project One Name>", "<a one-line purpose in plain words>",
     "github.com/<your-handle>/<project-one>", "<year>", [
        "<Bullet 1: what it does and the one number that proves it, backed by the ledger.>",
        "<Bullet 2: how you verified it - tests, a check, a rerun - and when.>",
     ]),
    ("<Project Two Name>", "<a one-line purpose in plain words>",
     "github.com/<your-handle>/<project-two>", "<year>", [
        "<Bullet 1: what it does and the one number that proves it, backed by the ledger.>",
        "<Bullet 2: how you verified it - tests, a check, a rerun - and when.>",
     ]),
]

JOBS = [
    ("<Job Title>", ", <Employer>, <City>", "<Month Year> - <Month Year>",
     "<One line on what you did, kept honest and specific.>"),
]

# (title, repo link, date, one bullet).
EXTRA_PROJECTS = [
    ("<Smaller Project Name>", "github.com/<your-handle>/<smaller-project>", "<year>",
     "<One bullet: what it is and one checkable fact about it.>"),
]

EXTRACURRICULAR = "<Role>, <Organization> (<one fact, e.g. member count or year>)"
