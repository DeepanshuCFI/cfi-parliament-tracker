#!/usr/bin/env python3
"""Fetch answer TEXT for records in the dataset, into a local cache.

LOCAL-ONLY - never wired into CI. The cache (data/answers_cache/) is
gitignored and re-fetchable; only grading VERDICTS (data/answer_grades.json,
written by the grading pass described in pipeline/GRADING.md) are committed.

Sources:
  RS - rsdoc Search_Questions carries full answer text (ans_text) per record;
       one unfiltered ses_no call per session covers all four ministries.
  LS - the API's answerText is null; we download each record's answer PDF
       (the 'u' field) and extract its text with PyMuPDF.

Usage:
  python3 pipeline/fetch_answers.py                 # current session only
  python3 pipeline/fetch_answers.py --all           # every record (backfill)
  python3 pipeline/fetch_answers.py --all --limit 200   # paced backfill
"""
import json, re, subprocess, sys, time
from pathlib import Path
from common import DATA, MINISTRIES, get, load_json, save_json, record_key

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
CACHE = DATA / 'answers_cache'
CACHE.mkdir(exist_ok=True)
MAX_CHARS = 12000

args = sys.argv[1:]
do_all = '--all' in args
limit = int(args[args.index('--limit') + 1]) if '--limit' in args else None

dataset = load_json(DATA / 'dataset.json')
sessions = load_json(DATA / 'sessions.json')
cur = sessions['current']

recs = dataset['records']
if not do_all:
    recs = [r for r in recs if
            (r['h'] == 'LS' and r.get('l') == str(cur['ls_lk']) and r['s'] == str(cur['ls_session'])) or
            (r['h'] == 'RS' and r['s'] == str(cur['rs_session']))]

def shard_path(r):
    return CACHE / (f"LS{r['l']}s{r['s']}.json" if r['h'] == 'LS' else f"RSs{r['s']}.json")

shards = {}
def shard(r):
    p = shard_path(r)
    if p not in shards:
        shards[p] = load_json(p, {})
    return shards[p]

def scrub(t):
    return ' '.join((t or '').replace('??', '').split())[:MAX_CHARS]

def fetch_pdf_text(url):
    """GET (sansad 403s HEAD) then extract text; None on any failure."""
    try:
        out = subprocess.run(['curl', '-sL', '--max-time', '60', '-A', UA, url],
                             capture_output=True, timeout=70).stdout
        if not out or not out.startswith(b'%PDF'):
            return None
        import fitz
        with fitz.open(stream=out, filetype='pdf') as doc:
            return scrub(' '.join(pg.get_text() for pg in doc))
    except Exception:
        return None

todo = [r for r in recs if record_key(r) not in shard(r)]
if limit:
    todo = todo[:limit]
print(f"fetch_answers: {len(recs)} in scope, {len(todo)} to fetch")

# ---- RS: one unfiltered session pull serves every RS record in that session ----
# The pull spans ALL ministries, starred + unstarred, and both numbering series
# restart from 1 each session - so qno alone COLLIDES (e.g. session 249 has
# MoRTH starred 151 and Defence unstarred 151). Key by (qno, S/U, min_code);
# a bare-qno dict silently served 28 starred records another ministry's answer.
RS_MIN = {label: str(rs_code) for label, _ls, rs_code, _fn in MINISTRIES}

def rs_row_key(q):
    qno = str(q.get('qno') or '').replace('.0', '').strip()
    qtype = 'S' if str(q.get('qtype') or '').strip().upper().startswith('S') else 'U'
    return (qno, qtype, str(q.get('min_code') or '').strip())

rs_sessions = {r['s'] for r in todo if r['h'] == 'RS'}
rs_by_session = {}
for s in sorted(rs_sessions):
    d = get(f"https://rsdoc.nic.in/Question/Search_Questions?whereclause=ses_no={s}")
    if isinstance(d, list):
        rs_by_session[s] = {rs_row_key(q): q for q in d if isinstance(q, dict)}
    else:
        print(f"  RS session {s}: pull FAILED (records stay pending)")
    time.sleep(0.3)

done = failed = 0
for r in todo:
    k, sh = record_key(r), shard(r)
    text = src = None
    if r['h'] == 'RS':
        q = rs_by_session.get(r['s'], {}).get((r['q'], r['t'], RS_MIN[r['min']]))
        api_text = scrub(q.get('ans_text')) if q else ''
        # Starred stubs ("A statement is laid on the Table of the House") carry
        # neither question nor answer - the statement itself is in the PDF.
        stub = len(api_text) < 400 and re.search(r'statement is (being )?laid on the table', api_text, re.I)
        if api_text and not stub:
            text, src = api_text, 'rs_api'
        elif r.get('u'):                       # RS fallback: answer PDF
            text, src = fetch_pdf_text(r['u']), 'rs_pdf'
            time.sleep(0.3)
    elif r.get('u'):
        text, src = fetch_pdf_text(r['u']), 'ls_pdf'
        time.sleep(0.4)
    if text:
        sh[k] = {'t': text, 'src': src, 'j': r['j']}
        done += 1
    else:
        failed += 1

for p, sh in shards.items():
    save_json(p, sh)
total_cached = sum(len(load_json(p, {})) for p in CACHE.glob('*.json'))
print(f"fetch_answers: +{done} fetched, {failed} unavailable, cache now {total_cached} answers")
