"""v32 item 2: case credit counting only each run's first k returned pairs (k = 1, 2, all), from the files score_v18b.py scores.
Run: python3 evals/conflicts/gen/analyze_v32.py <repo root>  (writes paper/results/v32_budget.json)"""
import json, sys, os, contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import analyze_v25 as A  # runs v25 on import (deterministic rewrite of v25_analyses.json)
V = A.V
ARMS = ('production', 'naive', 'naiveChange', 'realX', 'depNoCap')
res = {}
for arm, f in V.ARMS:
    if arm not in ARMS or not os.path.exists(f'{V.R}/{f}'): continue
    for l in open(f'{V.R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        c = r['case']; rows = []
        for run in range(1, 7):
            p = f"{V.R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
            if not os.path.exists(p): continue
            t = open(p).read()
            try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: g = {}
            ps = A.ordered_pairs(r, g)
            rows.append([A.hit(c, ps[:k], False) for k in (1, 2, 99)])
        res.setdefault(arm, {})[c] = {'set': V.setof[c], 'runs': rows}
maj = lambda xs: sum(xs) * 2 > len(xs)
out = {arm: {k: sum(maj([r[i] for r in x['runs']]) for x in cs.values()) for i, k in enumerate(('k1', 'k2', 'all'))} | {'unseen_k1': sum(maj([r[0] for r in x['runs']]) for x in cs.values() if x['set'] in ('fresh2', 'fresh3')), 'n': len(cs)} for arm, cs in res.items()}
json.dump(out, open(f'{V.R}/v32_budget.json', 'w'), indent=1)
for k, v in out.items(): print(k, v)
