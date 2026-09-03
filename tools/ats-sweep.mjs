#!/usr/bin/env node
/**
 * ats-sweep.mjs - deterministic live-ness + eligibility sweep across ATS board APIs.
 *
 * WHY THIS EXISTS
 * ---------------
 * An LLM research pass once produced job rows that were wrong three times out of five: a deadline
 * off by a week, roles asserted "apply now" that were closed, terms labelled Fall that were Winter.
 * Root cause: it treated an HTTP 200 from a job URL as proof the job was open. Ashby/Greenhouse/
 * Lever/Workday job pages are JavaScript apps - they return 200 for dead postings. This tool
 * removes the model from that judgement: a posting is LIVE iff the employer's own board API still
 * returns it, and eligibility text is sliced verbatim from the API response.
 *
 * USAGE
 *   node ats-sweep.mjs --selfcheck              prove the tool works before trusting a run
 *   node ats-sweep.mjs                          sweep SLUGS below -> sweep-<date>.{json,md}
 *   node ats-sweep.mjs --slugs more-slugs.json  sweep a discovered slug list
 *   node ats-sweep.mjs --all                    no filtering; dump every posting per board
 *
 * A slug file is JSON: [{"platform":"ashby","slug":"cohere"}, {"platform":"lever","slug":"acme"}]
 * Needs Node 18+ (built-in fetch). No dependencies.
 *
 * EDIT THESE FOR YOURSELF: SLUGS, JUNIOR, REGION, NOT_REGION, EXCLUDE, STRENGTH_TERMS.
 */

const TODAY = new Date().toISOString().slice(0, 10);
const UA = { "User-Agent": "Mozilla/5.0 (compatible; job-sweep/1.0)" };

// ponytail: slugs live here, not in a config file - one file, one place to edit.
const SLUGS = [
  { platform: "ashby", slug: "cohere" },
  { platform: "ashby", slug: "1password" },
];

// Titles you can plausibly clear. Edit to your level.
const JUNIOR = /intern|co-?op|new ?grad|junior|student|entry[- ]level|associate|apprentice|assistant/i;
// Where you can legally work. Eligibility and remoteness are SEPARATE questions: a "remote" posting
// from a company with no hiring entity in your country is not a job you can take, so `remote` is
// deliberately NOT in this list. Default = Canada; replace with your own country/provinces/cities.
const REGION = /canada|canadian|ontario|british columbia|\bbc\b|vancouver|victoria|burnaby|richmond|surrey|toronto|ottawa|montr|quebec|calgary|edmonton|winnipeg|halifax|saskat|manitoba|alberta|nova scotia|new brunswick/i;
// Locations that, if named, positively exclude you.
const NOT_REGION = /united states|\busa\b|\bus only\b|san francisco|new york|seattle|austin|boston|chicago|denver|mountain view|palo alto|london|berlin|paris|amsterdam|dublin|singapore|sydney|bangalore|india\b|brazil|mexico|poland|romania|bulgaria|latvia|estonia|sweden/i;
// Hard exclusion you cannot clear; reported per row so a human sees what was dropped.
const EXCLUDE = /\bph\.?d\b|doctoral/i;

const ELIGIBILITY_HEAD = /(qualification|requirement|what you.{0,3}ll bring|what we.{0,3}re looking for|who you are|about you|you (?:will )?have|minimum|eligib|basic qualif|skills? (?:and|&) experience)/i;

// ---------------------------------------------------------------- fetchers

async function getJSON(url) {
  const r = await fetch(url, { headers: UA });
  if (!r.ok) return { ok: false, status: r.status, data: null };
  try { return { ok: true, status: r.status, data: await r.json() }; }
  catch { return { ok: false, status: r.status, data: null }; }
}

