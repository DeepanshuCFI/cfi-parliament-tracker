# Road Safety in Parliament — auto-refreshing tracker

Every road-safety question asked in the Lok Sabha and Rajya Sabha since 2014, across four
ministries (MoRTH, Health, Heavy Industries, Housing & Urban Affairs), refreshed **daily
during live sessions** by GitHub Actions and deployed to Vercel.

**Live:** https://road-safety-parliament.vercel.app (final home: crashfreeindia.org/parliament)
**RTI Watch:** https://road-safety-parliament.vercel.app/rti (static sibling page, deployed from `site/rti/`)

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
session list) and shouts in the job summary until you do.

## Human-review gates (check the job summary / failure issue)

- `data/curation_log.json` — LLM overrides of keyword verdicts + `needs_review` batches
- `data/enrich_report.json` — new askers whose names couldn't be matched to the official
  roster (add them to `data/mp_enrichment.csv`, then correct `data/enrich.json` counts)
- Failure issue **"Daily refresh FAILED"** — one reusable issue, commented per failure

## Manual operations

- **Full rebuild** (complete re-enumeration since 2014, tens of minutes):
  `python3 pipeline/full_rebuild.py` from repo root (env `RS_MAX_SESSION` bumps the RS
  ceiling; default 280). Output lands in `data/full_rebuild_output.json` for hand-merge.
- **Local run of the daily chain:**
  `cd pipeline && for s in delta_refresh curate build_enrich publish build_page sanity_check; do python3 $s.py || break; done`
  (run from repo root with `python3 pipeline/<step>.py` — paths are repo-relative)
- **Deploy by hand:** `cd site && npx vercel deploy --prod`

## Data notes

- Dataset floor is the hand-audited v3.1 (1,415 records, complete through 2026-04-02);
  `sanity_check.py` refuses any dataset smaller than that.
- Public copy always says "named/titled" — counts are title-based and a floor.
- Never-asked headline is ALL-TIME (287 at v3.1): an MP who asked in ANY term they served
  is not "never asked". Do not reintroduce the 367 per-term figure.
- `data/curation_decisions.json` remembers every include/exclude ever made, so rejected
  titles are not re-sent to the LLM on later runs.
