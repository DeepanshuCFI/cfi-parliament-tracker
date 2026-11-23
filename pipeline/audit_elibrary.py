#!/usr/bin/env python3
"""Full-text audit of the tracker's Lok Sabha records against eLibrary Sansad.

MANUAL ONLY. Never part of the daily workflow, never writes dataset.json.

eLibrary Sansad (elibrary.sansad.in) is the Lok Sabha Secretariat's DSpace
archive. Its "Part 1 (Questions And Answers)" collection holds every Lok Sabha
question with the answer PDF's extracted text, so its search is FULL TEXT
(question + answer + annexures). The tracker picks questions by TITLE, so this
is an independent net for questions the title filter missed.

Limits: Lok Sabha only (no Rajya Sabha), and it loads about seven weeks behind.

Stages (each caches under --work, rerunnable):
  sweep   full-text queries per Lok Sabha -> sweep.json (item metadata + terms hit)
  diff    sweep vs data/dataset.json      -> unmatched.json + recall figures
  texts   question text of unmatched items in the four tracked ministries
  all     the three above in order

A full-text hit is a CANDIDATE, never an inclusion: answers carry boilerplate
mentions of road safety. Inclusion stays an editorial decision.

Python urllib fails TLS on some machines here, so requests go through curl.
"""
import argparse
import collections
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

API = 'https://elibrary.sansad.in/server/api'
COLLECTION = '75228d43-3a98-4b7d-b90f-ffec6aa9fa11'   # Part 1 (Questions And Answers)
LOK_SABHAS = ('16', '17', '18')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Phrases searched in the full text. Broad on purpose: precision comes later.
TERMS = [
    'road safety', 'road accident', 'road accidents', 'road crash', 'road crashes',
    'road fatalities', 'accident victims', 'accident prone', 'black spot', 'black spots',
    'hit and run', 'drunk driving', 'drunken driving', 'drink and drive',
    'helmet', 'helmets', 'seat belt', 'seat belts', 'airbag', 'airbags',
    'overspeeding', 'over speeding', 'speed limit', 'speed limits', 'speed governor',
    'wrong side driving', 'overloading', 'pedestrian', 'pedestrians', 'footpath',
    'footpaths', 'foot over bridge', 'cycle track', 'golden hour', 'good samaritan',
    'rah-veer', 'rahveer', 'trauma care', 'trauma centre', 'trauma centres',
    'cashless treatment', 'motor vehicles act', 'motor vehicle accident',
    'motor accident claims', 'driving licence', 'driving license', 'vehicle fitness',
    'crash test', 'bharat ncap', 'vehicle recall', 'road safety audit', 'crash barrier',
    'crash barriers', 'school bus', 'zero fatality', 'traffic violation',
    'traffic violations', 'e-challan', 'ambulance', 'ambulances',
    # Added after the first pass: 55 of our own 813 Lok Sabha records were not
    # found by the phrases above (safety audits, driver training, EMS, CMVR).
    'accident', 'accidents', 'collision', 'collisions', 'fatalities', 'safety audit',
    'driver training', 'driving training', 'emergency medical', 'motor vehicle',
    'motor vehicles', 'public safety', 'safety measures',
]
# Ministries enumerated IN FULL (every question, no phrase needed). MoRTH carries
# 83% of our Lok Sabha records, so its audit must not depend on a phrase list.
ENUMERATE = ['ROAD TRANSPORT AND HIGHWAYS']

# eLibrary ministry label -> tracker ministry key (labels changed over 2014-2026).
MINISTRY = {
    'ROAD TRANSPORT AND HIGHWAYS': 'MoRTH',
    'HEALTH AND FAMILY WELFARE': 'Health',
    'HEAVY INDUSTRIES': 'Heavy',
    'HEAVY INDUSTRIES AND PUBLIC ENTERPRISES': 'Heavy',
    'HOUSING AND URBAN AFFAIRS': 'Urban',
    'URBAN DEVELOPMENT': 'Urban',
    'HOUSING AND URBAN POVERTY ALLEVIATION': 'Urban',
    'HOME AFFAIRS': 'Home',
}