/** Each adapter returns a normalized posting array, or null if the board does not resolve. */
const ADAPTERS = {
  async ashby(slug) {
    const { ok, data } = await getJSON("https://api.ashbyhq.com/posting-api/job-board/" + slug + "?includeCompensation=true");
    if (!ok || !data || !data.jobs) return null;
    return data.jobs.map(j => ({
      id: j.id, title: j.title, location: j.location,
      secondary: (j.secondaryLocations || []).map(s => s.location).join("; "),
      employmentType: j.employmentType, isRemote: j.isRemote, workplaceType: j.workplaceType,
      publishedAt: j.publishedAt, applyUrl: j.applyUrl || j.jobUrl, text: j.descriptionPlain || "",
      compensation: (j.compensation && j.compensation.compensationTierSummary) || "",
    }));
  },
  async lever(slug) {
    const { ok, data } = await getJSON("https://api.lever.co/v0/postings/" + slug + "?mode=json");
    if (!ok || !Array.isArray(data)) return null;
    return data.map(j => ({
      id: j.id, title: j.text,
      location: (j.categories && j.categories.location) || "",
      secondary: (j.categories && j.categories.allLocations ? j.categories.allLocations.join("; ") : ""),
      employmentType: (j.categories && j.categories.commitment) || "",
      isRemote: /remote/i.test(j.workplaceType || (j.categories && j.categories.location) || ""),
      workplaceType: j.workplaceType || "",
      publishedAt: j.createdAt ? new Date(j.createdAt).toISOString() : "",
      applyUrl: j.applyUrl || j.hostedUrl,
      text: j.descriptionPlain || j.description || "",
      compensation: j.salaryRange ? JSON.stringify(j.salaryRange) : "",
    }));
  },
  async greenhouse(slug) {
    const { ok, data } = await getJSON("https://boards-api.greenhouse.io/v1/boards/" + slug + "/jobs?content=true");
    if (!ok || !data || !data.jobs) return null;
    return data.jobs.map(j => ({
      id: String(j.id), title: j.title, location: (j.location && j.location.name) || "", secondary: "",
      employmentType: "", isRemote: /remote/i.test((j.location && j.location.name) || ""), workplaceType: "",
      publishedAt: j.updated_at || "", applyUrl: j.absolute_url,
      text: (j.content || "").replace(/<[^>]+>/g, " ").replace(/&[a-z]+;/g, " "), compensation: "",
    }));
  },
  async workable(slug) {
    const { ok, data } = await getJSON("https://apply.workable.com/api/v1/widget/accounts/" + slug + "?details=true");
    if (!ok || !data || !data.jobs) return null;
    return data.jobs.map(j => ({
      id: j.shortcode, title: j.title,
      location: [j.city, j.state, j.country].filter(Boolean).join(", "), secondary: "",
      employmentType: j.type || "", isRemote: !!j.telecommuting, workplaceType: j.telecommuting ? "Remote" : "",
      publishedAt: j.published_on || "", applyUrl: j.application_url || j.url,
      text: [j.description, j.requirements].filter(Boolean).join("\n").replace(/<[^>]+>/g, " "), compensation: "",
    }));
  },
  async recruitee(slug) {
    const { ok, data } = await getJSON("https://" + slug + ".recruitee.com/api/offers/");
    if (!ok || !data || !data.offers) return null;
    return data.offers.map(j => ({
      id: String(j.id), title: j.title, location: [j.city, j.country].filter(Boolean).join(", "), secondary: "",
      employmentType: j.employment_type_code || "", isRemote: /remote/i.test(j.remote || j.location || ""),
      workplaceType: j.remote || "", publishedAt: j.published_at || "", applyUrl: j.careers_url,
      text: (j.description || "") + "\n" + (j.requirements || ""), compensation: "",
    }));
  },
};


// ---------------------------------------------------------------- the actual constraint
//
// The filter this encodes: "jobs that need my strength but don't need experience." A posting is a
// FIT when it asks for work you can already do and does NOT gate on time served. Everything here
// reads the posting's own words; nothing is inferred.

// "3+ years of experience", "minimum 2 years relevant experience", etc. Captures the number.
const YEARS_BAR = /(\d+)\s*\+?\s*(?:to\s*\d+\s*)?years?[^.\n]{0,40}?experience/ig;
// Gates that exclude an early-year student outright, regardless of skill.
// Includes "completed in 2025" / "graduated by 2026" phrasings - the original regex missed them and
// scored a new-grad-only posting WEAK-MATCH instead of BLOCKED (caught by a human read).
const YEAR_GATE = /final year|currently enrolled in (?:your |the )?final|recent(?:ly)? graduat|new ?grad(?:uate)? only|graduat(?:ing|ed?)\s+(?:by|in|before)\s+\w*\s*20\d\d|completed (?:in|by|before)\s+20\d\d|must have completed[^.\n]{0,40}(?:internship|degree)/i;
const DEGREE_GATE = /\b(?:master'?s|msc|m\.s\.|ph\.?d|doctoral|graduate degree)\b[^.\n]{0,80}?(?:required|is a must|only|must be|must have)/i;
// Language that explicitly opens the door to someone without a work history.
const NOVICE_WELCOME = /no (?:prior |technical |programming |relevant |)experience (?:is )?(?:required|necessary|needed)|through coursework|personal projects|class projects[^.\n]{0,25}count|we assess what you can make|don'?t meet every requirement|apply anyway|even if you (?:feel|do ?n'?o?t)|encourage you to apply|entry[- ]level|eager(?:ness)? to learn|growth mindset|willingness to learn|curious|first (?:co-?op|internship|role)/i;
// The work you can actually do today, evidenced by things you can show. EDIT THIS to your strengths.
const STRENGTH_TERMS = /\b(evaluation|eval|testing|test automation|QA|quality|verification|verify|reliability|automation|internal tool(?:ing|s)?|developer tool|documentation|provenance|traceab\w*|audit\w*|data quality|debugg?\w*|regression|CI\/CD|pipeline|search|retrieval|agent\w*|LLM|prompt\w*|python|javascript|typescript|node\.?js|sql|git|rest api|json)\b/ig;

