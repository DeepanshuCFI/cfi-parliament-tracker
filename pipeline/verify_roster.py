#!/usr/bin/env python3
"""Reconcile ENRICH.mpDir / ENRICH.rsDir against the live sansad.in rosters.

The directories are snapshots; the Houses turn over between sessions (bypolls,
resignations, deaths, retirements, nominations). On 15 Aug 2026 a manual
reconciliation found four RS bypoll entrants missing and one resignee still
listed - this script is that check, made repeatable.

REPORT-ONLY, BY DESIGN. It never edits enrich.json or any other file. Roster
repairs need a human: party/defection data must be verified before writing
(15 Aug 2026: sansad's surprising TMC->BJP party labels were RIGHT and
pre-cutoff knowledge wrong - verify before "correcting" official data), and a
new member's question history needs the usual homonym-guarded matching.

Joins (the same rules as fetch_mp_emails.py and the 15 Aug 2026 repair):
  LS: api_ls/member?loksabha=18 (all statuses, paginated). Directory entries
      join by photo uuid (roster imageUrl carries the DMS uuid mpDir stores in
      img), falling back to a unique (state, name-token) match - initials do
      not distinguish members, so colliding keys are poisoned, never first-wins
      (see name_tokens in common.py).
  RS: api_rs/member/sitting-members WITHOUT a status filter - the sitting
      filter is known non-exhaustive, mpsno is unique across all ~2,550
      records. Directory entries join by the mpsno embedded in
      img='rs/P<mpsno>.jpg'.

Findings classes (grep-stable prefixes, consumed by verify-roster.yml):
  MISSING    sitting per sansad but absent from the directory
  DEPARTED   directory entry whose roster status is no longer 'Sitting'
  UNMATCHED  directory entry that could not be joined to the roster at all
             (RS: an mpsno absent from even the full list is possibly an API
             gap - e.g. Rukmini Mallik while sitting, 1 Aug 2026 - so it is
             reported for a human pass, not assumed departed)
  DRIFT      fresh sitting count vs ENRICH.sittingLS18/rsSitting vs directory size

Repair notes for whoever picks up the issue:
  - rsDir may lack a KEY for a state that was previously all-vacant: use
    setdefault when adding (the 15 Aug Mizoram trap).
  - Keep sittingLS18/rsSitting, neverTotal/rsNeverTotal and the directories
    three-way consistent or sanity_check.py will block the next publish.
  - After turnover repairs, rerun fetch_rs_photos.py and fetch_mp_emails.py.

  python3 pipeline/verify_roster.py           # both houses
  python3 pipeline/verify_roster.py --ls      # Lok Sabha only
  python3 pipeline/verify_roster.py --rs      # Rajya Sabha only

Exit codes: 0 = directories match the rosters, 1 = findings, 2 = fetch failure
(retryable - the workflow retries once).
"""
import re
import sys

from common import DATA, get, load_json, name_tokens, state_key

LS_API = 'https://sansad.in/api_ls/member?loksabha=18&page={page}&size=100'
RS_API = 'https://sansad.in/api_rs/member/sitting-members?page={page}&size=500'

UUID_RE = re.compile(r'fetch/([0-9a-f\-]{36})')

CLASSES = ('missing', 'departed', 'unmatched', 'drift')
LABEL = {'missing': 'MISSING', 'departed': 'DEPARTED',
         'unmatched': 'UNMATCHED', 'drift': 'DRIFT'}


def die_fetch(msg):
    print(f'verify_roster: FETCH FAILED - {msg}')
    sys.exit(2)


def fetch_ls():
    members, page = [], 1
    while True:
        d = get(LS_API.format(page=page))
        if not d or 'membersDtoList' not in d:
            die_fetch(f'LS member API page {page}')
        members.extend(d['membersDtoList'])
        if page >= d['metaDatasDto']['totalPages']:
            return members
        page += 1


def fetch_rs():
    members, page = [], 1
    while True:
        d = get(RS_API.format(page=page))
        if not d or 'records' not in d:
            die_fetch(f'RS member API page {page}')
        members.extend(d['records'])
        if page >= d['_metadata']['totalPages']:
            return members
        page += 1


