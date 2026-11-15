"""v39 analysis: labeller-free case credit. (a) key pair only: the keyed early passage with the announced or unannounced passage;
(b) either end: any early-by-later pair that includes the keyed early passage or the announced/unannounced passage. Majority of runs, 30 cases.
Run: python3 evals/conflicts/gen/analyze_v39.py <repo root>  (writes paper/results/v39_judgefree.json)"""
import json, sys, os, contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import analyze_v25 as A
V = A.V
ARMS = ('production', 'prodPara', 'naive', 'naiveChange', 'realX', 'depNoCap')
res = {}
for arm, f in V.ARMS:
    if arm not in ARMS or not os.path.exists(f'{V.R}/{f}'): continue
    for l in open(f'{V.R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN' or V.setof[r['case']] == 'fresh4': continue
        c = r['case']
        K = {f'{c}_announced', f'{c}_unannounced'}; rows = []
        for run in range(1, 7):
            p = f"{V.R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
            if not os.path.exists(p): continue
            t = open(p).read()
            try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: g = {}
            key = either = False
            for q in A.ordered_pairs(r, g):
                a, b = sorted(q, key=lambda x: V.side(c, x) or 'Z')
                if V.side(c, a) != 'E' or V.side(c, b) != 'L': continue
                if a == f'{c}_early' and b in K: key = True
                if a == f'{c}_early' or b in K: either = True
            rows.append((key, either))
        res.setdefault(arm, {})[c] = rows
maj = lambda xs: sum(xs) * 2 > len(xs)
out = {arm: {'n': len(cs), 'key_only': sum(maj([r[0] for r in rows]) for rows in cs.values()), 'either_end': sum(maj([r[1] for r in rows]) for rows in cs.values())} for arm, cs in res.items()}
json.dump(out, open(f'{V.R}/v39_judgefree.json', 'w'), indent=1)
for k, v in out.items(): print(k, v)
