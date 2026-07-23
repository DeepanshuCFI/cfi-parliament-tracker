#!/usr/bin/env python3
"""Commit staged questions into the dataset, with a Claude review of borderline calls.

Why an LLM pass at all: the original scrape missed ~25% of questions because
keyword filters under-capture; the approved scope ("anything associated with road
safety; exclude trade agreements, vehicle tax, pure congestion") is a judgment
call. Claude Haiku reviews every NEW title (with the keyword verdict as prior)
and can override in either direction. Overrides + reasons are logged.

Titles are sent in CHUNKS of 100 so one oversized batch can never blow the
max_tokens ceiling and drag every already-decided title down with it; a chunk
that degrades (truncation, API error, budget cap) falls back to keyword verdicts
for that chunk only.

Verdict permanence: LLM-reviewed verdicts are sealed in curation_decisions.json.
Degraded keyword-only verdicts seal only their INCLUDES (keyword-in is high
precision); their excludes are left undecided so the titles re-stage on the next
run and get a real review once the LLM is available again.

HARD BUDGET CAP: monthly Anthropic spend is tracked in data/curation_state.json
and the LLM is skipped once estimated spend reaches USD_CAP (~INR 100/month).
Curation degrades; it never blocks the refresh.
"""
import json, os, sys, time
from common import DATA, load_json, save_json, record_key

MODEL = 'claude-haiku-4-5'
IN_USD_PER_TOK = 1.00 / 1_000_000   # Haiku 4.5 input
OUT_USD_PER_TOK = 5.00 / 1_000_000  # Haiku 4.5 output
USD_CAP = 1.10                       # ~ INR 96/month hard ceiling
CHUNK = 100                          # titles per API call (~25 out-tokens each)
MAX_TOKENS = 8000

SCOPE = """You curate a public dataset: every parliamentary question (Lok Sabha + Rajya Sabha) associated with ROAD SAFETY in India, across four ministries.

INCLUDE (inclusive scope, approved by the editor): anything associated with road safety - crashes/accidents/fatalities, the Motor Vehicles Act and rules, road design/engineering/black spots, enforcement (challans, licensing, speeding, drink-driving), helmets/seatbelts/vehicle safety standards/NCAP/recalls, pedestrians/cyclists/footpaths, trauma care/ambulances/golden hour/Good Samaritan/cashless treatment/compensation for crash victims, road safety policy/schemes/data.
EXCLUDE: cross-border trade or vehicle agreements (BBIN, Nepal/Bhutan/Bangladesh), vehicle taxation/GST, toll & FASTag revenue matters, pure congestion/transport-capacity questions with no safety angle, occupational/factory safety, disease or non-road health matters.

Per ministry context: MoRTH questions need a road-safety angle (not pure highway construction/finance). Health questions must be about post-crash care (trauma/ambulance/victims), not general health. Heavy Industries must be about vehicle crashworthiness/safety standards, not production. Urban must be about pedestrian/NMT/street safety, not general urban infrastructure.

You are given question titles with a keyword-filter verdict as a prior. Override ONLY when confident the keyword call is wrong. Be inclusive on genuine borderline road-safety matters."""

SCHEMA = {
    'type': 'object',
    'properties': {
        'decisions': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'i': {'type': 'integer'},
                    'include': {'type': 'boolean'},
                    'reason': {'type': 'string'},
                },
                'required': ['i', 'include', 'reason'],
                'additionalProperties': False,
            },
        },
    },
    'required': ['decisions'],
    'additionalProperties': False,
}


def apply(pending, verdicts, source, log_notes, sealed=None):
    """Apply final verdicts. sealed[i]=False means: if the verdict is EXCLUDE,
    write no decision so the title re-stages for a real review next run."""
    dataset = load_json(DATA / 'dataset.json')
    decisions = load_json(DATA / 'curation_decisions.json', {})
    existing = {record_key(r) for r in dataset['records']}
    added = deferred = 0
    for i, (p, keep) in enumerate(zip(pending, verdicts)):
        k = record_key(p['record'])
        seal = sealed[i] if sealed is not None else True
        if keep:
            decisions[k] = {'include': True, 'title': p['record']['j'],
                            'ministry': p['record']['min'], 'source': source}
            if k not in existing:
                dataset['records'].append(p['record']); existing.add(k); added += 1
        elif seal:
            decisions[k] = {'include': False, 'title': p['record']['j'],
                            'ministry': p['record']['min'], 'source': source}
        else:
            deferred += 1
    dataset['records'].sort(key=lambda r: r['d'] or '0', reverse=True)
    save_json(DATA / 'dataset.json', dataset, compact=True)
    save_json(DATA / 'curation_decisions.json', decisions)
    log = load_json(DATA / 'curation_log.json', {'runs': []})
    log['runs'] = (log['runs'] + [{'candidates': len(pending), 'added': added,
                                   'deferred_excludes': deferred,
                                   'source': source, 'notes': log_notes}])[-60:]
    save_json(DATA / 'curation_log.json', log)
    save_json(DATA / 'pending_curation.json', [])
    print(f'curate: {len(pending)} candidates -> {added} added, {deferred} excludes '
          f'deferred for re-review ({source}) {log_notes}')