def reconcile_ls(enrich):
    fresh = []
    for m in fetch_ls():
        u = UUID_RE.search(m.get('imageUrl') or '')
        fresh.append({'mpsno': m['mpsno'],
                      'name': (m.get('mpFirstLastName') or '').strip(),
                      'state': (m.get('stateName') or '').strip(),
                      'const': (m.get('constName') or '').strip(),
                      'party': (m.get('partySname') or '').strip(),
                      'status': (m.get('status') or '').strip(),
                      'uuid': u.group(1) if u else ''})
    sitting = [r for r in fresh if r['status'] == 'Sitting']
    by_uuid = {r['uuid']: r for r in fresh if r['uuid']}
    by_name = {}
    for r in fresh:
        key = (state_key(r['state']), name_tokens(r['name']))
        # homonym guard: a colliding (state, tokens) key is poisoned, not first-wins
        by_name[key] = None if key in by_name else r

    out = {c: [] for c in CLASSES}
    seen, n_dir = set(), 0
    for st, entries in (enrich.get('mpDir') or {}).items():
        for x in entries:
            n_dir += 1
            r = by_uuid.get(x.get('img') or '')
            if r is None:
                r = by_name.get((state_key(st), name_tokens(x.get('mp'))))
            if r is None:
                out['unmatched'].append(
                    f"{x.get('mp')} ({st}) img={x.get('img') or '-'} - "
                    'no uuid or unique name+state match in the LS18 roster; verify by hand')
                continue
            seen.add(r['mpsno'])
            if r['status'] != 'Sitting':
                out['departed'].append(
                    f"{x.get('mp')} ({st}) - roster status now "
                    f"'{r['status']}' (roster name: {r['name']})")
    for r in sitting:
        if r['mpsno'] not in seen:
            out['missing'].append(
                f"{r['name']} ({r['party']}, {r['const']}, {r['state']}) "
                f"mpsno={r['mpsno']} - sitting per sansad, not in mpDir")
    declared = enrich.get('sittingLS18')
    if not (len(sitting) == declared == n_dir):
        out['drift'].append(
            f'fresh sitting={len(sitting)} vs ENRICH.sittingLS18={declared} '
            f'vs mpDir entries={n_dir}')
    return out, len(sitting), n_dir


def reconcile_rs(enrich):
    by_mpsno = {}
    for m in fetch_rs():
        # every RS field arrives space-padded; state is blank for nominated members
        by_mpsno[m['mpsno']] = {'mpsno': m['mpsno'],
                                'name': (m.get('name') or '').strip().rstrip(','),
                                'state': (m.get('state') or '').strip() or 'Nominated',
                                'party': (m.get('party') or '').strip(),
                                'status': (m.get('status') or '').strip(),
                                'term': (m.get('term') or '').strip()}
    sitting = [r for r in by_mpsno.values() if r['status'] == 'Sitting']

    out = {c: [] for c in CLASSES}
    seen, n_dir = set(), 0
    for st, entries in (enrich.get('rsDir') or {}).items():
        for x in entries:
            n_dir += 1
            mm = re.fullmatch(r'rs/P(\d+)\.jpg', str(x.get('img') or ''))
            if not mm:
                out['unmatched'].append(
                    f"{x.get('mp')} ({st}) img={x.get('img') or '-'} - "
                    'no rs/P<mpsno>.jpg id to join on; verify by hand')
                continue
            r = by_mpsno.get(int(mm.group(1)))
            if r is None:
                out['unmatched'].append(
                    f"{x.get('mp')} ({st}) mpsno={mm.group(1)} - absent from the "
                    'FULL member list (possible API gap; verify by hand before '
                    'treating as departed)')
                continue
            seen.add(r['mpsno'])
            if r['status'] != 'Sitting':
                out['departed'].append(
                    f"{x.get('mp')} ({st}) - roster status now "
                    f"'{r['status']}' (roster name: {r['name']})")
    for r in sitting:
        if r['mpsno'] not in seen:
            out['missing'].append(
                f"{r['name']} ({r['party']}, {r['state']}) mpsno={r['mpsno']} "
                f"term={r['term']} - sitting per sansad, not in rsDir")
    declared = enrich.get('rsSitting')
    if not (len(sitting) == declared == n_dir):
        out['drift'].append(
            f'fresh sitting={len(sitting)} vs ENRICH.rsSitting={declared} '
            f'vs rsDir entries={n_dir}')
    return out, len(sitting), n_dir


def report(house, out, n_sitting, n_dir):
    counts = ', '.join(f'{c}={len(out[c])}' for c in CLASSES)
    print(f'{house}: roster sitting={n_sitting}, directory={n_dir}, {counts}')
    for c in CLASSES:
        for line in out[c]:
            print(f'   {LABEL[c]} [{house}] {line}')
    return sum(len(out[c]) for c in CLASSES)


def main():
    want_ls = '--rs' not in sys.argv
    want_rs = '--ls' not in sys.argv
    enrich = load_json(DATA / 'enrich.json')
    if not enrich:
        print('verify_roster: data/enrich.json missing/unparseable')
        sys.exit(2)

    total = 0
    if want_ls:
        total += report('LS', *reconcile_ls(enrich))
    if want_rs:
        total += report('RS', *reconcile_rs(enrich))

    if total:
        print(f'verify_roster: FINDINGS - {total} item(s) need a human pass')
        print('   NOTE: report-only by design; nothing was written. Verify party/'
              'defection data before repairing (see module docstring).')
        sys.exit(1)
    print('verify_roster: OK - directories match the live rosters')
    sys.exit(0)


if __name__ == '__main__':
    main()
