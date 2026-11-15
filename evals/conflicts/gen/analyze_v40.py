"""PLAN v40: the decision rule. Case-level finds (majority of runs, v18b credit) for longCur and longBig on the 30 long histories,
against the same 30 cases at short length with the same prompt (depNoCap, rounds 30 and 37); key-only finds too; control pairs per
run; non-genuine cards per history from cost40_scores.json. Writes paper/results/v40_scores.json.
Run: python3 evals/conflicts/gen/analyze_v40.py <repo root> (after score_v18b.py and score_cost_so.py cost40)"""
import json, sys, os
R = f'{sys.argv[1]}/paper/results'
d = json.load(open(f'{R}/v18b_scores.json'))['cases']
cases = [json.loads(l)['case'] for l in open(f'{R}/requests_v40_longcur.jsonl')]
maj = lambda h: sum(h) * 2 > len(h)
cost = json.load(open(f'{R}/cost40_scores.json')) if os.path.exists(f'{R}/cost40_scores.json') else {}
out = {}
for arm, name in (('depNoCap', 'short'), ('longCur', 'longCur'), ('longBig', 'longBig')):
    v = {c: d[arm][c] for c in cases}
    runs = min(len(x['hits']) for x in v.values())
    out[name] = {'runs': runs, 'found': sum(maj(x['hits']) for x in v.values()), 'any': sum(any(x['hits']) for x in v.values()),
                 'controls_per_run': round(sum(sum(x['controls']) for x in v.values()) / runs, 2),
                 'pairs_per_history_run': round(sum(sum(x['pairs']) for x in v.values()) / runs / len(v), 1),
                 'missed': sorted(c for c, x in v.items() if not maj(x['hits'])),
                 'not_per_history': cost.get(name, {}).get('not_per_history')}
base = out['short']['found']
for a in ('longCur', 'longBig'):
    o = out[a]; o['passes'] = o['found'] >= base - 3 and (o['not_per_history'] is not None and o['not_per_history'] <= 0.5) and o['controls_per_run'] <= 1
ok = [a for a in ('longCur', 'longBig') if out[a]['passes']]
out['decision'] = (max(ok, key=lambda a: (out[a]['found'], a == 'longCur')) if ok else 'keep 124')
json.dump(out, open(f'{R}/v40_scores.json', 'w'), indent=1)
for k, v in out.items(): print(k, v)
