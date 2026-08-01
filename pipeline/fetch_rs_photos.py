#!/usr/bin/env python3
"""Stamp Rajya Sabha member photo ids onto ENRICH.rsDir.

LS photos came out of the original v3.1 assembly as sansad DMS UUIDs
(/mpimg/<uuid> -> getFile/dms/fetch/<uuid>). RS photos live on a different
sansad path and need no lookup table at all: the file is derived from the
member number, P<mpsno>.jpg. So we only need mpsno per sitting member, which
api_rs/member/sitting-members returns.

rsDir entries get img='rs/P<mpsno>.jpg'; site/vercel.json rewrites /mpimg/rs/:f
to the sansad newmembers path, so the page keeps one /mpimg/ convention for
both houses and stays same-origin under the CSP.

Not wired into the daily workflow - rsDir turns over only when the House does.
Re-run on an RS roster change:  python3 pipeline/fetch_rs_photos.py

  --dry-run   report matches, write nothing
  --verify    GET every stamped photo, drop any that does not return an image
"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor

from common import DATA, UA, get, load_json, save_json, name_tokens, state_key

API = ('https://sansad.in/api_rs/member/sitting-members?state=&party=&gender='
       '&page={page}&size=50&mpFlag=1&ageFrom=&ageTo=&terms=&search=&locale=en'
       '&month=&ministership=&membershipFrom=&membershipTo=&educationLevelCode='
       '&degreeCode=&subjectCode=&profession1=&profession2=&profession3='
       '&noOfChildren=&nominated=')
PHOTO = 'https://sansad.in/getFile/newmembers/photos/{f}?source=rajyasabha'

# The roster spells Delhi out in full; rsDir uses the short form.
STATE_ALIAS = {'national capital territory delhi': 'delhi', 'nct delhi': 'delhi'}

# Hand-verified where rsDir and the sansad roster disagree on the NAME itself,
# not just its word order - no token rule can bridge these, and guessing across
# a surname change is exactly how the wrong MP gets someone else's face.
#   Laxmikant Bajpayee = "Bajpai, Dr. Laxmi Kant"  (mpsno 2558, matches roster.json)
#   Alka Singh         = "Gurjar, Dr. Alka"        (Alka Singh Gurjar)
NAME_ALIAS = {('uttar pradesh', 'Laxmikant Bajpayee'): 2558,
              ('rajasthan', 'Alka Singh'): 2688}

def canon(s):
    k = state_key(s)
    return STATE_ALIAS.get(k, k)

def dedup(toks):
    """rsDir carries the odd doubled word ('Karamvir Singh Singh Boudh')."""
    return tuple(sorted(set(toks)))

dry = '--dry-run' in sys.argv
verify = '--verify' in sys.argv

enrich = load_json(DATA / 'enrich.json')
rsdir = enrich.get('rsDir') or {}
if not rsdir:
    sys.exit('fetch_rs_photos: ENRICH.rsDir missing - nothing to stamp')

# --- pull every page of the sitting-members roster -------------------------
members, page, pages = [], 1, 1
while page <= pages:
    d = get(API.format(page=page))
    if not d or 'records' not in d:
        sys.exit(f'fetch_rs_photos: page {page} fetch failed - aborting, nothing written')
    pages = d['_metadata']['totalPages']
    members += d['records']
    page += 1
print(f'fetch_rs_photos: pulled {len(members)} sitting members across {pages} pages')

# --- index by (state, name tokens), with the homonym guard -----------------
# Same trap as build_enrich: name_tokens drops initials, so distinct members can
# share a key. Keying by state first shrinks the collision space; anything still
# ambiguous is refused rather than resolved by order.
idx, ambiguous = {}, set()
for m in members:
    toks = name_tokens(m.get('name'))
    if not toks:
        continue
    # index under both the exact and the deduped token key; a member whose two
    # keys are identical simply writes the same entry twice
    for k in {(canon(m.get('state')), toks), (canon(m.get('state')), dedup(toks))}:
        if k in idx and idx[k] != m['mpsno']:
            ambiguous.add(k)
        else:
            idx[k] = m['mpsno']
# The live sitting-members list is not exhaustive - it missed Rukmini Mallik
# (mpsno 2680, notified Apr 2026) whose photo exists. roster.json carries mpsno
# for every member, so use it to fill gaps; API entries win where both have a key.
roster_rs = (load_json(DATA / 'roster.json', {}) or {}).get('rs', [])
gap_filled = 0
for m in roster_rs:
    if not m.get('mpFlag') or not m.get('mpsno'):
        continue
    toks = name_tokens(m.get('name'))
    if not toks:
        continue
    for k in {(canon(m.get('state')), toks), (canon(m.get('state')), dedup(toks))}:
        if k in idx:
            if idx[k] != m['mpsno']:
                ambiguous.add(k)
        else:
            idx[k] = m['mpsno']; gap_filled += 1
for k in ambiguous:
    idx.pop(k, None)
print(f'fetch_rs_photos: {gap_filled} keys filled from roster.json beyond the API list')

# --- stamp ------------------------------------------------------------------
stamped, missed, skipped_amb = 0, [], 0
for st, entries in rsdir.items():
    for e in entries:
        toks = name_tokens(e.get('mp'))
        keys = [(canon(st), toks), (canon(st), dedup(toks))]
        if any(k in ambiguous for k in keys):
            skipped_amb += 1
            missed.append((st, e.get('mp'), 'ambiguous name in state'))
            continue
        mpsno = NAME_ALIAS.get((canon(st), e.get('mp')))
        for k in keys:
            if mpsno is not None:
                break
            mpsno = idx.get(k)
        if mpsno is None:
            missed.append((st, e.get('mp'), 'no roster match'))
            continue
        e['img'] = f'rs/P{mpsno}.jpg'
        stamped += 1

total = sum(len(v) for v in rsdir.values())
print(f'fetch_rs_photos: stamped {stamped}/{total} rsDir entries '
      f'({len(missed)} unmatched, {skipped_amb} of them ambiguous)')
for st, mp, why in missed:
    print(f'   UNMATCHED  {mp} ({st}) - {why}')

if verify:
    def probe(e):
        # GET, not HEAD: sansad answers HEAD with 403 across the board. Check the
        # content type too, so an HTML error page served as 200 is not a pass.
        f = e['img'].split('/', 1)[1]
        r = subprocess.run(['curl', '-s', '-o', '/dev/null', '--max-time', '45',
                            '-A', UA, '-w', '%{http_code} %{content_type} %{size_download}',
                            PHOTO.format(f=f)], capture_output=True, text=True)
        return e, r.stdout.strip()
    have = [e for v in rsdir.values() for e in v if e.get('img')]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(probe, have))
    def ok(v):
        p = v.split()
        return len(p) == 3 and p[0] == '200' and p[1].startswith('image/') and int(p[2]) > 1000
    bad = [(e, v) for e, v in results if not ok(v)]
    print(f'fetch_rs_photos: verified {len(results)} photos, {len(bad)} failed')
    for e, v in bad:
        print(f"   FAIL [{v}]  {e['mp']}  {e['img']}")
    # a photo that does not resolve is worse than no photo: the card would show a
    # broken frame instead of falling back to the initials avatar
    for e, _ in bad:
        e.pop('img', None)
    if bad:
        print(f'fetch_rs_photos: dropped img from {len(bad)} unreachable entries')

if dry:
    print('fetch_rs_photos: --dry-run, enrich.json not written')
    sys.exit(0)

save_json(DATA / 'enrich.json', enrich, compact=True)
final = sum(1 for v in rsdir.values() for e in v if e.get('img'))
print(f'fetch_rs_photos: wrote enrich.json - {final}/{total} RS entries now carry a photo')