ROMAN = {r: i + 1 for i, r in enumerate(
    'I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX'.split())}

# Road-safety vocabulary used to test the QUESTION part of a PDF's text.
SAFETY_RE = re.compile(
    r'accident|crash|collision|fatalit|casualt|road\s+safety|safety\s+(?:audit|measure|norm|standard|feature|rating)|'
    r'black\s*spot|hit\s*(?:and|&)\s*run|drunk|drink\s+and\s+driv|helmet|seat\s*belt|air\s*bag|'
    r'over\s*-?\s*speed|speed\s+(?:limit|governor|camera|monitor|gun)|wrong\s+side|overload|'
    r'pedestrian|foot\s*path|foot\s+over\s+bridge|cycle\s+track|zebra|golden\s+hour|good\s+samaritan|'
    r'rah\s*-?\s*veer|trauma|ambulance|cashless|compensation\s+to\s+(?:the\s+)?(?:victim|kin|famil)|'
    r'motor\s+vehicles?\s+(?:act|\(amendment\))|driving\s+licen[cs]e|fitness\s+(?:certificate|test)|'
    r'ncap|recall|crash\s+barrier|school\s+bus|zero\s+fatalit|traffic\s+(?:violation|rule|offen[cs]e)|'
    r'challan|injur|death', re.I)


def curl_json(path, params=None, tries=3):
    url = API + path + ('?' + urllib.parse.urlencode(params, doseq=True) if params else '')
    for attempt in range(tries):
        r = subprocess.run(['curl', '-sS', '-m', '120', '-A', 'Mozilla/5.0', url],
                           capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except ValueError:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f'no JSON from {url}: {r.stdout[:200]} {r.stderr[:200]}')