/**
 * Score one posting against the constraint. Returns the numbers AND the sentence that produced
 * each verdict, so a human can disagree with the classifier instead of trusting it.
 */
function fitScore(text) {
  const t = text || "";
  let maxYears = 0, yearsQuote = "";
  YEARS_BAR.lastIndex = 0;
  let m;
  while ((m = YEARS_BAR.exec(t)) !== null) {
    const n = parseInt(m[1], 10);
    if (n > maxYears) { maxYears = n; yearsQuote = m[0].replace(/\s+/g, " ").trim(); }
  }
  const yg = t.match(YEAR_GATE), dg = t.match(DEGREE_GATE), nw = t.match(NOVICE_WELCOME);
  const strengths = [...new Set((t.match(STRENGTH_TERMS) || []).map(x => x.toLowerCase()))];

  let verdict;
  if (yg || dg || maxYears >= 3) verdict = "BLOCKED";
  else if (maxYears >= 1) verdict = "STRETCH";
  else if (strengths.length >= 4) verdict = "FIT";
  else verdict = "WEAK-MATCH";

  return {
    verdict, yearsRequired: maxYears, strengthHits: strengths.length,
    strengths: strengths.slice(0, 10),
    noviceWelcome: !!nw,
    why: [
      yg ? "YEAR GATE: " + yg[0].replace(/\s+/g, " ").trim().slice(0, 110) : "",
      dg ? "DEGREE GATE: " + dg[0].replace(/\s+/g, " ").trim().slice(0, 110) : "",
      yearsQuote ? "EXPERIENCE BAR: " + yearsQuote.slice(0, 110) : "",
      nw ? "WELCOMES A BEGINNER: " + nw[0].replace(/\s+/g, " ").trim().slice(0, 110) : "",
    ].filter(Boolean),
  };
}

// ---------------------------------------------------------------- extraction

/** Slice the eligibility/requirements block out of the posting body, verbatim. */
function eligibility(text, max = 1400) {
  if (!text) return "";
  const lines = text.split(/\r?\n/);
  const start = lines.findIndex(l => l.trim() && ELIGIBILITY_HEAD.test(l) && l.trim().length < 120);
  if (start === -1) return text.slice(0, max).trim();      // fall back to the head of the posting
  return lines.slice(start, start + 40).join("\n").slice(0, max).trim();
}

/**
 * `regionEvidence` is deliberately three-valued. A boolean silently promotes every remote posting
 * to eligible, which is how a foreign-remote role reaches your shortlist.
 *   EXPLICIT           - your region/province/city is named in the location fields.
 *   REMOTE-UNSPECIFIED - remote, but no country named. NOT eligibility. A human must confirm the
 *                        employer can actually pay someone where you live (entity, EOR, contractor).
 *   NO                 - a location outside your region is named.
 */
function classify(p) {
  const hay = p.title + " " + p.location + " " + p.secondary;
  const body = (p.text || "").slice(0, 6000);
  let regionEvidence;
  if (REGION.test(hay)) regionEvidence = "EXPLICIT";
  else if (REGION.test(body)) regionEvidence = "EXPLICIT";
  else if (p.isRemote || /remote|anywhere|distributed/i.test(hay)) regionEvidence = "REMOTE-UNSPECIFIED";
  else regionEvidence = "NO";

  if (regionEvidence !== "EXPLICIT" && NOT_REGION.test(hay)) regionEvidence = "NO";

  return {
    junior: JUNIOR.test(p.title),
    regionEvidence,
    region: regionEvidence !== "NO",   // kept wide so REMOTE-UNSPECIFIED rows still surface, flagged
    excluded: EXCLUDE.test((p.text || "").slice(0, 4000)),
  };
}

// ---------------------------------------------------------------- run

