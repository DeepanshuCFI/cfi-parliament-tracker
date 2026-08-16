# Road Safety in Parliament — auto-refreshing tracker

Every road-safety question asked in the Lok Sabha and Rajya Sabha since 2014, across four
ministries (MoRTH, Health, Heavy Industries, Housing & Urban Affairs), refreshed **daily
during live sessions** by GitHub Actions and deployed to Vercel.

**Live:** https://parliament.crashfreeindia.org (road-safety-parliament.vercel.app is the underlying Vercel deployment)
**RTI Watch:** archived to `archive/rti-watch/` ahead of launch (OCR figures pending a human verification pass); `/rti` redirects to the home page

A Crashfree India (Vision Zero Trust) public dataset. License: CC BY 4.0.

## How the daily refresh works

```
delta_refresh.py   pull ONLY the current session (sessions.json) from the official APIs
                   LS: sansad.in qetFilteredQuestionsAns (param is sessionNumber, NOT sessionNo)
                   RS: rsdoc.nic.in Search_Questions (one call per ministry, unpaginated)
                   -> stages new titles with keyword-filter verdicts
curate.py          Claude Haiku reviews every new title against the approved inclusion scope
                   (keyword verdict as prior). HARD BUDGET CAP ~INR 100/month tracked in
                   data/curation_state.json; over-cap or API failure -> keyword-only + needs_review.
build_enrich.py    incremental update of the page's ENRICH blob: MP counts, state rollups,
                   never-asked hemicycle (an MP asking their FIRST question is logged as a story)
publish.py         name merges, meta (data_through), session block, public CSV export
build_page.py      inject DATA + ENRICH + fonts/logo into site/template.html -> site/index.html
sanity_check.py    publish gate: record count must never regress; no leftover placeholders
commit + deploy    commit-back with GITHUB_TOKEN; `npx vercel deploy --prod` from site/
```

Off-session, the daily run is a cheap no-op (no new questions -> no LLM call, no commit).

## Repo secrets (Settings → Secrets → Actions)

| Secret | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Haiku curation of new titles (optional — pipeline degrades to keyword-only) |
| `VERCEL_TOKEN` | Deploy (create at vercel.com/account/tokens) |
| `VERCEL_ORG_ID` | From `site/.vercel/project.json` after `vercel link` (team crashfreeindia) |
| `VERCEL_PROJECT_ID` | Same file — project `road-safety-parliament` |

Verify with the manual **Check secrets** workflow. Public repo = unlimited free Actions minutes.

## Session rollover ritual (3× a year)

When a new session is notified (Budget/Monsoon/Winter), edit `data/sessions.json`:
move `current` into `history`, set the new `current` (label, dates, sittings, LS/RS
session numbers). The pipeline detects rollover on its own (probes RS N+1 and the LS
session list) and files/comments a **"Tracker needs attention"** GitHub issue daily
until you do. The same issue fires when any API source fails 3+ consecutive runs.

**When the 19th Lok Sabha begins** (post-general-election): beyond sessions.json,
the enrichment layer needs structural work — `data/enrich.json`'s mpDir/hemicycle
and never-asked list are LS18-specific (new 540-member roster, fresh never list,
new mpDir with photos). Plan a session for it; do not let the daily refresh run
LS19 records through the LS18 enrichment.

## Human-review gates (check the job summary / failure issue)

- `data/curation_log.json` — LLM overrides of keyword verdicts + `needs_review` batches.
  Degraded (keyword-only) runs seal only their INCLUDES; excludes re-stage the next day
  for a real review, so nothing is permanently mis-filed by a bad day.
- `data/enrich_report.json` → `unresolved_askers_outstanding` — askers whose names can't
  be matched to the roster. They stay on this list (and in every job summary) until you
  add a row to `data/mp_enrichment.csv`; the pipeline then heals their state/party
  automatically on the next run (`healed_this_run`).
- Issue **"Daily refresh FAILED"** — pipeline/deploy failures, commented per failure
- Issue **"Tracker needs attention"** — session rollover needed, or an API source
  failing 3+ consecutive runs (fires daily until fixed)

## Manual operations

- **Full rebuild** (complete re-enumeration since 2014, tens of minutes):
  `python3 pipeline/full_rebuild.py` from repo root (env `RS_MAX_SESSION` bumps the RS
  ceiling; default 280). Output lands in `data/full_rebuild_output.json` for hand-merge.
- **Local run of the daily chain:**
  `cd pipeline && for s in delta_refresh curate build_enrich publish build_page sanity_check; do python3 $s.py || break; done`
  (run from repo root with `python3 pipeline/<step>.py` — paths are repo-relative)
- **Deploy by hand:** `cd site && npx vercel deploy --prod`
- **Regenerate the OG share image** (evergreen — no numbers/dates, edit copy in `site/assets/og-card-src.html` first if needed, fonts are embedded):
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --screenshot=site/og-card.png --window-size=1200,630 --hide-scrollbars "file://$PWD/site/assets/og-card-src.html"` from repo root

## Data notes

- Dataset floor is the hand-audited v3.1 (1,415 records, complete through 2026-04-02);
  `sanity_check.py` refuses any dataset smaller than that.
- Public copy always says "named/titled" — counts are title-based and a floor.
- Never-asked headline is ALL-TIME (287 at v3.1): an MP who asked in ANY term they served
  is not "never asked". Do not reintroduce the 367 per-term figure.
- `data/curation_decisions.json` remembers every include/exclude ever made, so rejected
  titles are not re-sent to the LLM on later runs.
