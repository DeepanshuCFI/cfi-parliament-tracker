#!/usr/bin/env python3
"""Apply an editor-curated HISTORICAL backfill to the dataset. MANUAL only.

The daily pipeline only ever ingests the current session. Records for earlier
sessions (a newly tracked ministry, questions an audit found missing) come in
through here instead:

    python3 pipeline/apply_backfill.py data/backfill/<file>.json
    python3 pipeline/build_enrich.py && python3 pipeline/publish.py \
        && python3 pipeline/build_page.py && python3 pipeline/sanity_check.py

Backfill file: {"source": "<who decided, when>", "note": "...",
                "records": [{h, l, s, q, t, d, m, j, u, min}, ...]}

What it does, idempotently:
  - appends each record not already present to data/dataset.json
  - seals an include decision in data/curation_decisions.json (source as given)
  - lists the record key in data/backfill_keys.json, which is what lets
    build_enrich.py fold a non-current-session record into the MP statistics

Names are canonicalised and topics tagged exactly as delta_refresh.py does, so
a backfilled record is indistinguishable from one the daily run ingested.
Nothing here is published until the usual build + sanity gate + deploy.
"""
import csv
import re
import sys

from common import (DATA, MIN_FULL, tag_for, clean_mp, record_key, load_json, save_json)


def safe_u(u):
    u = (u or '').strip()
    return u if u.startswith('http://') or u.startswith('https://') else ''


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec = load_json(sys.argv[1])
    if not spec or not spec.get('records') or not spec.get('source'):
        sys.exit('backfill file needs "source" and a non-empty "records" list')

    merges = {}
    with open(DATA / 'name_merges.csv') as f:
        for row in csv.DictReader(f):
            merges[row['variant_merged']] = row['canonical_name']

    dataset = load_json(DATA / 'dataset.json')
    decisions = load_json(DATA / 'curation_decisions.json', {})
    backfill = load_json(DATA / 'backfill_keys.json', [])
    existing = {record_key(r) for r in dataset['records']}

    added = already = 0
    for raw in spec['records']:
        if raw.get('min') not in MIN_FULL:
            sys.exit(f"unknown ministry {raw.get('min')!r} in {raw.get('j')!r}")
        if raw.get('h') not in ('LS', 'RS') or not raw.get('s') or not raw.get('q') or not raw.get('j'):
            sys.exit(f'malformed record: {raw}')
        if raw.get('d') and not re.match(r'^\d{4}-\d{2}-\d{2}$', raw['d']):
            sys.exit(f"bad date {raw['d']!r} in {raw['j']!r}")
        title = raw['j'].strip()
        rec = {'h': raw['h'], 'l': str(raw.get('l') or ''), 's': str(raw['s']), 'q': str(raw['q']),
               't': 'S' if raw.get('t') == 'S' else 'U', 'd': raw.get('d') or '',
               'm': [merges.get(n, n) for n in (clean_mp(m) for m in raw.get('m', []) if m)],
               'j': title, 'g': tag_for(title, raw['min']), 'u': safe_u(raw.get('u')), 'min': raw['min']}
        k = record_key(rec)
        decisions[k] = {'include': True, 'title': title, 'ministry': rec['min'], 'source': spec['source']}
        if k in existing:
            already += 1
            continue
        dataset['records'].append(rec)
        existing.add(k)
        added += 1
        if k not in backfill:
            backfill.append(k)

    dataset['records'].sort(key=lambda r: r['d'] or '0', reverse=True)
    save_json(DATA / 'dataset.json', dataset, compact=True)
    save_json(DATA / 'curation_decisions.json', decisions)
    save_json(DATA / 'backfill_keys.json', sorted(backfill))
    print(f"apply_backfill: {added} added, {already} already present "
          f"({len(dataset['records'])} records now) - source: {spec['source']}")


if __name__ == '__main__':
    main()
