#!/usr/bin/env python3
"""Incrementally update the ENRICH blob (states rollup, MP metadata, hemicycle
never-asked counts, constituency directory) with current-session records.

The blob in data/enrich.json was originally computed from the full dataset
through Apr 2026 (v3.1). Rather than re-derive it from scratch (the original
assembly was never scripted), this applies exact per-record increments for NEW
current-session records, tracked idempotently in data/enrich_state.json.

A new asker whose name has no entry in mp_enrichment.csv cannot be mapped to a
state/party/never-list entry automatically; they are flagged in
data/enrich_report.json for a manual matching pass (same human-gate philosophy
as the SC litigation tracker).
"""
import csv, re, sys
from common import DATA, SITE, TAGS, load_json, save_json, record_key

dataset = load_json(DATA / 'dataset.json')
enrich = load_json(DATA / 'enrich.json')
if enrich is None:
    print('build_enrich: data/enrich.json missing - run build_page.py once to bootstrap it from the live page')
    sys.exit(1)
state = load_json(DATA / 'enrich_state.json', {'counted_keys': []})
counted = set(state['counted_keys'])
cur = dataset.get('session') or {}

# dataset-name -> (official_name, state, party) from the hand-verified enrichment table
name_map = {}
with open(DATA / 'mp_enrichment.csv') as f:
    for row in csv.DictReader(f):
        name_map[row['mp_name_in_dataset']] = (row['official_name'], row['state'], row['party'])

# Fallback: the official sansad roster, which stores names comma-flipped with
# honorifics ("Kumar, Shri Mithlesh"). Normalising to a sorted token set matches
# those against dataset-form names without a fuzzy pass.
HON_TOK = {'shri', 'smt', 'dr', 'prof', 'kumari', 'km', 'sardar', 'adv', 'ms', 'mr',
           'mrs', 'sushri', 'shrimata', 'shrimati', 'thiru', 'justice', 'col', 'capt', 'maj', 'gen'}
def name_tokens(s):
    toks = re.findall(r'[a-z]+', (s or '').lower())
    return tuple(sorted(t for t in toks if t not in HON_TOK and len(t) > 1))

roster_map = {}
roster = load_json(DATA / 'roster.json', {})
for house_key in ('rs', 'ls'):
    for m in roster.get(house_key, []):
        k = name_tokens(m.get('name'))
        if k and k not in roster_map:
            roster_map[k] = (m.get('name', ''), m.get('state', ''), m.get('party', ''))

def resolve(name):
    """(official_name, state, party) or (None, '', '') when unresolvable."""
    if name in name_map:
        return name_map[name]
    hit = roster_map.get(name_tokens(name))
    return hit if hit else (None, '', '')

# official never-asked list (LS18); membership here drives the red hemicycle dots
never = load_json(DATA / 'never_official.json')
if never is None:
    with open(DATA / 'never_asked.csv') as f:
        rows = list(csv.DictReader(f))
    never = {r['mp_name_official']: r['state'] for r in rows}

def in_session(r):
    return ((r['h'] == 'LS' and r['l'] == cur.get('ls_lk') and r['s'] == cur.get('ls_session'))
            or (r['h'] == 'RS' and r['s'] == cur.get('rs_session')))

new = [r for r in dataset['records'] if in_session(r) and record_key(r) not in counted]
unmatched, removed_from_never = [], []

for r in new:
    yr = int(r['d'][:4]) if r['d'] else None
    enrich['minCounts'][r['min']] = enrich['minCounts'].get(r['min'], 0) + 1
    for name in r['m']:
        meta = enrich['mpMeta'].get(name)
        if meta:
            meta[2] += 1
            if yr:  # blob may store years as strings - compare numerically, keep int
                meta[3] = min(int(meta[3]), yr) if meta[3] else yr
                meta[4] = max(int(meta[4]), yr) if meta[4] else yr
            st = meta[0]
        else:
            official, st, party = resolve(name)
            enrich['mpMeta'][name] = [st, party, 1, yr, yr]
            if official is None:
                unmatched.append({'name': name, 'house': r['h'], 'title': r['j']})
        if st and st in enrich['states']:
            enrich['states'][st]['total'] = enrich['states'][st].get('total', 0) + 1
        # never-asked -> asked transition (LS only; the headline stat)
        official = resolve(name)[0]
        if r['h'] == 'LS' and official and official in never:
            nst = never.pop(official)
            removed_from_never.append({'official': official, 'dataset_name': name, 'state': nst})
            enrich['neverTotal'] = max(0, enrich['neverTotal'] - 1)
            if nst in enrich['states'] and 'never' in enrich['states'][nst]:
                enrich['states'][nst]['never'] = max(0, enrich['states'][nst]['never'] - 1)
        # constituency directory (LS18 sitting members): bump count + year range
        if st:
            for entry in enrich['mpDir'].get(st, []):
                if entry.get('ds') == name:
                    entry['n'] = entry.get('n', 0) + 1
                    if yr and entry.get('y'):
                        entry['y'] = [min(entry['y'][0], yr), max(entry['y'][1], yr)] \
                            if isinstance(entry['y'], list) else entry['y']
                    break
    counted.add(record_key(r))

# recompute each state's top-asker list from mpMeta (keep existing list length)
for st, s in enrich['states'].items():
    if 'top' in s and s['top']:
        k = len(s['top'])
        ranked = sorted(((n, m[2], m[1]) for n, m in enrich['mpMeta'].items() if m[0] == st),
                        key=lambda x: -x[1])[:k]
        s['top'] = [[n, c, p] for n, c, p in ranked]

save_json(DATA / 'enrich.json', enrich, compact=True)
save_json(DATA / 'never_official.json', never)
save_json(DATA / 'enrich_state.json', {'counted_keys': sorted(counted)})
save_json(DATA / 'enrich_report.json', {'new_records_applied': len(new),
                                        'unmatched_new_askers': unmatched,
                                        'left_never_asked_list': removed_from_never})
print(f'build_enrich: applied {len(new)} new records | never-asked now {enrich["neverTotal"]} '
      f'| unmatched new askers: {len(unmatched)}')
if removed_from_never:
    for x in removed_from_never:
        print(f"  STORY: {x['official']} ({x['state']}) asked their FIRST road-safety question")
sys.exit(0)
