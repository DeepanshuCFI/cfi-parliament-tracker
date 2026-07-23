#!/usr/bin/env python3
"""Delta refresh: pull ONLY the current session's questions from the LS/RS APIs,
stage anything new for curation, and detect session rollover.

Light by design (~10 API calls) so it can run daily during a live session.
The full 2014-onwards re-enumeration lives in full_rebuild.py (manual only).

Outputs:
  data/pending_curation.json  - new candidate records + keyword verdicts (curate.py commits them)
  data/refresh_report.json    - what happened this run (surfaced in the CI job summary)
"""
import sys, time
from common import (DATA, get, MINISTRIES, tag_for, iso, clean_mp,
                    record_key, load_json, save_json)

sessions = load_json(DATA / 'sessions.json')
cur = sessions['current']
dataset = load_json(DATA / 'dataset.json')
existing = {record_key(r) for r in dataset['records']}
decisions = load_json(DATA / 'curation_decisions.json', {})

report = {'session': cur['label'], 'api_failures': [], 'fetched': {}, 'new_candidates': 0,
          'rollover_alert': None}

# ---- session rollover detection ------------------------------------------------
# RS: probe one session past the registered one; LS: read the official session list.
probe = get(f"https://rsdoc.nic.in/Question/Search_Questions?whereclause=ses_no={int(cur['rs_session'])+1}")
if isinstance(probe, list) and len(probe) > 0:
    report['rollover_alert'] = (f"RS session {int(cur['rs_session'])+1} has questions but sessions.json "
                                f"still points at {cur['rs_session']} - update data/sessions.json")
sess_meta = get('https://sansad.in/api_ls/business/getAllLoksabhaAndSession?locale=en')
if sess_meta:
    def walk(o, acc):
        if isinstance(o, dict):
            lk = o.get('loksabhaNo') or o.get('lokSabhaNo'); sn = o.get('sessionNumber') or o.get('sessionNo')
            if lk and sn:
                try: acc.setdefault(int(lk), set()).add(int(sn))
                except Exception: pass
            for v in o.values(): walk(v, acc)
        elif isinstance(o, list):
            for v in o: walk(v, acc)
    acc = {}
    walk(sess_meta, acc)
    lk = int(cur['ls_lk'])
    max_lk = max(acc) if acc else lk
    max_sn = max(acc.get(lk, {int(cur['ls_session'])}))
    if max_lk > lk or max_sn > int(cur['ls_session']):
        report['rollover_alert'] = ((report['rollover_alert'] or '') +
            f" | LS shows Lok Sabha {max_lk} session {max_sn}; sessions.json has "
            f"LS{cur['ls_lk']} session {cur['ls_session']} - update data/sessions.json")

# ---- pull the current session, both houses, all four ministries ----------------
pending = []
for label, ls_code, rs_code, keep in MINISTRIES:
    # RS: single unpaginated call per ministry
    d = get(f"https://rsdoc.nic.in/Question/Search_Questions?whereclause=ses_no={cur['rs_session']}%20and%20min_code=%27{rs_code}%27")
    if d is None:
        report['api_failures'].append(f'RS {label}')
    else:
        report['fetched'][f'RS/{label}'] = len(d)
        for q in d:
            # rsdoc emits '?' for unencodable unicode (e.g. soft hyphens) - scrub the artifact
            title = (q.get('qtitle') or '').replace('??', '').strip()
            if not title: continue
            typ = 'S' if ('STARRED' in (q.get('qtype') or '') and 'UN' not in (q.get('qtype') or '')) else 'U'
            mp = clean_mp((q.get('name') or '').strip(), (q.get('shri') or '').strip())
            rec = {'h': 'RS', 'l': '', 's': str(cur['rs_session']), 'q': str(q.get('qno') or '').replace('.0', '').strip(),
                   't': typ, 'd': iso(q.get('ans_date')), 'm': [mp] if mp else [], 'j': title,
                   'g': tag_for(title, label), 'u': (q.get('files') or '').strip(), 'min': label}
            k = record_key(rec)
            if k in existing or k in decisions: continue
            pending.append({'record': rec, 'keyword_verdict': bool(keep(title))})
    time.sleep(0.2)

    # LS: paginated; CRITICAL - the working session param is sessionNumber
    # (sessionNo is silently ignored and returns the whole Lok Sabha)
    base = (f"https://sansad.in/api_ls/question/qetFilteredQuestionsAns?loksabhaNo={cur['ls_lk']}"
            f"&sessionNumber={cur['ls_session']}&ministryCode={ls_code}&locale=en&pageSize=100&pageNo=")
    first = get(base + '1')
    if first is None:
        report['api_failures'].append(f'LS {label}')
    else:
        rows = []
        if first and isinstance(first, list) and first[0].get('listOfQuestions'):
            total = first[0]['totalRecordSize']; rows = list(first[0]['listOfQuestions'])
            for p in range(2, (total + 99) // 100 + 1):
                dd = get(base + str(p)); time.sleep(0.1)
                if dd and dd[0].get('listOfQuestions'): rows += dd[0]['listOfQuestions']
        report['fetched'][f'LS/{label}'] = len(rows)
        for q in rows:
            title = (q.get('subjects') or '').strip()
            if not title: continue
            # defensive: if the API ignored our session filter, drop out-of-session rows
            if str(q.get('sessionNo') or cur['ls_session']) != str(cur['ls_session']): continue
            typ = 'S' if ('STARRED' in (q.get('type') or '') and 'UN' not in (q.get('type') or '')) else 'U'
            mps = [clean_mp(m) for m in (q.get('member') or []) if m]
            rec = {'h': 'LS', 'l': str(cur['ls_lk']), 's': str(cur['ls_session']), 'q': str(q.get('quesNo') or '').strip(),
                   't': typ, 'd': iso(q.get('date')), 'm': mps, 'j': title,
                   'g': tag_for(title, label), 'u': (q.get('questionsFilePath') or '').strip(), 'min': label}
            k = record_key(rec)
            if k in existing or k in decisions: continue
            pending.append({'record': rec, 'keyword_verdict': bool(keep(title))})
    time.sleep(0.2)

# dedupe within the staged batch itself
seen = {}
for p in pending:
    seen.setdefault(record_key(p['record']), p)
pending = list(seen.values())

report['new_candidates'] = len(pending)
report['keyword_included'] = sum(1 for p in pending if p['keyword_verdict'])
save_json(DATA / 'pending_curation.json', pending)
save_json(DATA / 'refresh_report.json', report)
print(f"delta_refresh: {report['fetched']} | new candidates: {len(pending)} "
      f"(keyword-included {report['keyword_included']}) | failures: {report['api_failures']}")
if report['rollover_alert']:
    print('ROLLOVER ALERT:', report['rollover_alert'])
# API failures are not fatal here (partial data just stays pending);
# sanity_check.py decides whether the run is publishable.
sys.exit(0)
