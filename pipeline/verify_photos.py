#!/usr/bin/env python3
"""Audit that every MP photo id in ENRICH still resolves to an image, both houses.

sanity_check.py guards coverage and id SHAPE on every run; it cannot guard
reachability, because that would mean ~780 requests to sansad per daily run and
would fail the publish on any upstream hiccup. So reachability is audited here,
on demand.

Read-only - it never edits enrich.json. Exits nonzero if anything is unreachable,
so it can be dropped into a weekly job later if photo rot ever becomes real.

  python3 pipeline/verify_photos.py           # both houses
  python3 pipeline/verify_photos.py --ls      # Lok Sabha only
  python3 pipeline/verify_photos.py --rs      # Rajya Sabha only
"""
import sys
from concurrent.futures import ThreadPoolExecutor

from common import DATA, load_json, probe_image

want_ls = '--rs' not in sys.argv
want_rs = '--ls' not in sys.argv

enrich = load_json(DATA / 'enrich.json')
if not enrich:
    sys.exit('verify_photos: enrich.json missing/unparseable')

targets = []
if want_ls:
    targets += [('LS', st, m) for st, v in (enrich.get('mpDir') or {}).items() for m in v]
if want_rs:
    targets += [('RS', st, m) for st, v in (enrich.get('rsDir') or {}).items() for m in v]

missing = [t for t in targets if not t[2].get('img')]
have = [t for t in targets if t[2].get('img')]
print(f'verify_photos: {len(have)} photos to probe '
      f'({len(missing)} entries carry no img)')
for house, st, m in missing:
    print(f'   NO IMG  [{house}] {m.get("mp")} ({st})')

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(lambda t: (t, probe_image(t[2]['img'])), have))

bad = [(t, v) for t, (ok, v) in results if not ok]
by_house = {}
for (house, _, _), (ok, _) in results:
    h = by_house.setdefault(house, [0, 0])
    h[0] += 1
    h[1] += 0 if ok else 1
for house, (n, nbad) in sorted(by_house.items()):
    print(f'   {house}: {n - nbad}/{n} reachable')

for (house, st, m), v in bad:
    print(f'   FAIL [{v}]  [{house}] {m.get("mp")} ({st}) {m.get("img")}')

if bad or missing:
    print(f'verify_photos: FAILED - {len(bad)} unreachable, {len(missing)} without an id')
    sys.exit(1)
print('verify_photos: OK - every photo id resolves to an image')
sys.exit(0)
