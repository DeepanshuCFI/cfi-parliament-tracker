# Page build: template.html → index.html

`site/index.html` is **generated**. Never edit it by hand — edit `site/template.html`
and rebuild:

```
python3 pipeline/build_page.py            # data/dataset.json + data/enrich.json → site/index.html
python3 pipeline/build_page.py --dataset X --enrich Y --template T --out O   # all optional
```

Stdlib-only, Python 3.12. Exits non-zero with a clear message on any failure.
If `data/enrich.json` is missing, the build bootstraps it once by extracting the
inline `const ENRICH` from the current `site/index.html`, writes it to
`data/enrich.json`, then proceeds.

## Placeholders (byte-exact, replaced wholesale)

| Placeholder    | Source                        | Occurrences |
|----------------|-------------------------------|-------------|
| `__FONT__`     | `site/assets/mont.b64`        | 1 (Montserrat @font-face) |
| `__GEIST__`    | `site/assets/geist.b64`       | 1 (Geist @font-face) |
| `__LOGOBLUE__` | `site/assets/logo_blue.b64`   | 2 (header + footer logo) |
| `__DATA__`     | dataset file, compact JSON    | 1 (`const DATA = __DATA__;`) |
| `__ENRICH__`   | enrich file, compact JSON     | 1 (`const ENRICH = __ENRICH__;`) |

`</` inside the JSON is escaped to `<\/` so it can never close the `<script>` block.

## `{{TOKENS}}` (build-computed, no-JS fallback text)

All computed from the dataset/enrich in `compute_tokens()`. The page JS
(`applyDynamicNumbers()` in the template) recomputes the same values at load —
**the two implementations must stay in lockstep**; the tokens are what
crawlers/no-JS readers see.

`TOTAL` (1,423) · `NEVER` (never-asked MPs, from `enrich.neverTotal`) ·
`SITTING` (`enrich.sittingLS18`) · `HITRUN` / `DRUNK` / `PED` (tag counts by tag
name) · `UNSTARRED_PCT` · `UNSTARRED_N` / `UNSTARRED_RAW` · `STARRED` /
`STARRED_RAW` (formatted vs bare, bare feeds CSS `flex:`) · `START_MY` ("July 2014") ·
`DATA_THROUGH_MY` ("July 2026", from max record date) · `PERIOD` ("Jul 2014 – Jul 2026") ·
`YEAR_LEAD` (record-year narrative sentence) · `RECORD_YEAR` · `CHART_NOTE` ·
`ASKED_MPS` · `LS_N` / `RS_N` · `PDF_NOTE` · `WITH_PDF` · `VERSION`
(`dataset.version`) · `CITE_YEAR` (year of max record date).

Number formatting uses Indian grouping (`toLocaleString('en-IN')` equivalent).
The build asserts every token in the template is one it computes, and that the
output contains no leftover `__X__` or `{{X}}`.

## `DATA.session` contract (ongoing-session strip)

Optional top-level key in `data/dataset.json`:

```json
"session": {
  "label": "Monsoon Session 2026",   // display name (uppercased in eyebrow)
  "start": "2026-07-20",             // YYYY-MM-DD, inclusive
  "end":   "2026-08-13",             // YYYY-MM-DD, inclusive
  "sittings": 19,                    // optional; omitted from copy if absent
  "ls_lk": "18",                     // Lok Sabha number  (matches record r.l)
  "ls_session": "8",                 // LS session number (matches record r.s)
  "rs_session": "271"                // RS session number (matches record r.s)
}
```

A record belongs to the session iff
`(r.h=='LS' && r.l==ls_lk && r.s==ls_session) || (r.h=='RS' && r.s==rs_session)`
(string-compared, so numbers or strings both work). `start` and `end` are
required — without both the strip stays hidden.

### Strip behaviour

| State | Behaviour |
|---|---|
| No `DATA.session` | Section stays `hidden`; `?session=current` in the URL is ignored and stripped. Fully backward compatible. |
| Upcoming (client date before `start`) | Eyebrow "NEXT SESSION · <LABEL>", no pulse dot; headline "Parliament convenes <start day>."; lead "<date range> · <sittings> sittings. The <label> opens <start day>; road-safety questions will appear here from the first answer day." Stats, recent list, CTA and zero-state all stay hidden. |
| Live (client date within start…end), records > 0 | Eyebrow "LIVE · <LABEL>" with pulsing brand-blue dot (animation disabled under `prefers-reduced-motion`), count + LS·RS split + latest answer date, 5 most recent titles linked to their PDFs (`target=_blank rel=noopener`), CTA "See all questions from this session". |
| Live, 0 records | Same eyebrow/dot; honest zero-state copy ("The session opened 20 July… the tracker checks daily"); stats, list and CTA hidden. |
| After `end` | Eyebrow "LATEST SESSION · <LABEL>", no pulse; stats + recent list + CTA if records exist, otherwise a plain "no road-safety questions" line. |

The CTA (and `?session=current` deep links) set a real `session` filter in the
explorer, shown as a removable pill ("Session: Monsoon Session 2026 ✕")
alongside the existing MP/ministry/state/year pills.

