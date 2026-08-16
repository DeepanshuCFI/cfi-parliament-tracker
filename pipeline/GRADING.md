# Answer grading — rubric v1

Grades the GOVERNMENT'S ANSWERS to road-safety questions (Green-Hour-style
response analysis, adapted from RTI Watch's response-grade taxonomy).
Grading runs LOCALLY on a Claude subscription session (Opus/Fable class —
Deep's call, 16 Aug 2026) — never in CI, never with API keys.

## Pipeline position

1. `python3 pipeline/fetch_answers.py [--all] [--limit N]` fills the local
   gitignored cache `data/answers_cache/<shard>.json` (`record_key -> {t, src, j}`).
   The text contains BOTH the question (clauses a/b/c/d) and the answer.
2. A Claude session reads ungraded cache entries and writes verdicts to
   `data/answer_grades.json` (committed). Never commit the cache.

## Verdict schema — data/answer_grades.json

```json
{"version": 1, "rubric": 1,
 "grades": {"<record_key>": {
   "da": true,          // question EXPLICITLY asks for data: counts, amounts,
                        // state-/district-/year-wise figures, lists, timelines
   "dg": "y|p|n",       // only when da=true, else omit. Did the answer provide
                        // the requested data? y = substantially provided;
                        // p = partial/different scope than asked (e.g. national
                        //     totals when district-wise was asked);
                        // n = none: refused, ignored, or "data not maintained"
   "sd": true,          // omit when false. Answer explicitly places the subject
                        // on state/UT governments ("subject of the State
                        // Government", "states are responsible", "falls under
                        // the purview of State Governments")
   "note": "...",       // <=140 chars, only when dg=n|p or sd=true: quote or
                        // paraphrase the load-bearing line
   "g": "YYYY-MM-DD", "m": "<model short-name>"
 }}}
```

## File serialisation (keep diffs readable)

No pipeline script writes `data/answer_grades.json` — the grading session does,
by hand. So the format is a convention, not something code enforces: write it
back with exactly this call, or every run reshuffles the whole file and the
diff stops showing which grades actually changed.

```python
json.dump(g, open(path, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
open(path, 'a').write('\n')   # trailing newline
```

- `sort_keys=True` — keys sorted at every level, so a batch appends in place
  instead of reordering; also makes the per-grade fields a fixed order
  (`da, dg, g, m, note, sd`).
- `ensure_ascii=False` — answer text quoted in notes is Devanagari-heavy;
  escaping it makes notes unreadable in review.
- `indent=1` — one record per few lines, cheap line-level diffs.
- Trailing newline — keeps `git diff` from flagging the last line every run.

## Judgment calls (keep these stable)

- `da` is about the QUESTION, graded from the question clauses in the same
  text. "Details thereof" alone is NOT a data ask; "the number of X",
  "state-wise details", "funds allocated and utilised" ARE.
- `dg=y` does not require every sub-clause answered — the substantive data
  asks, substantially. Annexures count as provided (the PDF text includes
  them; a referenced-but-missing annexure counts as `p`).
- `sd` is NOT set for factual mentions of state implementation roles — only
  when responsibility placement substitutes for an answer or dodges a clause.
- Silence on a data clause = `n` for that clause; grade `dg` on the whole.
- When genuinely borderline, prefer the grade kinder to the government —
  every published claim must survive an adversarial read (same rule as the
  never-asked framing).

## Consistency protocol

- Grade in batches; re-read this file at the start of every session.
- Never regrade existing keys (rubric bump = new file version, full regrade).
- After grading, run `python3 pipeline/grade_stats.py` for the aggregate;
  spot-check any batch where dg=n exceeds ~40% — that usually means the
  question text was misread as the answer.