def main():
    pending = load_json(DATA / 'pending_curation.json', [])
    if not pending:
        print('curate: nothing staged'); return
    kw = [p['keyword_verdict'] for p in pending]

    month = time.strftime('%Y-%m')
    state = load_json(DATA / 'curation_state.json', {})
    if state.get('month') != month:
        state = {'month': month, 'input_tokens': 0, 'output_tokens': 0, 'est_usd': 0.0}

    if not os.environ.get('ANTHROPIC_API_KEY'):
        apply(pending, kw, 'keyword-only (no API key)', 'needs_review',
              sealed=[False] * len(pending)); return

    try:
        import anthropic
        client = anthropic.Anthropic()
    except Exception as e:
        apply(pending, kw, 'keyword-only (SDK unavailable)', f'needs_review: {e}',
              sealed=[False] * len(pending)); return

    final = list(kw)
    sealed = [False] * len(pending)   # flipped to True chunk-by-chunk on LLM success
    overrides, degraded = [], []

    for c0 in range(0, len(pending), CHUNK):
        chunk = pending[c0:c0 + CHUNK]
        if state['est_usd'] >= USD_CAP:
            degraded.append(f'chunk@{c0}: budget cap (${state["est_usd"]:.2f})'); continue
        titles = [{'i': i, 'ministry': p['record']['min'], 'title': p['record']['j'],
                   'keyword_verdict': p['keyword_verdict']} for i, p in enumerate(chunk)]
        try:
            resp = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS, system=SCOPE,
                output_config={'format': {'type': 'json_schema', 'schema': SCHEMA}},
                messages=[{'role': 'user', 'content':
                           'Decide include/exclude for each title. Return one decision per item, '
                           'keeping reasons under 12 words:\n' + json.dumps(titles, ensure_ascii=False)}],
            )
            state['input_tokens'] += resp.usage.input_tokens
            state['output_tokens'] += resp.usage.output_tokens
            state['est_usd'] = round(state['input_tokens'] * IN_USD_PER_TOK
                                     + state['output_tokens'] * OUT_USD_PER_TOK, 4)
            save_json(DATA / 'curation_state.json', state)
            if resp.stop_reason == 'max_tokens':
                degraded.append(f'chunk@{c0}: truncated'); continue
            text = next(b.text for b in resp.content if b.type == 'text')
            by_i = {d['i']: d for d in json.loads(text)['decisions']}
            for i, p in enumerate(chunk):
                d = by_i.get(i)
                if d is None: continue          # missing item stays keyword+unsealed
                final[c0 + i] = d['include']
                sealed[c0 + i] = True
                if d['include'] != p['keyword_verdict']:
                    overrides.append({'title': p['record']['j'], 'ministry': p['record']['min'],
                                      'keyword': p['keyword_verdict'], 'llm': d['include'],
                                      'reason': d['reason']})
        except Exception as e:
            degraded.append(f'chunk@{c0}: {type(e).__name__}: {e}')

    if overrides:
        log = load_json(DATA / 'curation_log.json', {'runs': []})
        log.setdefault('overrides', []).extend(overrides)
        log['overrides'] = log['overrides'][-200:]
        save_json(DATA / 'curation_log.json', log)

    n_llm = sum(sealed)
    source = f'keyword+{MODEL}' if n_llm else 'keyword-only (all chunks degraded)'
    note = (f'llm-reviewed {n_llm}/{len(pending)} | overrides: {len(overrides)} | '
            f'spend this month: ${state["est_usd"]:.2f}')
    if degraded:
        note += ' | needs_review: ' + '; '.join(degraded)
    apply(pending, final, source, note, sealed=sealed)


if __name__ == '__main__':
    main()
    sys.exit(0)
