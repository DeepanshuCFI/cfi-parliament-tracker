#!/usr/bin/env python3
"""Finalize the dataset for publication: apply MP name merges, refresh meta,
attach the current-session block, and export the public CSV.

Recreates the previously unscripted post-processing step that produced the
published v3.1 files (record IDs, name merges, meta, CSV expansion).
"""
import csv, sys
from common import DATA, SITE, TAGS, MIN_FULL, record_id, load_json, save_json

dataset = load_json(DATA / 'dataset.json')
sessions = load_json(DATA / 'sessions.json')

# ---- name merges (variant -> canonical, hand-curated) ----
merges = {}
with open(DATA / 'name_merges.csv') as f:
    for row in csv.DictReader(f):
        merges[row['variant_merged']] = row['canonical_name']
merged_n = 0
for r in dataset['records']:
    for i, m in enumerate(r['m']):
        if m in merges:
            r['m'][i] = merges[m]; merged_n += 1

# ---- meta ----
prev = load_json(DATA / 'stats.json', {})
dates = [r['d'] for r in dataset['records'] if r['d']]
dataset['version'] = '3.2'
dataset['data_through'] = max(dates) if dates else ''
dataset['license'] = 'CC BY 4.0'
dataset['citation'] = 'Crashfree India, Road Safety in Parliament (2026)'
dataset['ministries'] = MIN_FULL
dataset['tags'] = TAGS

# ---- current-session block (drives the site's ongoing-session strip) ----
cur = sessions['current']
dataset['session'] = {'label': cur['label'], 'start': cur['start'], 'end': cur['end'],
                      'sittings': cur['sittings'], 'ls_lk': cur['ls_lk'],
                      'ls_session': cur['ls_session'], 'rs_session': cur['rs_session']}

dataset['records'].sort(key=lambda r: r['d'] or '0', reverse=True)
save_json(DATA / 'dataset.json', dataset, compact=True)

# ---- public CSV (same column layout as the published v3.1 CSV) ----
def write_csv(path):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['record_id', 'ministry', 'house', 'lok_sabha_no', 'session', 'question_no',
                    'type', 'date', 'mp_names', 'subject', 'topic_tags', 'answer_pdf_url'])
        for r in dataset['records']:
            w.writerow([record_id(r), MIN_FULL[r['min']], r['h'], r['l'], r['s'], r['q'],
                        'Starred' if r['t'] == 'S' else 'Unstarred', r['d'], ';'.join(r['m']),
                        r['j'], ';'.join(TAGS[gi] for gi in r['g']), r['u']])

write_csv(DATA / 'road-safety-in-parliament.csv')
(SITE / 'data').mkdir(exist_ok=True)
write_csv(SITE / 'data' / 'road-safety-in-parliament.csv')

save_json(DATA / 'stats.json', {'records': len(dataset['records']),
                                'previous': prev.get('records'),
                                'data_through': dataset['data_through']})
print(f"publish: {len(dataset['records'])} records (prev {prev.get('records')}), "
      f"through {dataset['data_through']}, {merged_n} name-merge applications")
sys.exit(0)
