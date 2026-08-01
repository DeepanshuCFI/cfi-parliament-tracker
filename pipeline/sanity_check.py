#!/usr/bin/env python3
"""Publish gate: refuse to deploy a dataset or page that regressed.

The fetch layer swallows network errors (a failed session pull just yields
fewer rows), so this is the step that turns silent partial data into a loud
CI failure. Exits nonzero -> workflow fails -> failure issue gets a comment.
"""
import re, sys
from common import DATA, SITE, load_json

errors = []

ds = load_json(DATA / 'dataset.json')
if not ds:
    errors.append('dataset.json missing/unparseable')
else:
    n = len(ds['records'])
    stats = load_json(DATA / 'stats.json', {})
    prev = stats.get('previous')
    if prev and n < prev:
        errors.append(f'record count regressed: {n} < previous {prev}')
    if n < 1415:
        errors.append(f'record count {n} below the v3.1 floor (1415)')
    for r in ds['records'][:2000]:
        if not (r.get('h') in ('LS', 'RS') and r.get('s') and r.get('q') and r.get('j')
                and r.get('min') in ds['ministries']):
            errors.append(f'malformed record: {r}'); break
        if r.get('d') and not re.match(r'^\d{4}-\d{2}-\d{2}$', r['d']):
            errors.append(f'bad date {r["d"]!r} in {r["j"]!r}'); break
    if not ds.get('session', {}).get('label'):
        errors.append('dataset.session block missing')

en = load_json(DATA / 'enrich.json')
if not en:
    errors.append('enrich.json missing/unparseable')
elif not (en.get('mpMeta') and en.get('states') and en.get('neverTotal')):
    errors.append('enrich.json missing required keys')
else:
    # The never-asked stat renders from THREE sources that must agree:
    # hero/og:title (neverTotal), hemicycle red dots (mpDir n==0), state cards
    hemi = sum(1 for members in en['mpDir'].values() for m in members if not m.get('n'))
    st_never = sum(s.get('never', 0) for s in en['states'].values())
    if not (en['neverTotal'] == hemi == st_never):
        errors.append(f"never-asked mismatch: neverTotal={en['neverTotal']} "
                      f"hemicycle={hemi} state-sum={st_never}")
    if ds and sum(en['minCounts'].values()) != len(ds['records']):
        errors.append(f"minCounts sum {sum(en['minCounts'].values())} != "
                      f"record count {len(ds['records'])} - enrichment drifted from dataset")
    if en.get('rsDir'):
        rs_n = sum(len(v) for v in en['rsDir'].values())
        rs_never = sum(1 for v in en['rsDir'].values() for m in v if not m.get('n'))
        if en.get('rsSitting') != rs_n:
            errors.append(f"rsSitting {en.get('rsSitting')} != rsDir member count {rs_n}")
        if en.get('rsNeverTotal') != rs_never:
            errors.append(f"rsNeverTotal {en.get('rsNeverTotal')} != rsDir n==0 count {rs_never}")

    # MP photo coverage. Photos are proxied per /mpimg/ (site/vercel.json), so a
    # malformed id renders a broken frame for a named person - check shape, and
    # hold coverage above a floor so a wiped img field is loud rather than a
    # gradual slide back to initials discs. The floor is proportional, not exact:
    # a newly sworn-in member with no photo yet must not fail the daily run.
    for house, dirname in (('LS', 'mpDir'), ('RS', 'rsDir')):
        entries = [m for v in (en.get(dirname) or {}).values() for m in v]
        if not entries:
            continue
        withimg = [m for m in entries if m.get('img')]
        if len(withimg) < 0.9 * len(entries):
            errors.append(f'{house} photo coverage {len(withimg)}/{len(entries)} '
                          f'below the 90% floor - did an img field get wiped?')
        bad = [m['mp'] for m in withimg
               if not re.fullmatch(r'rs/P\d+\.jpg|[0-9a-f-]{36}', str(m['img']))]
        if bad:
            errors.append(f'{house} malformed photo id on {len(bad)} entries: {bad[:3]}')

page = SITE / 'index.html'
if not page.exists():
    errors.append('site/index.html missing')
else:
    html = page.read_text()
    if html.count('const DATA') != 1:
        errors.append('site/index.html: const DATA count != 1')
    if re.search(r'__[A-Z]+__|\{\{[A-Z_]+\}\}', html):
        errors.append('site/index.html: unreplaced placeholders remain')
    if len(html) < 500_000:
        errors.append(f'site/index.html suspiciously small ({len(html)} bytes) - fonts/logo missing?')

report = load_json(DATA / 'refresh_report.json', {})
if len(report.get('api_failures', [])) >= 4:
    errors.append(f"most API pulls failed this run: {report['api_failures']}")

if errors:
    print('SANITY CHECK FAILED:')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print(f"sanity_check: OK ({len(ds['records'])} records, page {len(html)//1024} KB)")
sys.exit(0)
