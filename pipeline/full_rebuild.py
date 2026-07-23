#!/usr/bin/env python3
"""MANUAL full rebuild (not part of CI - takes tens of minutes, hits every session
since 2014). Writes data/full_rebuild_output.json for hand-merging into dataset.json.
Run from repo root. RS session ceiling: env RS_MAX_SESSION (default 280).
CAUTION (audit 23 Jul 2026): this rebuild applies KEYWORD filters only. The live
dataset additionally contains LLM/editor-curated inclusions (e.g. pothole and
speed-limit titles the keywords miss) and excludes some keyword matches. NEVER
overwrite dataset.json with this output directly - reconcile against
data/curation_decisions.json first (apply include=True records the keywords
missed; drop include=False ones the keywords caught).
Build the COMPLETE dataset from sansad.in's official MoRTH question APIs.
Enumerates the full MoRTH universe, applies a calibrated inclusive road-safety title
filter, retags topics, and reconstructs answer-PDF links + member names."""
import json, subprocess, time, re, os
from collections import defaultdict

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'
def get(url, tries=3):
    for i in range(tries):
        try:
            out = subprocess.run(['curl','-sL','--max-time','90','-A',UA,'-H','Accept: application/json',url],
                                 capture_output=True, timeout=100).stdout
            return json.loads(out)
        except Exception:
            time.sleep(1.5)
    return None

# ---------- calibrated INCLUSIVE road-safety title filter ----------
INC = re.compile('|'.join([
    r'\bsafety\b', r'road accident', r'\baccident', r'fatalit', r'\bdeaths?\b', r'\bkilled\b', r'\bcrash',
    r'collision', r'helmet', r'seat ?belt', r'air ?bag', r'\bncap\b', r'drink[- ]?driv', r'drunk',
    r'\bhit[- ]and[- ]run\b', r'hit and run', r'pedestrian', r'black ?spot', r'trauma', r'good samaritan',
    r'golden hour', r'ambulance', r'emergency response', r'motor vehicle', r'road design', r'road engineering',
    r'\bsignage\b', r'crash barrier', r'guard ?rail', r'over[- ]?speed', r'over[- ]?load',
    r'two[- ]?wheeler', r'driving licen[cs]', r'driver training', r'e-?challan', r'\bchallan', r'vehicle fitness',
    r'road transport and safety', r'vehicle recall', r'safety recall', r'road ranking', r'ranking of nh',
    r'road safety', r'nrsb', r'national road safety', r'road worthiness', r'roadworthiness', r'lane driving',
    r'road rage', r'speed governor', r'speed limit', r'safe.*road',
    r'traffic (rule|violation|law|enforcement|police|signal|safety|calming|discipline|offen)',
    r'enforcement of traffic', r'violation of traffic',
]), re.I)
# hard excludes: title matches an include term but is genuinely off-topic (trade / tax / pure counts)
EXC = re.compile('|'.join([
    r'agreement with', r'\bbbin\b', r'bhutan', r'bangladesh|nepal', r'motor vehicles? agreement',
    r'\btax(es|ation)?\b', r'rationaliz.*tax', r'gst\b', r'registered motor vehicles?$',
    r'number of registered', r'import of|export of', r'fastag', r'toll (collection|plaza|revenue|rate)',
]), re.I)
def is_safety(title):
    t = title or ''
    if EXC.search(t) and not re.search(r'\bsafety\b|accident|fatal|crash|black ?spot|pedestrian|helmet|trauma|hit and run', t, re.I):
        return False
    return bool(INC.search(t))

# Health & Family Welfare: keep only the road-safety CONTEXT (post-crash care), not disease deaths.
HCTX = re.compile('|'.join([
    r'road accident', r'accident victim', r'\btrauma\b', r'golden hour', r'good samaritan',
    r'\bambulance', r'road crash', r'emergency medical', r'\bemt\b|emergency medical tech',
    r'injured in road', r'injury (surveillance|registr)', r'treatment.*(accident|injur)',
    r'cashless treatment', r'\b108\b', r'trauma (care|centre|center|registry|management)',
]), re.I)
HXC = re.compile(r'dead bod|carrying dead|women in labour|maternal|snakebite|encephalit|measles|sterili|dengue|malaria|cancer patient|\bwaste\b|recycl', re.I)
def is_health_safety(title):
    t = title or ''
    return bool(HCTX.search(t)) and not HXC.search(t)

