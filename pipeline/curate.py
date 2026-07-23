#!/usr/bin/env python3
"""Commit staged questions into the dataset, with a Claude review of borderline calls.

Why an LLM pass at all: the original scrape missed ~25% of questions because
keyword filters under-capture; the approved scope ("anything associated with road
safety; exclude trade agreements, vehicle tax, pure congestion") is a judgment
call. Claude Haiku reviews every NEW title (with the keyword verdict as prior)
and can override in either direction. Overrides + reasons are logged.

HARD BUDGET CAP: monthly Anthropic spend is tracked in data/curation_state.json
and the LLM is skipped once estimated spend reaches USD_CAP (~INR 100/month).
Fallback (no API key / over budget / API error): keyword verdicts apply and the
batch is flagged needs_review in data/curation_log.json. The refresh still
publishes either way - curation degrades, it never blocks.
"""
import json, os, sys, time
from common import DATA, load_json, save_json, record_key

MODEL = 'claude-haiku-4-5'
IN_USD_PER_TOK = 1.00 / 1_000_000   # Haiku 4.5 input
OUT_USD_PER_TOK = 5.00 / 1_000_000  # Haiku 4.5 output
USD_CAP = 1.10                       # ~ INR 96/month hard ceiling
MAX_TITLES_PER_RUN = 400
MAX_TOKENS = 8000

SCOPE = """You curate a public dataset: every parliamentary question (Lok Sabha + Rajya Sabha) associated with ROAD SAFETY in India, across four ministries.

INCLUDE (inclusive scope, approved by the editor): anything associated with road safety - crashes/accidents/fatalities, the Motor Vehicles Act and rules, road design/engineering/black spots, enforcement (challans, licensing, speeding, drink-driving), helmets/seatbelts/vehicle safety standards/NCAP/recalls, pedestrians/cyclists/footpaths, trauma care/ambulances/golden hour/Good Samaritan/cashless treatment/compensation for crash victims, road safety policy/schemes/data.
EXCLUDE: cross-border trade or vehicle agreements (BBIN, Nepal/Bhutan/Bangladesh), vehicle taxation/GST, toll & FASTag revenue matters, pure congestion/transport-capacity questions with no safety angle, occupational/factory safety, disease or non-road health matters.

Per ministry context: MoRTH questions need a road-safety angle (not pure highway construction/finance). Health questions must be about post-crash care (trauma/ambulance/victims), not general health. Heavy Industries must be about vehicle crashworthiness/safety standards, not production. Urban must be about pedestrian/NMT/street safety, not general urban infrastructure.

You are given question titles with a keyword-filter verdict as a prior. Override ONLY when confident the keyword call is wrong. Be inclusive on genuine borderline road-safety matters."""

def apply(pending, verdicts, source, log_notes):
    """Apply final verdicts: append accepted records to the dataset, log every decision."""
    dataset = load_json(DATA / 'dataset.json')
    decisions = load_json(DATA / 'curation_decisions.json', {})
    existing = {record_key(r) for r in dataset['records']}
    added = 0
    for p, keep in zip(pending, verdicts):
        k = record_key(p['record'])
        decisions[k] = {'include': bool(keep), 'title': p['record']['j'],
                        'ministry': p['record']['min'], 'source': source}
        if keep and k not in existing:
            dataset['records'].append(p['record']); existing.add(k); added += 1
    dataset['records'].sort(key=lambda r: r['d'] or '0', reverse=True)
    save_json(DATA / 'dataset.json', dataset, compact=True)
    save_json(DATA / 'curation_decisions.json', decisions)
    log = load_json(DATA / 'curation_log.json', {'runs': []})
    log['runs'] = (log['runs'] + [{'candidates': len(pending), 'added': added,
                                   'source': source, 'notes': log_notes}])[-60:]
    save_json(DATA / 'curation_log.json', log)
    save_json(DATA / 'pending_curation.json', [])
    print(f'curate: {len(pending)} candidates -> {added} added ({source}) {log_notes}')

def main():
    pending = load_json(DATA / 'pending_curation.json', [])
    if not pending:
        print('curate: nothing staged'); return
    pending = pending[:MAX_TITLES_PER_RUN]
    kw = [p['keyword_verdict'] for p in pending]

    # ---- budget state (monthly) ----
    month = time.strftime('%Y-%m')
    state = load_json(DATA / 'curation_state.json', {})
    if state.get('month') != month:
        state = {'month': month, 'input_tokens': 0, 'output_tokens': 0, 'est_usd': 0.0}

    if not os.environ.get('ANTHROPIC_API_KEY'):
        apply(pending, kw, 'keyword-only (no API key)', 'needs_review'); return
    if state['est_usd'] >= USD_CAP:
        apply(pending, kw, 'keyword-only (budget cap reached)',
              f"needs_review: spent ${state['est_usd']:.2f} this month"); return

    try:
        import anthropic
        client = anthropic.Anthropic()
        titles = [{'i': i, 'ministry': p['record']['min'], 'title': p['record']['j'],
                   'keyword_verdict': p['keyword_verdict']} for i, p in enumerate(pending)]
        schema = {
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
        resp = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, system=SCOPE,
            output_config={'format': {'type': 'json_schema', 'schema': schema}},
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
            apply(pending, kw, 'keyword-only (LLM truncated)', 'needs_review'); return
        text = next(b.text for b in resp.content if b.type == 'text')
        by_i = {d['i']: d for d in json.loads(text)['decisions']}
        final, overrides = [], []
        for i, p in enumerate(pending):
            d = by_i.get(i)
            v = d['include'] if d else p['keyword_verdict']
            final.append(v)
            if d and v != p['keyword_verdict']:
                overrides.append({'title': p['record']['j'], 'ministry': p['record']['min'],
                                  'keyword': p['keyword_verdict'], 'llm': v, 'reason': d['reason']})
        note = f"overrides: {len(overrides)} | spend this month: ${state['est_usd']:.2f}"
        if overrides:
            log = load_json(DATA / 'curation_log.json', {'runs': []})
            log.setdefault('overrides', []).extend(overrides)
            log['overrides'] = log['overrides'][-200:]
            save_json(DATA / 'curation_log.json', log)
        apply(pending, final, f'keyword+{MODEL}', note)
    except Exception as e:
        # LLM failure never blocks the refresh
        apply(pending, kw, 'keyword-only (LLM error)', f'needs_review: {type(e).__name__}: {e}')

if __name__ == '__main__':
    main()
    sys.exit(0)
