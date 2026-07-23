# Road Safety in Parliament — Codebook

**Version 3.1 (complete, cross-ministry) · Data through 2 April 2026 · License CC BY 4.0**
Cite as: *Crashfree India, Road Safety in Parliament (2026).*

## Files

- `road-safety-in-parliament_v3.1.csv` — one row per parliamentary question (1,415 rows)
- `road-safety-in-parliament_v3.1.json` — identical data as JSON, with version metadata

## Scope and selection

Road safety is answered by more than one ministry, so we enumerate every question — directly from Parliament's Lok Sabha and Rajya Sabha question APIs — put to the **four ministries that own it**: **Road Transport & Highways** (roads, vehicles, enforcement), **Health & Family Welfare** (trauma centres, ambulances, accident-victim care), **Heavy Industries** (vehicle crash standards), and **Housing & Urban Affairs** (urban pedestrian, footpath and non-motorised-transport safety), across the **16th–18th Lok Sabhas** and **Rajya Sabha sessions 232–270** (7 July 2014 – 2 April 2026). Of the full universe we retain the **1,415** whose **titles** concern road safety: accidents, fatalities, helmets, seat belts, drink/drunk driving, hit-and-run, pedestrians, black spots, trauma care, the Motor Vehicles Act & rules, road design & engineering, enforcement & licensing, vehicle safety standards, and related terms. Health and Heavy Industries use a road-safety-*context* filter (trauma/accident/ambulance; vehicle crashworthiness) so unrelated health or industry questions are excluded.

**Independently reconciled.** The original pass was an automated scrape of MoRTH alone; it was checked question-by-question against the official API and extended across the other two ministries: 0 spurious records, ~520 missed questions added. **Selection is title-based** — a question raising road safety under an unrelated title is not captured; treat counts as a near-complete floor, not an absolute ceiling. Ministry codes: LS `ministryCode` 55/32/9/60, RS `min_code` 65/32/45/110.

## Columns

| Column | Description |
|---|---|
| `ministry` | Answering ministry: Road Transport & Highways, Health & Family Welfare, Heavy Industries, or Housing & Urban Affairs. |
| `record_id` | Stable unique ID: `LS{lok_sabha}-S{session}-{type}{qno}` for Lok Sabha, `RS-S{session}-{type}{qno}` for Rajya Sabha. Type letter: S = starred, U = unstarred. Starred and unstarred questions have separate numbering series, so the type letter is required for uniqueness. |
| `house` | `LS` (Lok Sabha) or `RS` (Rajya Sabha) |
| `lok_sabha_no` | 16, 17 or 18 for LS records; empty for RS |
| `session` | Session number (LS: within that Lok Sabha; RS: continuous numbering 232–270) |
| `question_no` | Question number as printed |
| `type` | `Starred` (answered orally on the floor, supplementaries allowed) or `Unstarred` (written reply only) |
| `date` | Answer date, ISO `YYYY-MM-DD`. One record has no recoverable date (empty). |
| `mp_names` | Asking MP(s), `;`-separated. Honorifics stripped, casing normalised, and 10 documented name-variant pairs merged (see `name_merges_APPLIED.csv`). Joint questions are credited to every co-asking MP. Name normalisation is automated — spelling variants may persist; verify before publishing per-MP claims. |
| `subject` | Question title as printed on sansad.in |
| `topic_tags` | One or more of the 12 topic tags below, `;`-separated |
| `answer_pdf_url` | Official answer PDF on sansad.in. 38 records (mostly pre-2019) have no retrievable PDF (empty). |

## Topic tags (12)

Assigned from the question title; a question can carry multiple tags.

| Tag | Count |
|---|---|
| Accidents & Fatalities | 637 |
| Trauma Care & Compensation | 304 |
| Road Safety (General) | 249 |
| Road Safety Policy | 108 |
| Enforcement & Licensing | 102 |
| Vehicle Safety Standards | 87 |
| Black Spots & Infrastructure | 84 |
| Motor Vehicles Act & Rules | 68 |
| Data & Reporting | 36 |
| Pedestrian Safety | 34 |
| Drunk/Drink Driving | 15 |
| Hit and Run | 4 |

## Known caveats

1. Title-based selection undercounts; body-text mentions are not captured.
2. MP name normalisation is automated; the same person may still appear under spelling variants. The dataset has 833 distinct MP name strings; a handful of MPs served in both Houses (e.g. one known cross-House name-variant pair), so the count of individuals is approximately 830.
3. A couple of records lack a date; 38 records lack PDFs (legacy formats on sansad.in).
4. Fatality-share comparisons quoted in Crashfree India materials come from MoRTH, *Road Accidents in India 2023*, not from this dataset.

## Refresh policy

The dataset is refreshed after every parliamentary session. Each release increments the version and states its data-through date; cite the version you used.

## MP enrichment (`mp_enrichment_SANSAD.csv`)

Each distinct MP name in the dataset is matched to the **official sansad.in member roster** — the Lok Sabha member API (`/api_ls/member`, 16th–18th LS) and the Rajya Sabha all-members API (`/api_rs/member/sitting-members`) — yielding the member's official name, party, state, constituency (LS) and `mpsno`. Matching uses exact, token-order-insensitive, subset/initials, Gujarati `-bhai` suffix, and conservative fuzzy tiers, with Lok Sabha candidates disambiguated by whether the term they asked in overlaps a term they served. 836 of 839 rows are high/medium confidence; the `source` column records `sansad.in` vs the single `wikipedia-fallback` row (one member not resolvable via the API). Verify the single `needs_review` row before publishing per-MP claims.

## Contact

Crashfree India (Vision Zero Trust) · crashfreeindia.org
