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
# LS first: LS roster names are plain-form ("Hemang Joshi") while RS names are
# comma-flipped with honorifics ("Kumar, Shri Mithlesh"); first-token-set-wins
# means RS entries must not shadow LS ones or never-list matching breaks.
for house_key in ('ls', 'rs'):
    for m in roster.get(house_key, []):
        k = name_tokens(m.get('name'))
        if k and k not in roster_map:
            roster_map[k] = (m.get('name', ''), m.get('state', ''), m.get('party', ''))

# State spellings differ across sources ('Jammu and Kashmir' / 'Jammu & Kashmir',
# 'NCT of Delhi', trailing spaces in the RS roster). Canonicalise onto the blob's
# own keys by connective-free token key so rollups never split across spellings.
def _state_key(s):
    return ' '.join(t for t in re.findall(r'[a-z]+', (s or '').lower())
                    if t not in ('and', 'of', 'the'))

STATE_CANON = {}
for _k in list(enrich['states'].keys()) + list(enrich['mpDir'].keys()):
    STATE_CANON.setdefault(_state_key(_k), _k)
STATE_CANON.setdefault('nct delhi', 'Delhi')
STATE_CANON.setdefault('national capital territory delhi', 'Delhi')

def canon_state(s):
    return STATE_CANON.get(_state_key(s), (s or '').strip())

def resolve(name):
    """(official_name, state, party) or (None, '', '') when unresolvable."""
    if name in name_map:
        o, st, p = name_map[name]
        return (o, canon_state(st), p)
    hit = roster_map.get(name_tokens(name))
    if hit:
        return (hit[0], canon_state(hit[1]), hit[2])
    return (None, '', '')

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

# token-set index of the never list: the roster fallback returns comma-flipped
# honorific forms ("Selvaganapathi, Shri T.M.") that never equal the plain
# never-list keys, so membership must be tested by token set, not exact string
never_tok = {name_tokens(k): k for k in never}

for r in new:
    yr = int(r['d'][:4]) if r['d'] else None
    enrich['minCounts'][r['min']] = enrich['minCounts'].get(r['min'], 0) + 1
    rec_states = set()
    for name in r['m']:
        official, rst, party = resolve(name)
        meta = enrich['mpMeta'].get(name)
        if meta:
            meta[2] += 1
            if yr:  # blob may store years as strings - compare numerically, keep int
                meta[3] = min(int(meta[3]), yr) if meta[3] else yr
                meta[4] = max(int(meta[4]), yr) if meta[4] else yr
            st = meta[0]
        else:
            st = rst
            enrich['mpMeta'][name] = [st, party, 1, yr, yr]
            if official is None:
                unmatched.append({'name': name, 'house': r['h'], 'title': r['j']})
        if st:
            rec_states.add(st)
        # never-asked -> asked transition (LS only; the headline stat)
        if r['h'] == 'LS' and official:
            nk = never_tok.pop(name_tokens(official), None)
            if nk is not None:
                nst = never.pop(nk)
                removed_from_never.append({'official': nk, 'dataset_name': name, 'state': nst})
                enrich['neverTotal'] = max(0, enrich['neverTotal'] - 1)
                if nst in enrich['states'] and 'never' in enrich['states'][nst]:
                    enrich['states'][nst]['never'] = max(0, enrich['states'][nst]['never'] - 1)
        # constituency directory (LS18 sitting members only, so LS records only):
        # bump the MP's entry. A first-time asker's entry has ds='' — fall back to
        # token-matching the official name, then stamp ds so their hemicycle dot
        # flips and future runs take the fast path.
        if st and r['h'] == 'LS':
            entries = enrich['mpDir'].get(st, [])
            hit = next((x for x in entries if x.get('ds') == name), None)
            if hit is None and official:
                otoks = name_tokens(official)
                hit = next((x for x in entries
                            if not x.get('ds') and name_tokens(x.get('mp')) == otoks), None)
                if hit is not None:
                    hit['ds'] = name
            if hit is not None:
                hit['n'] = hit.get('n', 0) + 1
                if yr:
                    yrs = [int(x) for x in re.findall(r'\d{4}', str(hit.get('y') or ''))] + [yr]
                    hit['y'] = f'{min(yrs)}–{max(yrs)}'
                tl = hit.setdefault('t', [])
                for gi in r['g']:
                    if TAGS[gi] not in tl:
                        tl.append(TAGS[gi])
    # per-state totals count DISTINCT QUESTIONS with >=1 asker from the state
    # (v3.1 baseline semantics) — never once per co-asker
    for st in rec_states:
        if st in enrich['states']:
            enrich['states'][st]['total'] = enrich['states'][st].get('total', 0) + 1
    counted.add(record_key(r))

# Persistently retry askers we couldn't resolve on earlier runs (new RS members,
# by-election MPs missing from the static roster). Once a mapping appears
# (roster refresh or a hand-added mp_enrichment.csv row), patch their mpMeta
# state/party in place and fold their accumulated count into the state rollup.
# Until then they stay in the report EVERY run, not just the day they appeared.
healed = []
still_unresolved = []
for nm in state.get('unresolved', []):
    meta = enrich['mpMeta'].get(nm)
    if meta is None:
        continue
    if meta[0]:
        healed.append(nm); continue          # fixed by hand in the blob itself
    off, st_, party = resolve(nm)
    if off is not None and st_:
        meta[0], meta[1] = st_, party
        if st_ in enrich['states']:
            # approximation: assumes no same-state co-asker already counted these
            # records; exact backfill would need per-record replay
            enrich['states'][st_]['total'] = enrich['states'][st_].get('total', 0) + meta[2]
        healed.append(nm)
    else:
        still_unresolved.append(nm)
for u in unmatched:
    if u['name'] not in still_unresolved:
        still_unresolved.append(u['name'])

# recompute each state's top-asker list from mpMeta (keep existing list length)
for st, s in enrich['states'].items():
    if 'top' in s and s['top']:
        k = len(s['top'])
        ranked = sorted(((n, m[2], m[1]) for n, m in enrich['mpMeta'].items() if m[0] == st),
                        key=lambda x: -x[1])[:k]
        s['top'] = [[n, c, p] for n, c, p in ranked]

save_json(DATA / 'enrich.json', enrich, compact=True)
save_json(DATA / 'never_official.json', never)
save_json(DATA / 'enrich_state.json', {'counted_keys': sorted(counted),
                                       'unresolved': still_unresolved})
save_json(DATA / 'enrich_report.json', {'new_records_applied': len(new),
                                        'unmatched_new_askers': unmatched,
                                        'unresolved_askers_outstanding': still_unresolved,
                                        'healed_this_run': healed,
                                        'left_never_asked_list': removed_from_never})
print(f'build_enrich: applied {len(new)} new records | never-asked now {enrich["neverTotal"]} '
      f'| unmatched new askers: {len(unmatched)}')
if removed_from_never:
    for x in removed_from_never:
        print(f"  STORY: {x['official']} ({x['state']}) asked their FIRST road-safety question")
sys.exit(0)
