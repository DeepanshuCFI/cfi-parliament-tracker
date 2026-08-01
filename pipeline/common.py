#!/usr/bin/env python3
"""Shared machinery for the Road Safety in Parliament pipeline.

Filters, tagging, date/name normalisation and the HTTP fetch layer are ported
verbatim from the original build_v3.py (parliament-tracker-launch/data/) so a
delta refresh classifies titles exactly the way the full build did.
All paths are repo-relative so this runs identically on a Mac and in CI.
"""
import json, re, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
SITE = ROOT / 'site'

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'

def get(url, tries=3):
    """Fetch JSON via curl (NIC hosts reject default python UAs). Returns None on failure."""
    for i in range(tries):
        try:
            out = subprocess.run(
                ['curl', '-sL', '--max-time', '90', '-A', UA,
                 '-H', 'Accept: application/json', '-H', 'Referer: https://sansad.in/', url],
                capture_output=True, timeout=100).stdout
            return json.loads(out)
        except Exception:
            time.sleep(1.5)
    return None

# ---------- calibrated INCLUSIVE road-safety title filter (MoRTH) ----------
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
    ('Urban',  60, 110, is_urban_safety),
]
MIN_FULL = {'MoRTH': 'Road Transport & Highways', 'Health': 'Health & Family Welfare',
            'Heavy': 'Heavy Industries', 'Urban': 'Housing & Urban Affairs'}

TAGS = ['Accidents & Fatalities', 'Road Safety (General)', 'Road Safety Policy', 'Trauma Care & Compensation',
        'Vehicle Safety Standards', 'Black Spots & Infrastructure', 'Pedestrian Safety', 'Data & Reporting',
        'Drunk/Drink Driving', 'Hit and Run', 'Motor Vehicles Act & Rules', 'Enforcement & Licensing']

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
    if minlabel == 'Health' and 3 not in g: g.append(3)
    if minlabel == 'Heavy' and 4 not in g: g.append(4)
    if minlabel == 'Urban' and 6 not in g: g.append(6)
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

def photo_url(img):
    """Upstream URL for an ENRICH img id, mirroring the /mpimg/ rewrites."""
    if str(img).startswith('rs/'):
        return f'https://sansad.in/getFile/newmembers/photos/{str(img)[3:]}?source=rajyasabha'
    return f'https://sansad.in/getFile/dms/fetch/{img}?source=dsp2'

def probe_image(img):
    """(ok, '<code> <type> <bytes>') for one photo id.

    GET, not HEAD: sansad answers HEAD with 403 for every file. The content type
    is checked too, so an HTML error page served as 200 does not pass.
    """
    r = subprocess.run(['curl', '-s', '-o', '/dev/null', '--max-time', '45', '-A', UA,
                        '-w', '%{http_code} %{content_type} %{size_download}',
                        photo_url(img)], capture_output=True, text=True)
    v = r.stdout.strip(); p = v.split()
    return (len(p) == 3 and p[0] == '200' and p[1].startswith('image/')
            and int(p[2]) > 1000), v

HON_TOK = {'shri', 'smt', 'dr', 'prof', 'kumari', 'km', 'sardar', 'adv', 'ms', 'mr',
           'mrs', 'sushri', 'shrimata', 'shrimati', 'thiru', 'justice', 'col', 'capt', 'maj', 'gen'}
def name_tokens(s):
    """Order-free, honorific-free key for matching one MP across sources.

    Sansad returns names comma-flipped with honorifics ("Kumar, Shri Mithlesh")
    where the dataset carries plain form ("Mithlesh Kumar"); a sorted token set
    matches those without a fuzzy pass. Single letters are dropped, so initials
    do NOT distinguish members - "C.R. / P P / R K Chaudhary" all key to
    ('chaudhary',). Every caller must therefore carry a homonym guard: never
    resolve an ambiguous key by taking the first hit. See docs/PAGE-BUILD.md.
    """
    toks = re.findall(r'[a-z]+', (s or '').lower())
    return tuple(sorted(t for t in toks if t not in HON_TOK and len(t) > 1))

def state_key(s):
    """Connective-free state key ('Jammu and Kashmir' == 'Jammu & Kashmir')."""
    return ' '.join(t for t in re.findall(r'[a-z]+', (s or '').lower())
                    if t not in ('and', 'of', 'the'))

def record_key(r):
    # 'l' (Lok Sabha number) is load-bearing: LS session numbers restart each
    # Lok Sabha, so without it an LS18 question collides with an LS16/17 record
    # of the same session+ministry+type+number and is silently dropped.
    return f"{r['h']}|{r['l']}|{r['min']}|{r['s']}|{r['t']}|{r['q']}"

def record_id(r):
    if r['h'] == 'LS':
        return f"LS{r['l']}-{r['min']}-S{r['s']}-{r['t']}{r['q']}"
    return f"RS-{r['min']}-S{r['s']}-{r['t']}{r['q']}"

def load_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text())

def save_json(path, obj, compact=False):
    kw = {'separators': (',', ':')} if compact else {'indent': 2}
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, **kw))
