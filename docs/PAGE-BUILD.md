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
RS members have **no constituency and no photo** — the card uses a two-letter
initials avatar and never fetches `/mpimg/`.

## Idempotence guarantee

The build is a pure function of (template, assets, dataset, enrich): running it
twice yields byte-identical output (verified by SHA-256). Built-in checks: the
inline `DATA` in the output must JSON-round-trip **equal** to the input dataset,
`const DATA =` / `const ENRICH =` each appear exactly once, and no placeholder
or token survives. Rebuilding with unchanged data reproduces the live page's
behaviour exactly.
