#!/usr/bin/env python3
"""Aggregate data/answer_grades.json into the headline response-quality stats.

Read-only reporter - run after any grading pass (see pipeline/GRADING.md).
"""
from common import DATA, load_json, record_key

g = load_json(DATA / 'answer_grades.json', {})
grades = g.get('grades', {})
dataset = load_json(DATA / 'dataset.json')
by_key = {record_key(r): r for r in dataset['records']}

n = len(grades)
da = {k: v for k, v in grades.items() if v.get('da')}
dg_n = [k for k, v in da.items() if v.get('dg') == 'n']
dg_p = [k for k, v in da.items() if v.get('dg') == 'p']
dg_y = [k for k, v in da.items() if v.get('dg') == 'y']
sd = [k for k, v in grades.items() if v.get('sd')]

print(f"graded: {n} of {len(by_key)} records "
      f"({n / len(by_key) * 100:.0f}% coverage)")
print(f"asked for data: {len(da)} ({len(da) / n * 100:.0f}% of graded)" if n else "no grades")
if da:
    print(f"  data given fully:  {len(dg_y):3d}  ({len(dg_y) / len(da) * 100:.0f}%)")
    print(f"  data partial:      {len(dg_p):3d}  ({len(dg_p) / len(da) * 100:.0f}%)")
    print(f"  data NOT given:    {len(dg_n):3d}  ({len(dg_n) / len(da) * 100:.0f}%)")
print(f"state-subject deflection: {len(sd)} of {n}" if n else "")

def show(keys, label):
    if not keys:
        return
    print(f"\n-- {label} --")
    for k in keys:
        r = by_key.get(k)
        note = grades[k].get('note', '')
        print(f"  [{k}] {r['j'] if r else '?'}" + (f"\n      {note}" if note else ''))

show(dg_n, 'data requested, none given')
show(sd, 'deflected to state governments')