## `ENRICH.rsDir` contract (Rajya Sabha layer of the #state section)

The #state section has a Lok Sabha / Rajya Sabha toggle. Everything RS-side —
hemicycle (241 dots), legend, vacant-seat caption, member picker, verdict card,
and the "Rajya Sabha: k members · j never asked" line in the state panel — is
computed **client-side from `ENRICH.rsDir` at load**; no RS number is baked into
the template or into build tokens (`build_page.py` needed no changes). Refining
`data/enrich.json` and rebuilding is therefore sufficient to update every RS
figure on the page.

Shape the page JS depends on (per state key, incl. `"Nominated"`):

```json
"rsDir": { "West Bengal": [
  { "mp":  "Sagarika Ghose",  // display name; also the ?rsm= deep-link value
    "p":   "AITC",            // party, rendered verbatim (short abbrev expected)
    "n":   3,                 // int; 0 = never asked (any term, either House)
    "ds":  "Sagarika Ghose",  // dataset MP name for the explorer filter; "" = no
                              //    records -> "See their questions" is hidden
    "exp": "2030" }           // term-end year, shown in the card footnote
] }
```

Client-side computations: members = Σ|rsDir[state]| (must equal `rsSitting`);
never = count of `n === 0` (must equal `rsNeverTotal` — `sanity_check.py`
enforces both); asked = members − never; vacant = 245 − members. Deep link:
`?rss=<State>&rsm=<mp>` (mutually exclusive with the LS `?pcs`/`?pc` pair).
RS members have **no constituency** — they sit for a whole state, so the card
prints `<State> · Rajya Sabha` where the LS card prints a constituency.

They **do** have photos. `/mpimg/` proxies both houses via `site/vercel.json`,
which keeps images same-origin under the CSP:

| House | `img` value | rewritten to |
|---|---|---|
| LS | DMS uuid | `getFile/dms/fetch/<uuid>?source=dsp2` |
| RS | `rs/P<mpsno>.jpg` | `getFile/newmembers/photos/P<mpsno>.jpg?source=rajyasabha` |

RS needs no uuid lookup — the filename is the member number. `fetch_rs_photos.py`
stamps `img` onto `rsDir` from `api_rs/member/sitting-members` (falling back to
`roster.json`, whose mpsno coverage is better: the live list dropped a sitting
member). It is **not** in the daily workflow — re-run it when the House turns
over. `--verify` GETs every photo and drops any that doesn't return an image, so
a dead id never ships; sansad answers HEAD with 403, so the check must use GET.
A missing or failed photo falls back to the initials disc via `photoFail()` — on
the LS card, the RS card and the shared asker modal alike.

Two layers of checking, deliberately split:

- `sanity_check.py` runs **daily** and guards coverage (≥90% per house) and id
  shape. Cheap, no network.
- `verify_photos.py` is **on demand** and GETs every id in both houses
  (`--ls` / `--rs` to narrow). Read-only, exits nonzero on any failure.
  Reachability is deliberately *not* in the daily gate: ~780 requests to sansad
  per run, and any upstream hiccup would block a publish over cosmetics.

Last full audit: 781/781 reachable (540 LS + 241 RS).

## Name resolution and the homonym guard

`build_enrich.name_tokens()` drops honorifics **and single-letter initials**, so
an asker's key is their surname plus full given names only. Distinct members
therefore collapse onto one key — C.R. Chaudhary (Rajasthan), P P Chaudhary
(Rajasthan) and R K Chaudhary (Uttar Pradesh) are all `('chaudhary',)`. The
roster has 64 such keys whose colliders disagree on state.

Resolution order and its guards:

1. `data/mp_enrichment.csv` (hand-verified, `mp_name_in_dataset` → official /
   state / party). Always wins; this is the override for any collision.
2. `data/roster.json`, first-token-set-wins, **LS before RS** — but a key whose
   colliders disagree on state is refused outright (`AMBIGUOUS`). Same-state
   collisions keep first-wins: those are one member listed in both houses
   (`C M Ramesh` / `Ramesh, Dr. C.M.`, both Andhra Pradesh).
3. Otherwise unresolved → `enrich_report.json` for the manual pass.

Two further guards, because the never-asked stat renders from three sources that
must agree (`neverTotal`, `mpDir` red dots, per-state `never`): the never-list
removal requires the never-list entry's **state to equal the resolved state**,
and the `mpDir` fallback match requires a **unique** unstamped candidate (the
same rule the RS path uses). Without them a repeat asker can evict a namesake
from the never list — the count drops with no red dot to flip, and
`sanity_check.py` fails the run rather than publish the three disagreeing.

## Idempotence guarantee

The build is a pure function of (template, assets, dataset, enrich): running it
twice yields byte-identical output (verified by SHA-256). Built-in checks: the
inline `DATA` in the output must JSON-round-trip **equal** to the input dataset,
`const DATA =` / `const ENRICH =` each appear exactly once, and no placeholder
or token survives. Rebuilding with unchanged data reproduces the live page's
behaviour exactly.