# Heavy Industries: vehicle crashworthiness / safety standards.
VCTX = re.compile('|'.join([
    r'safety (standard|norm|rating|feature|device|test)', r'\bncap\b', r'air ?bag', r'crashworth',
    r'vehicle recall', r'recall (policy|of vehicles)', r'car safety', r'automobile safety',
    r'vehicle safety', r'passenger safety', r'safety (of|in) (cars|vehicles|passengers)',
    r'road accident', r'four wheeler', r'international safety',
]), re.I)
VXC = re.compile(r'occupational safety|safety in public sector|factory|plant safety', re.I)
def is_heavy_safety(title):
    t = title or ''
    return bool(VCTX.search(t)) and not VXC.search(t)

# Housing & Urban Affairs: urban pedestrian / footpath / non-motorised-transport safety.
UUCTX = re.compile('|'.join([
    r'pedestrian', r'footpath', r'foot[- ]?over', r'walkab', r'non[- ]?motor',
    r'\bnmt\b', r'\bcycl(e|es|ing|ist)', r'bicycle', r'zebra cross', r'road cross',
    r'traffic calm', r'street (design|scap|safe)', r'complete street',
]), re.I)
UUXC = re.compile(r'\bwaste\b|recycl|rickshaw|metro rail|rapid transit|last mile|sewage|drainage', re.I)
def is_urban_safety(title):
    t = title or ''
    return bool(UUCTX.search(t)) and not UUXC.search(t)

# ministry registry: label -> (LS ministryCode, RS min_code, keep-fn)
MINISTRIES = [
    ('MoRTH',  55, 65, is_safety),
    ('Health', 32, 32, is_health_safety),
    ('Heavy',   9, 45, is_heavy_safety),
    ('Urban',  60,110, is_urban_safety),
]
MIN_FULL = {'MoRTH':'Road Transport & Highways','Health':'Health & Family Welfare',
            'Heavy':'Heavy Industries','Urban':'Housing & Urban Affairs'}

# ---------- topic tagging (title-based, multi-label) ----------
TAGS = ['Accidents & Fatalities','Road Safety (General)','Road Safety Policy','Trauma Care & Compensation',
        'Vehicle Safety Standards','Black Spots & Infrastructure','Pedestrian Safety','Data & Reporting',
        'Drunk/Drink Driving','Hit and Run','Motor Vehicles Act & Rules','Enforcement & Licensing']
def tag(title):
    t = (title or '').lower(); g = []
    if re.search(r'accident|fatal|death|killed|crash|collision|lives lost', t): g.append(0)
    if re.search(r'road safety|safety measure|safety on|safe road|safety of road|safety issue|road worthiness', t): g.append(1)
    if re.search(r'policy|scheme|programme|plan|nrsb|national road safety|bill|strategy|target|vision', t): g.append(2)
    if re.search(r'trauma|good samaritan|golden hour|ambulance|emergency|compensation|cashless|victim', t): g.append(3)
    if re.search(r'helmet|seat ?belt|air ?bag|ncap|vehicle safety|safety (device|feature|standard|norm)|fitness|recall|safety in (cars|vehicles|buses)|car safety', t): g.append(4)
    if re.search(r'black ?spot|infrastructure|road design|engineering|signage|crash barrier|guard ?rail|road maintenance|bridge|tunnel|junction', t): g.append(5)
    if re.search(r'pedestrian|footpath|zebra|foot over', t): g.append(6)
    if re.search(r'\bdata\b|report|statistic|survey|number of|ranking', t): g.append(7)
    if re.search(r'drink[- ]?driv|drunk|alcohol|blood alcohol', t): g.append(8)
    if re.search(r'hit[- ]and[- ]run|hit and run', t): g.append(9)
    if re.search(r'motor vehicle', t): g.append(10)
    if re.search(r'challan|licen[cs]|enforcement|penalt|fine|traffic (rule|violation|police|management)|speed governor|over[- ]?speed|over[- ]?load|lane driving|road rage', t): g.append(11)
    return g or [1]
def tag_for(title, minlabel):
    g = tag(title)
    if minlabel == 'Health' and 3 not in g: g.append(3)     # Trauma Care & Compensation
    if minlabel == 'Heavy' and 4 not in g: g.append(4)      # Vehicle Safety Standards
    if minlabel == 'Urban' and 6 not in g: g.append(6)      # Pedestrian Safety
    return g

def iso(d):
    d = (d or '').strip()
    m = re.match(r'(\d{2})[.\-/](\d{2})[.\-/](\d{4})', d)
    if m: return f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', d)
    if m: return m.group(0)
    return ''

HON = re.compile(r'^(shri|smt|smt\.|dr|dr\.|prof|prof\.|kumari|km|sardar|adv|ms|mr|mrs|sushri|shrimati|thiru|justice|col|capt|maj|gen)\.?\s+', re.I)
def clean_mp(name, prefix=''):
    n = f'{prefix} {name}'.strip() if prefix else name
    n = re.sub(r'\s+', ' ', n).strip()
    prev = None
    while prev != n:
        prev = n; n = HON.sub('', n).strip()
    return n