def curl_text(url, tries=3):
    for attempt in range(tries):
        r = subprocess.run(['curl', '-sS', '-L', '-m', '120', '-A', 'Mozilla/5.0', url],
                           capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode('utf-8', 'replace')
        time.sleep(2 * (attempt + 1))
    return ''


def first(meta, key):
    v = meta.get(key) or []
    return v[0]['value'].strip() if v else ''


def record_of(item):
    m = item['metadata']
    return {
        'uuid': item['uuid'],
        'handle': item.get('handle', ''),
        'title': first(m, 'dc.title'),
        'date': first(m, 'dc.date.issued'),
        'l': first(m, 'dc.identifier.loksabhanumber'),
        's': first(m, 'dc.identifier.sessionnumber'),
        'q': first(m, 'dc.identifier.questionnumber'),
        'type': first(m, 'dc.identifier.questiontype'),
        'ministry': first(m, 'dc.relation.ministry'),
        'members': [x['value'].strip() for x in m.get('dc.contributor.members', [])],
    }


def search(query, ls, extra=None):
    page = 0
    while True:
        params = {'scope': COLLECTION, 'dsoType': 'ITEM', 'size': 100, 'page': page,
                  'f.loksabhanumber': f'{ls},equals'}
        if query:
            params['query'] = query
        params.update(extra or {})
        sr = curl_json('/discover/search/objects', params)['_embedded']['searchResult']
        for o in sr.get('_embedded', {}).get('objects', []):
            yield record_of(o['_embedded']['indexableObject'])
        page += 1
        if page >= sr['page']['totalPages']:
            return
        time.sleep(0.15)


def key_of(l, s, q, t):
    """(lok sabha, session int, question number, S/U) - the tracker's own identity."""
    s = str(s).strip()
    s = str(ROMAN.get(s.upper(), s))
    q = re.sub(r'\D', '', str(q))
    return (str(l).strip().lstrip('0'), s.lstrip('0'), q.lstrip('0'),
            'S' if str(t).upper().startswith('S') else 'U')


def norm_title(t):
    return re.sub(r'[^a-z0-9]+', ' ', t.replace('&amp;', '&').lower()).strip()


def stage_sweep(work):
    out = os.path.join(work, 'sweep.json')
    items, counts = {}, {}
    if os.path.exists(out):
        saved = json.load(open(out))
        items, counts = saved['items'], saved['counts']
    for ls in LOK_SABHAS:
        for term in TERMS:
            tag = f'{ls}|{term}'
            if tag in counts:
                continue
            n = 0
            for rec in search(f'"{term}"', ls):
                n += 1
                it = items.setdefault(rec['uuid'], dict(rec, terms=[]))
                if term not in it['terms']:
                    it['terms'].append(term)
            counts[tag] = n
            print(f'  LS{ls} "{term}": {n}', flush=True)
            json.dump({'items': items, 'counts': counts}, open(out, 'w'), ensure_ascii=False)
        for ministry in ENUMERATE:
            tag = f'{ls}|ALL:{ministry}'
            if tag in counts:
                continue
            n = 0
            for rec in search(None, ls, {'f.ministry': f'{ministry},equals'}):
                n += 1
                items.setdefault(rec['uuid'], dict(rec, terms=[]))
            counts[tag] = n
            print(f'  LS{ls} every {ministry} question: {n}', flush=True)
            json.dump({'items': items, 'counts': counts}, open(out, 'w'), ensure_ascii=False)
    print(f'sweep: {len(items)} distinct items across {len(counts)} queries')
    return items


def stage_diff(work, dataset_path=None):
    items = json.load(open(os.path.join(work, 'sweep.json')))['items']
    ds = json.load(open(dataset_path or os.path.join(REPO, 'data', 'dataset.json')))
    ours = [r for r in ds['records'] if r['h'] == 'LS']
    our_keys = {key_of(r['l'], r['s'], r['q'], r['t']): r for r in ours}
    our_titles = {(r['d'], norm_title(r['j'])) for r in ours}

    # Collapse eLibrary duplicates (a starred question and its supplementaries share a key).
    by_key = {}
    for it in items.values():
        k = key_of(it['l'], it['s'], it['q'], it['type'])
        cur = by_key.get(k)
        if cur is None:
            by_key[k] = dict(it, key=list(k))
        else:
            cur['terms'] = sorted(set(cur['terms']) | set(it['terms']))
            for m in it['members']:
                if m not in cur['members']:
                    cur['members'].append(m)

    matched = {k for k in by_key if k in our_keys}
    title_matched = {k for k, it in by_key.items()
                     if k not in matched and (it['date'], norm_title(it['title'])) in our_titles}
    unmatched = [it for k, it in by_key.items() if k not in matched and k not in title_matched]
    for it in unmatched:
        # '?' = eLibrary left the ministry blank (LS16 sessions XIII-XV); resolved
        # later from the question text ("Will the Minister of ...").
        it['min'] = MINISTRY.get(it['ministry'].upper(), '') if it['ministry'] else '?'

    found = len(matched) + len(title_matched)
    not_found = [r for k, r in our_keys.items() if k not in matched
                 and (r['d'], norm_title(r['j'])) not in
                 {(it['date'], norm_title(it['title'])) for it in by_key.values()}]
    stats = {
        'elibrary_items': len(items), 'elibrary_questions': len(by_key),
        'our_ls_records': len(ours), 'our_records_found_by_sweep': found,
        'our_records_not_found': len(not_found),
        'unmatched_total': len(unmatched),
        'unmatched_by_ministry': collections.Counter(
            it['min'] or 'other' for it in unmatched).most_common(),
        'unmatched_other_ministries': collections.Counter(
            it['ministry'] for it in unmatched if not it['min']).most_common(15),
    }
    json.dump({'stats': stats, 'unmatched': unmatched,
               'not_found': [{k: r[k] for k in ('l', 's', 'q', 't', 'd', 'j', 'min')} for r in not_found]},
              open(os.path.join(work, 'unmatched.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(stats, indent=1))
    return unmatched


QUESTION_RE = re.compile(r'will\s+the\s+minister', re.I)
ANSWER_RE = re.compile(r'\n\s*A\s*N\s*S\s*W\s*E\s*R\b|\bANSWER\b')


def question_part(text):
    """The MP's question, cut from the PDF text: 'Will the Minister ...' up to 'ANSWER'."""
    m = QUESTION_RE.search(text)
    start = m.start() if m else 0
    a = ANSWER_RE.search(text, start + 20)
    end = a.start() if a else min(len(text), start + 2500)
    return re.sub(r'\s+', ' ', text[start:end]).strip()[:3000]


def fetch_question(uuid):
    d = curl_json(f'/core/items/{uuid}', {'embed': 'bundles/bitstreams'})
    for b in d.get('_embedded', {}).get('bundles', {}).get('_embedded', {}).get('bundles', []):
        if b['name'] != 'TEXT':
            continue
        streams = b.get('_embedded', {}).get('bitstreams', {}).get('_embedded', {}).get('bitstreams', [])
        english = [s for s in streams if 'hindi' not in s['name'].lower()] or streams
        if english:
            text = curl_text(english[0]['_links']['content']['href'])
            return question_part(text)
    return ''


def stage_texts(work, workers=4):
    path = os.path.join(work, 'unmatched.json')
    data = json.load(open(path))
    cache_path = os.path.join(work, 'questions.json')
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    todo = [it for it in data['unmatched'] if it['min'] and it['uuid'] not in cache]
    print(f'texts: {len(todo)} to fetch ({len(cache)} cached)')

    def one(it):
        try:
            return it['uuid'], fetch_question(it['uuid'])
        except Exception as e:                      # one bad item must not stop the run
            return it['uuid'], f'__ERR__ {e}'

    with cf.ThreadPoolExecutor(workers) as ex:
        for n, (uuid, q) in enumerate(ex.map(one, todo), 1):
            cache[uuid] = q
            if n % 100 == 0 or n == len(todo):
                json.dump(cache, open(cache_path, 'w'), ensure_ascii=False)
                print(f'  {n}/{len(todo)}', flush=True)
    for it in data['unmatched']:
        q = cache.get(it['uuid'], '')
        it['question'] = '' if q.startswith('__ERR__') else q
        if it['min'] == '?':
            m = re.search(r'will\s+the\s+minister\s+of\s+(.{3,60}?)\s+be\s+pleased', it['question'], re.I)
            label = re.sub(r'\s+', ' ', m.group(1)).upper() if m else ''
            it['ministry'] = label
            it['min'] = MINISTRY.get(label, '') if label else '?'
        it['q_terms'] = sorted({m.group(0).lower() for m in SAFETY_RE.finditer(it['question'])})
        it['t_terms'] = sorted({m.group(0).lower() for m in SAFETY_RE.finditer(it['title'])})
    json.dump(data, open(path, 'w'), ensure_ascii=False, indent=1)
    errs = sum(1 for v in cache.values() if v.startswith('__ERR__') or not v)
    print(f'texts: done, {errs} without question text')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('stage', choices=['sweep', 'diff', 'texts', 'all'])
    ap.add_argument('--work', required=True, help='cache directory (keep it outside the repo)')
    ap.add_argument('--dataset', help='dataset.json to compare against (default: this checkout)')
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    if a.stage in ('sweep', 'all'):
        stage_sweep(a.work)
    if a.stage in ('diff', 'all'):
        stage_diff(a.work, a.dataset)
    if a.stage in ('texts', 'all'):
        stage_texts(a.work)


if __name__ == '__main__':
    sys.exit(main())
