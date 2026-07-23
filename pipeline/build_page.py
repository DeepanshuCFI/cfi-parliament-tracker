#!/usr/bin/env python3
"""Build site/index.html from site/template.html + data/dataset.json + data/enrich.json.

Stdlib only (Python 3.12). Run from repo root:  python3 pipeline/build_page.py
Optional:
  --dataset PATH   alternate dataset JSON (default data/dataset.json)
  --enrich PATH    alternate enrich JSON  (default data/enrich.json; bootstrapped
                   from the current site/index.html if the file does not exist)
  --template PATH  alternate template     (default site/template.html)
  --out PATH       alternate output       (default site/index.html)

Placeholders (byte-exact, replaced wholesale):
  __FONT__      Montserrat woff2 base64   <- site/assets/mont.b64
  __GEIST__     Geist woff2 base64        <- site/assets/geist.b64
  __LOGOBLUE__  CFI blue logo SVG base64  <- site/assets/logo_blue.b64  (2 occurrences)
  __DATA__      compact JSON of the whole dataset file (becomes const DATA)
  __ENRICH__    compact JSON of the enrich file        (becomes const ENRICH)

{{TOKENS}} are computed from the dataset/enrich (see compute_tokens). The same
values are recomputed client-side by applyDynamicNumbers() in the page JS; the
build-time text is the no-JS fallback, so the two copies must stay in lockstep.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MONTHS_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONTHS_FULL = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
               'August', 'September', 'October', 'November', 'December']


def die(msg: str) -> None:
    print(f"build_page: ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def fmt_in(n: int) -> str:
    """Indian-style digit grouping, matching JS toLocaleString('en-IN')."""
    s = str(int(n))
    neg = s.startswith('-')
    if neg:
        s = s[1:]
    if len(s) <= 3:
        return ('-' if neg else '') + s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ('-' if neg else '') + ','.join(parts + [tail])


def js_json(obj) -> str:
    """Compact JSON safe to inline inside a <script> block."""
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def bootstrap_enrich(enrich_path: Path) -> dict:
    """Extract ENRICH verbatim from the current live page and persist it."""
    live = ROOT / 'site' / 'index.html'
    if not live.exists():
        die(f"{enrich_path} missing and {live} not available to bootstrap from")
    html = live.read_text(encoding='utf-8')
    m = re.search(r'^const ENRICH = (\{.*\});$', html, re.M)
    if not m:
        die(f"{enrich_path} missing and no inline 'const ENRICH = {{...}};' found in {live}")
    try:
        enrich = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        die(f"inline ENRICH in {live} is not valid JSON: {e}")
    enrich_path.parent.mkdir(parents=True, exist_ok=True)
    enrich_path.write_text(js_json(enrich).replace('<\\/', '</'), encoding='utf-8')
    print(f"build_page: bootstrapped {enrich_path} from {live} ({len(enrich)} top-level keys)")
    return enrich


def tag_count(dataset: dict, tag_name: str) -> int:
    tags = dataset.get('tags', [])
    if tag_name not in tags:
        return 0
    idx = tags.index(tag_name)
    return sum(1 for r in dataset['records'] if idx in r.get('g', []))


def compute_tokens(dataset: dict, enrich: dict) -> dict:
    R = dataset.get('records')
    if not R:
        die("dataset has no records")
    total = len(R)
    dates = sorted(r['d'] for r in R if r.get('d'))
    if not dates:
        die("dataset has no dated records")
    dmin, dmax = dates[0], dates[-1]
    my_full = lambda d: f"{MONTHS_FULL[int(d[5:7]) - 1]} {d[:4]}"
    my_short = lambda d: f"{MONTHS_SHORT[int(d[5:7]) - 1]} {d[:4]}"

    unstarred = sum(1 for r in R if r.get('t') == 'U')
    starred = total - unstarred
    ls_n = sum(1 for r in R if r.get('h') == 'LS')
    rs_n = total - ls_n
    with_pdf = sum(1 for r in R if r.get('u'))
    no_pdf = total - with_pdf
    asked_mps = len({m for r in R for m in r.get('m', [])})

    # year narrative (must mirror applyDynamicNumbers in the template JS)
    yc: dict[str, int] = {}
    for r in R:
        if r.get('d'):
            yc[r['d'][:4]] = yc.get(r['d'][:4], 0) + 1
    years = sorted(yc)
    latest_y = years[-1]
    rec_y = years[0]
    for y in years:
        if yc[y] >= yc[rec_y]:
            rec_y = y
    m_full = MONTHS_FULL[int(dmax[5:7]) - 1]
    if rec_y == latest_y:
        year_lead = (f"Parliamentary attention to road safety reached {fmt_in(yc[rec_y])} questions "
                     f"in {rec_y} — a record — with data through {m_full}.")
    else:
        year_lead = (f"Parliamentary attention to road safety reached {fmt_in(yc[rec_y])} questions "
                     f"in {rec_y} — a record — and {latest_y} has already logged "
                     f"{fmt_in(yc[latest_y])} (through {m_full}).")

    undated = total - len(dates)
    chart_note = f"{latest_y} covers sessions up to {m_full}"
    if undated == 0:
        chart_note += "."
    elif undated == 1:
        chart_note += "; one undated question is excluded from the chart."
    else:
        chart_note += f"; {fmt_in(undated)} undated questions are excluded from the chart."

    if no_pdf == 0:
        pdf_note = "every record links to an answer PDF"
    else:
        all_pre2019 = all(r.get('u') or not r.get('d') or r['d'][:4] < '2019' for r in R)
        pdf_note = f"{fmt_in(no_pdf)} {'pre-2019 ' if all_pre2019 else ''}records survive only in legacy formats"

    return {
        'TOTAL': fmt_in(total),
        'NEVER': fmt_in(enrich.get('neverTotal', 0)),
        'SITTING': fmt_in(enrich.get('sittingLS18', 540)),
        'HITRUN': fmt_in(tag_count(dataset, 'Hit and Run')),
        'DRUNK': fmt_in(tag_count(dataset, 'Drunk/Drink Driving')),
        'PED': fmt_in(tag_count(dataset, 'Pedestrian Safety')),
        'UNSTARRED_PCT': str(round(unstarred / total * 100)),
        'UNSTARRED_N': fmt_in(unstarred),
        'UNSTARRED_RAW': str(unstarred),
        'STARRED': fmt_in(starred),
        'STARRED_RAW': str(starred),
        'START_MY': my_full(dmin),
        'DATA_THROUGH_MY': my_full(dmax),
        'PERIOD': f"{my_short(dmin)} – {my_short(dmax)}",
        'YEAR_LEAD': year_lead,
        'RECORD_YEAR': rec_y,
        'CHART_NOTE': chart_note,
        'ASKED_MPS': fmt_in(asked_mps),
        'LS_N': fmt_in(ls_n),
        'RS_N': fmt_in(rs_n),
        'PDF_NOTE': pdf_note,
        'WITH_PDF': fmt_in(with_pdf),
        'VERSION': str(dataset.get('version', '3.1')),
        'CITE_YEAR': dmax[:4],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--dataset', default=str(ROOT / 'data' / 'dataset.json'))
    ap.add_argument('--enrich', default=str(ROOT / 'data' / 'enrich.json'))
    ap.add_argument('--template', default=str(ROOT / 'site' / 'template.html'))
    ap.add_argument('--out', default=str(ROOT / 'site' / 'index.html'))
    args = ap.parse_args()

    template_path, dataset_path = Path(args.template), Path(args.dataset)
    enrich_path, out_path = Path(args.enrich), Path(args.out)

    if not template_path.exists():
        die(f"template not found: {template_path}")
    if not dataset_path.exists():
        die(f"dataset not found: {dataset_path}")
    html = template_path.read_text(encoding='utf-8')

    try:
        dataset = json.loads(dataset_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        die(f"{dataset_path} is not valid JSON: {e}")
    if enrich_path.exists():
        try:
            enrich = json.loads(enrich_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            die(f"{enrich_path} is not valid JSON: {e}")
    else:
        enrich = bootstrap_enrich(enrich_path)

    # ---- assets ----
    assets = {}
    for ph, fname in (('__FONT__', 'mont.b64'), ('__GEIST__', 'geist.b64'),
                      ('__LOGOBLUE__', 'logo_blue.b64')):
        p = ROOT / 'site' / 'assets' / fname
        if not p.exists():
            die(f"asset not found: {p}")
        assets[ph] = p.read_text(encoding='utf-8').strip()

    # ---- placeholder presence checks ----
    expected = {'__FONT__': 1, '__GEIST__': 1, '__LOGOBLUE__': 2, '__DATA__': 1, '__ENRICH__': 1}
    for ph, n in expected.items():
        got = html.count(ph)
        if got != n:
            die(f"template must contain {ph} exactly {n}x, found {got}")

    tokens = compute_tokens(dataset, enrich)
    in_template = set(re.findall(r'\{\{([A-Z_]+)\}\}', html))
    unknown = in_template - set(tokens)
    if unknown:
        die(f"template has tokens the build does not compute: {sorted(unknown)}")

    # ---- substitute ----
    for ph, blob in assets.items():
        html = html.replace(ph, blob)
    html = html.replace('__DATA__', js_json(dataset))
    html = html.replace('__ENRICH__', js_json(enrich))
    for tok, val in tokens.items():
        html = html.replace('{{' + tok + '}}', val)

    # ---- output assertions ----
    leftovers = sorted(set(re.findall(r'__[A-Z]+__|\{\{[A-Z_]+\}\}', html)))
    if leftovers:
        die(f"unreplaced placeholders/tokens remain in output: {leftovers}")
    if html.count('const DATA =') != 1:
        die(f"output must contain 'const DATA =' exactly once, found {html.count('const DATA =')}")
    if html.count('const ENRICH =') != 1:
        die(f"output must contain 'const ENRICH =' exactly once, found {html.count('const ENRICH =')}")

    # idempotence / integrity: DATA in the output must round-trip to the dataset
    m = re.search(r'^const DATA = (\{.*\});$', html, re.M)
    if not m:
        die("could not locate inline DATA in the built page")
    rebuilt = json.loads(m.group(1))
    if rebuilt != dataset:
        die("DATA embedded in the output does not round-trip to the input dataset")
    if len(rebuilt['records']) != len(dataset['records']):
        die("record count mismatch between output and dataset")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding='utf-8')
    sess = dataset.get('session')
    print(f"build_page: wrote {out_path} ({len(html):,} bytes) — "
          f"{len(dataset['records'])} records, data through {tokens['DATA_THROUGH_MY']}, "
          f"session strip: {'ACTIVE (' + str(sess.get('label')) + ')' if sess else 'hidden (no DATA.session)'}")


if __name__ == '__main__':
    main()
