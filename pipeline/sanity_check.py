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