import os
records = []

# session metadata for LS
sess_meta = get("https://sansad.in/api_ls/business/getAllLoksabhaAndSession?locale=en")
lk_sessions = defaultdict(set)
def walk(o):
    if isinstance(o, dict):
        lk = o.get('loksabhaNo') or o.get('lokSabhaNo'); sn = o.get('sessionNumber') or o.get('sessionNo')
        if lk and sn:
            try: lk_sessions[int(lk)].add(int(sn))
            except: pass
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(sess_meta)

for label, ls_code, rs_code, keep in MINISTRIES:
    # ----- RS via rsdoc -----
    rs_kept = 0
    for ses in range(232, int(os.environ.get('RS_MAX_SESSION', '280'))):
        d = get(f"https://rsdoc.nic.in/Question/Search_Questions?whereclause=ses_no={ses}%20and%20min_code=%27{rs_code}%27")
        if not d: print(f'  [{label}] RS ses {ses} FAILED'); continue
        for q in d:
            title = (q.get('qtitle') or '').strip()
            if not keep(title): continue
            typ = 'S' if ('STARRED' in (q.get('qtype') or '') and 'UN' not in (q.get('qtype') or '')) else 'U'
            mp = clean_mp((q.get('name') or '').strip(), (q.get('shri') or '').strip())
            records.append({'h':'RS','l':'','s':str(ses),'q':str(q.get('qno') or '').replace('.0','').strip(),
                            't':typ,'d':iso(q.get('ans_date')),'m':[mp] if mp else [],'j':title,
                            'g':tag_for(title,label),'u':(q.get('files') or '').strip(),'min':label})
            rs_kept += 1
        time.sleep(0.15)
    # ----- LS via api_ls -----
    ls_kept = 0
    for lk in (16,17,18):
        for sn in sorted(lk_sessions.get(lk) or set(range(1,18))):
            base = f"https://sansad.in/api_ls/question/qetFilteredQuestionsAns?loksabhaNo={lk}&sessionNumber={sn}&ministryCode={ls_code}&locale=en&pageSize=100&pageNo="
            first = get(base+'1')
            if not first or not first[0].get('listOfQuestions'): continue
            total = first[0]['totalRecordSize']; rows = list(first[0]['listOfQuestions'])
            for p in range(2, (total+99)//100+1):
                dd = get(base+str(p)); time.sleep(0.1)
                if dd and dd[0].get('listOfQuestions'): rows += dd[0]['listOfQuestions']
            for q in rows:
                title = (q.get('subjects') or '').strip()
                if not keep(title): continue
                typ = 'S' if ('STARRED' in (q.get('type') or '') and 'UN' not in (q.get('type') or '')) else 'U'
                mps = [clean_mp(m) for m in (q.get('member') or []) if m]
                records.append({'h':'LS','l':str(lk),'s':str(q.get('sessionNo') or sn),'q':str(q.get('quesNo') or '').strip(),
                                't':typ,'d':iso(q.get('date')),'m':mps,'j':title,'g':tag_for(title,label),
                                'u':(q.get('questionsFilePath') or '').strip(),'min':label})
                ls_kept += 1
            time.sleep(0.12)
    print(f'[{label}] kept RS {rs_kept} + LS {ls_kept} = {rs_kept+ls_kept}')

# ---------- dedupe (by house+ministry+session+type+qno) & finalize ----------
seen = {}
for r in records:
    k = (r['h'], r['l'], r['min'], r['s'], r['t'], r['q'])  # 'l': LS session numbers restart per Lok Sabha
    if k not in seen: seen[k] = r
records = list(seen.values())
records.sort(key=lambda r: r['d'] or '0', reverse=True)
print('\nTOTAL v3.0 records:', len(records))

from collections import Counter
print('by ministry:', dict(Counter(r['min'] for r in records)))
tc = Counter()
for r in records:
    for gi in r['g']: tc[TAGS[gi]] += 1
print('topic counts:', dict(tc))
print('with PDF:', sum(1 for r in records if r['u'].startswith('http')))
print('distinct MP names:', len(set(m for r in records for m in r['m'])))
print('houses:', dict(Counter(r['h'] for r in records)))
print('hit-and-run:', sum(1 for r in records if 9 in r['g']), '| pedestrian:', sum(1 for r in records if 6 in r['g']))

json.dump({'version':'3.0','tags':TAGS,'ministries':MIN_FULL,'records':records},
          open('data/full_rebuild_output.json','w'), separators=(',',':'), ensure_ascii=False)
print('saved parl_data_v3.json')