async function sweep(slugs, opts) {
  const all = !!(opts && opts.all);
  const boards = [], rows = [];
  for (const entry of slugs) {
    const platform = entry.platform, slug = entry.slug;
    const adapter = ADAPTERS[platform];
    if (!adapter) { boards.push({ platform, slug, status: "UNKNOWN-PLATFORM", jobs: 0, matches: 0 }); continue; }
    let postings = null;
    try { postings = await adapter(slug); } catch (e) { postings = null; }
    if (postings === null) { boards.push({ platform, slug, status: "NO-BOARD", jobs: 0, matches: 0 }); continue; }
    const matched = all ? postings : postings.filter(p => {
      const c = classify(p); return c.junior && c.region && !c.excluded;
    });
    boards.push({ platform, slug, status: "OK", jobs: postings.length, matches: matched.length });
    for (const p of matched) {
      rows.push(Object.assign({ platform, slug }, p, { eligibility: eligibility(p.text), _class: classify(p), fit: fitScore(p.text) }));
    }
  }
  const ORDER = { FIT: 0, STRETCH: 1, "WEAK-MATCH": 2, BLOCKED: 3 };
  const R_ORDER = { EXPLICIT: 0, "REMOTE-UNSPECIFIED": 1, NO: 2 };
  rows.sort((a, b) => (ORDER[a.fit.verdict] - ORDER[b.fit.verdict])
    || (R_ORDER[a._class.regionEvidence] - R_ORDER[b._class.regionEvidence])
    || (b.fit.strengthHits - a.fit.strengthHits));
  return { boards, rows };
}

function toMarkdown(result) {
  const boards = result.boards, rows = result.rows;
  const esc = s => String(s == null ? "" : s).replace(/\|/g, "\\|").replace(/\r?\n/g, "<br>");
  const okCount = boards.filter(b => b.status === "OK").length;
  const scanned = boards.reduce((a, b) => a + b.jobs, 0);
  let md = "# ATS sweep - " + TODAY + "\n\n";
  md += "Produced by `tools/ats-sweep.mjs`. **A row here is LIVE because the employer's own board API still returns it** - not because a URL responded. Eligibility text is sliced verbatim from the API's posting body; it is never summarized.\n\n";
  md += "Boards resolved: **" + okCount + "/" + boards.length + "** · postings scanned: **" + scanned + "** · matching rows: **" + rows.length + "**\n\n";
  const tally = rows.reduce((a, r) => { a[r.fit.verdict] = (a[r.fit.verdict] || 0) + 1; return a; }, {});
  md += "Fit tally: " + Object.entries(tally).map(e => "**" + e[0] + "** " + e[1]).join(" · ") + "\n\n";
  md += "**Region?** `yes` = your region is named. `**CONFIRM**` = remote with no country stated - **this is not eligibility**; confirm the employer can pay you where you live before applying. `no` = a location outside your region is named.\n\n`FIT` = asks for work you can already do and does **not** gate on years served. `STRETCH` = 1-2 years wanted. `BLOCKED` = a final-year / degree / 3+-years gate you cannot clear. Every verdict cites the posting sentence that produced it. **The classifier reads gate language, not technical depth - always apply a human pass.**\n\n";
  md += "## Verified-live rows\n\n| Fit | Region? | Yrs req | Beginner-friendly? | Company (slug) | Role | Location | Type / remote | Pay | Apply | Why this verdict | Eligibility - verbatim |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n";
  for (const r of rows) {
    md += "| **" + r.fit.verdict + "** | " + (r._class.regionEvidence === "EXPLICIT" ? "yes" : r._class.regionEvidence === "REMOTE-UNSPECIFIED" ? "**CONFIRM**" : "no") +
          " | " + (r.fit.yearsRequired || "0") + " | " + (r.fit.noviceWelcome ? "yes" : "-") +
          " | " + esc(r.slug) + " | " + esc(r.title) + " | " + esc(r.location) + (r.secondary ? " / " + esc(r.secondary) : "") +
          " | " + esc(r.employmentType) + (r.isRemote ? " · remote" : "") +
          " | " + (esc(r.compensation) || "not stated") +
          " | " + (r.applyUrl ? "[apply](" + r.applyUrl + ")" : "-") +
          " | " + esc(r.fit.why.join(" · ") || "no gate language found; matched " + r.fit.strengthHits + " strength terms") +
          " | " + esc(r.eligibility) + " |\n";
  }
  md += "\n## Board registry\n\n| Platform | Slug | Status | Postings | Matches |\n|---|---|---|---|---|\n";
  for (const b of boards) md += "| " + b.platform + " | " + b.slug + " | " + b.status + " | " + b.jobs + " | " + b.matches + " |\n";
  md += "\n`NO-BOARD` means the API did not resolve - a wrong slug, or the employer does not use that platform. It is **not** evidence the company isn't hiring.\n";
  return md;
}

