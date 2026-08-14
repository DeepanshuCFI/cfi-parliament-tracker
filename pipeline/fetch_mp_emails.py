#!/usr/bin/env python3
"""Stamp official parliamentary email addresses onto ENRICH.mpDir / ENRICH.rsDir.

Powers the page's "Write to your MP" layer. OFFICIAL addresses only: an email
qualifies iff its domain contains 'sansad' (@mpls.sansad.in, @sansad.nic.in).
The same APIs return personal gmail/rediffmail addresses and personal phone
numbers - those are deliberately never written to any file in this repo.

LS: api_ls/member?loksabha=18 (paginated). Joined to mpDir by photo uuid
    (the roster's imageUrl carries the same DMS uuid mpDir stores in img),
    falling back to a unique-candidate token match within the state - initials
    do not distinguish members, so an ambiguous key is left unstamped rather
    than guessed (see name_tokens in common.py).
RS: api_rs/member/sitting-members WITHOUT a status filter, keyed by mpsno
    (the sitting filter is known non-exhaustive; mpsno is unique across all
    2,500+ records so keying everything sidesteps it). rsDir img='rs/P<mpsno>.jpg'
    embeds mpsno, so the join is exact. RS emails arrive obfuscated
    ("x[at]sansad[dot]nic[dot]in", sometimes '; personal@...' appended) -
    de-obfuscated, split, filtered.

Writes em='<first official email>' per entry; audit trail in data/mp_emails.json.
Not wired into the daily workflow - emails turn over when the House does.
Re-run on a roster change:  python3 pipeline/fetch_mp_emails.py   (--dry-run)
"""
import re
import sys

from common import DATA, get, load_json, save_json, name_tokens, state_key

LS_API = 'https://sansad.in/api_ls/member?loksabha=18&page={page}&size=100'
RS_API = ('https://sansad.in/api_rs/member/sitting-members?page={page}&size=500')

UUID_RE = re.compile(r'fetch/([0-9a-f\-]{36})')


def deobfuscate(s):
    """'x[at]y[dot]z; p@q' -> ['x@y.z', 'p@q']"""
    if not s:
        return []
    s = re.sub(r'\[\s*at\s*\]', '@', s, flags=re.I)
    s = re.sub(r'\[\s*dot\s*\]', '.', s, flags=re.I)
    return [p.strip().rstrip('.') for p in re.split(r'[;,\s]+', s) if '@' in p]


def official_only(emails):
    """Keep addresses whose DOMAIN contains 'sansad'; personal ids never pass."""
    out = []
    for e in emails:
        if not e:
            continue
        e = e.strip()
        dom = e.split('@', 1)[1].lower() if '@' in e else ''
        if 'sansad' in dom and re.fullmatch(r"[A-Za-z0-9._%+\-']+@[A-Za-z0-9.\-]+", e):
            out.append(e.lower())
    return out


def fetch_ls():
    members, page = [], 1
    while True:
        d = get(LS_API.format(page=page))
        if not d or 'membersDtoList' not in d:
            sys.exit(f'fetch_mp_emails: LS API failed on page {page}')
        members.extend(d['membersDtoList'])
        if page >= d['metaDatasDto']['totalPages']:
            return members
        page += 1


def fetch_rs():
    members, page = [], 1
    while True:
        d = get(RS_API.format(page=page))
        if not d or 'records' not in d:
            sys.exit(f'fetch_mp_emails: RS API failed on page {page}')
        members.extend(d['records'])
        if page >= d['_metadata']['totalPages']:
            return members
        page += 1


def main():
    dry = '--dry-run' in sys.argv
    enrich = load_json(DATA / 'enrich.json')
    if not enrich:
        sys.exit('fetch_mp_emails: data/enrich.json missing')

    # ---- Lok Sabha ----
    ls = fetch_ls()
    by_uuid, by_name = {}, {}
    audit = {'ls': [], 'rs': []}
    for m in ls:
        emails = official_only(m.get('email') or [])
        rec = {'mpsno': m['mpsno'], 'name': (m.get('mpFirstLastName') or '').strip(),
               'state': m.get('stateName') or '', 'const': m.get('constName') or '',
               'emails': emails}
        audit['ls'].append(rec)
        u = UUID_RE.search(m.get('imageUrl') or '')
        if u:
            by_uuid[u.group(1)] = rec
        key = (state_key(rec['state']), name_tokens(rec['name']))
        # homonym guard: a colliding (state, tokens) key is poisoned, not first-wins
        by_name[key] = None if key in by_name else rec

    stamped_ls = missing_ls = unmatched_ls = 0
    for st, entries in enrich['mpDir'].items():
        for x in entries:
            rec = by_uuid.get(x.get('img') or '')
            if rec is None:
                rec = by_name.get((state_key(st), name_tokens(x.get('mp'))))
            if rec is None:
                unmatched_ls += 1
                print(f"  LS unmatched: {x.get('mp')} ({st})")
                continue
            if rec['emails']:
                x['em'] = rec['emails'][0]
                stamped_ls += 1
            else:
                x.pop('em', None)
                missing_ls += 1

    # ---- Rajya Sabha ----
    rs = fetch_rs()
    by_mpsno = {}
    for m in rs:
        emails = official_only(deobfuscate(m.get('emailID')))
        by_mpsno[m['mpsno']] = emails
        if (m.get('status') or '').strip() == 'Sitting':
            audit['rs'].append({'mpsno': m['mpsno'], 'name': (m.get('name') or '').strip(),
                                'state': (m.get('state') or '').strip(), 'emails': emails})

    stamped_rs = missing_rs = unmatched_rs = 0
    for st, entries in enrich.get('rsDir', {}).items():
        for x in entries:
            mm = re.fullmatch(r'rs/P(\d+)\.jpg', str(x.get('img') or ''))
            emails = by_mpsno.get(int(mm.group(1))) if mm else None
            if emails is None:
                unmatched_rs += 1
                print(f"  RS unmatched: {x.get('mp')} ({st})")
                continue
            if emails:
                x['em'] = emails[0]
                stamped_rs += 1
            else:
                x.pop('em', None)
                missing_rs += 1

    n_ls = sum(len(v) for v in enrich['mpDir'].values())
    n_rs = sum(len(v) for v in enrich.get('rsDir', {}).values())
    print(f'fetch_mp_emails: LS {stamped_ls}/{n_ls} stamped '
          f'({missing_ls} no official email, {unmatched_ls} unmatched) | '
          f'RS {stamped_rs}/{n_rs} stamped '
          f'({missing_rs} no official email, {unmatched_rs} unmatched)')
    if dry:
        print('fetch_mp_emails: dry run, nothing written')
        return
    save_json(DATA / 'enrich.json', enrich, compact=True)
    save_json(DATA / 'mp_emails.json', audit)
    print('fetch_mp_emails: wrote data/enrich.json + data/mp_emails.json')


if __name__ == '__main__':
    main()