// ---------------------------------------------------------------- self-check

/** Offline regression guards: pure-function checks that need no network. */
function offlineChecks() {
  const fails = [];
  const usOnly = classify({ title: "Software Engineer Intern", location: "San Francisco", secondary: "", text: "", isRemote: false });
  if (usOnly.regionEvidence !== "NO") fails.push("a San Francisco posting classified as " + usOnly.regionEvidence + " - the region/remote split is broken");
  const remoteOnly = classify({ title: "Engineer", location: "Remote", secondary: "", text: "", isRemote: true });
  if (remoteOnly.regionEvidence !== "REMOTE-UNSPECIFIED") fails.push("a bare remote posting classified as " + remoteOnly.regionEvidence + " - should be REMOTE-UNSPECIFIED, never eligibility");
  const local = classify({ title: "Co-op", location: "Vancouver, British Columbia, Canada", secondary: "", text: "", isRemote: false });
  if (local.regionEvidence !== "EXPLICIT") fails.push("an in-region posting did not classify as EXPLICIT");
  // Regression: the phrasing the original YEAR_GATE missed (a real new-grad posting scored WEAK-MATCH).
  const newGrad = fitScore("Bachelor's degree in Computer Science or a related field; completed in 2025. You will write tests.");
  if (newGrad.verdict !== "BLOCKED") fails.push("'completed in 2025' scored " + newGrad.verdict + " - YEAR_GATE regression");
  const gradBy = fitScore("Graduating by 2026 with a degree in engineering.");
  if (gradBy.verdict !== "BLOCKED") fails.push("'graduating by 2026' scored " + gradBy.verdict + " - YEAR_GATE regression");
  const open = fitScore("We welcome students at any year. You will work on testing, automation, documentation, and evaluation pipelines with python.");
  if (open.verdict !== "FIT") fails.push("an open, strength-matching posting scored " + open.verdict + " - FIT path broken");
  return fails;
}

/**
 * A broken run and a genuinely empty market both print zero rows. These assertions make the two
 * cases distinguishable before anyone rules on the output.
 */
async function selfcheck() {
  const fails = offlineChecks();

  const cohere = await ADAPTERS.ashby("cohere");
  if (!cohere || cohere.length === 0) fails.push("known-live board 'cohere' returned no postings - fetcher or endpoint is broken (or the company moved boards; pick another known-live slug)");

  const bogus = await ADAPTERS.ashby("definitely-not-a-real-company-xyzzy");
  if (bogus !== null) fails.push("a nonsense slug resolved - NO-BOARD detection is broken");

  const withText = (cohere || []).filter(p => p.text && p.text.length > 200).length;
  if (withText === 0) fails.push("no posting carried body text - eligibility extraction would silently return empty");

  const sample = (cohere || []).find(p => p.text && p.text.length > 500);
  if (sample && !eligibility(sample.text)) fails.push("eligibility() returned empty on a posting with a full body");

  if (fails.length) console.log("SELFCHECK FAIL\n - " + fails.join("\n - "));
  else console.log("SELFCHECK OK - offline regressions pass, fetcher live, dead-slug detection live, body text present");
  return fails.length === 0;
}

// ---------------------------------------------------------------- main

const argv = process.argv.slice(2);
const fs = await import("node:fs");

if (argv.includes("--selfcheck-offline")) {
  const fails = offlineChecks();
  console.log(fails.length ? "OFFLINE FAIL\n - " + fails.join("\n - ") : "OFFLINE OK - " + 6 + " regression checks pass");
  process.exit(fails.length ? 1 : 0);
}
if (argv.includes("--selfcheck")) {
  process.exit((await selfcheck()) ? 0 : 1);
}

let slugs = SLUGS;
const slugArg = argv.indexOf("--slugs");
if (slugArg !== -1 && argv[slugArg + 1]) {
  slugs = JSON.parse(fs.readFileSync(argv[slugArg + 1], "utf8"));
}

const result = await sweep(slugs, { all: argv.includes("--all") });
fs.writeFileSync("sweep-" + TODAY + ".json", JSON.stringify(result, null, 2), "utf8");
fs.writeFileSync("sweep-" + TODAY + ".md", toMarkdown(result), "utf8");
console.log("boards OK " + result.boards.filter(b => b.status === "OK").length + "/" + result.boards.length +
            " · postings " + result.boards.reduce((a, b) => a + b.jobs, 0) + " · rows " + result.rows.length);
console.log("WROTE sweep-" + TODAY + ".json and sweep-" + TODAY + ".md");
