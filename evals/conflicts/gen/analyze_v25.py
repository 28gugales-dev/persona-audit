"""v25 item 3: (a) credit without the keyed announced passage, (b) first 2 returned pairs per run only, from the files score_v18b.py scores.
Run: python3 evals/conflicts/gen/analyze_v25.py <repo root>  (writes paper/results/v25_analyses.json)"""
import json, sys, os, contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import score_v18b as V
R, S, side, yes = V.R, V.S, V.side, V.yes

def ordered_pairs(req, g):
    ids = [e['id'] for e in req['body']['excerpts']]; out = []
    for x in (g or {}).get('conflicts', []):
        try:
            p = frozenset((ids[int(x['a'][1:]) - 1], ids[int(x['b'][1:]) - 1]))
            if p not in out: out.append(p)
        except Exception: pass
    return out

def hit(c, ps, no_announced):
    for q in ps:
        a, b = sorted(q, key=lambda x: side(c, x) or 'Z')
        if side(c, a) != 'E' or side(c, b) != 'L': continue
        if no_announced and b == f'{c}_announced': continue
        if (a == f'{c}_early' and b in (f'{c}_announced', f'{c}_unannounced')) or (c, a, b) in yes: return True
    return False

res = {}
for arm, f in V.ARMS:
    if not os.path.exists(f'{R}/{f}'): continue
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        c = r['case']; rows = []
        for run in range(1, 7):
            p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
            if not os.path.exists(p): continue
            t = open(p).read()
            try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: g = {}
            ps = ordered_pairs(r, g)
            assert set(ps) == S.pairs(r, g)
            rows.append((hit(c, ps, False), hit(c, ps, True), hit(c, ps[:2], False)))
        res.setdefault(arm, {})[c] = {'set': V.setof[c], 'runs': rows}
maj = lambda xs: sum(xs) * 2 > len(xs)
summary = {}
for arm, cs in res.items():
    for s in ('dev', 'fresh1', 'fresh2', 'fresh3'):
        v = {c: x for c, x in cs.items() if x['set'] == s}
        if not v: continue
        summary[f'{arm}/{s}'] = {k: sum(maj([r[i] for r in x['runs']]) for x in v.values()) for i, k in enumerate(('all', 'no_announced', 'first2'))} | {'n': len(v)}
json.dump(summary, open(f'{R}/v25_analyses.json', 'w'), indent=1)
for arm in ('production', 'naive', 'realX', 'ships', 'realX_long', 'beliefshift_style', 'prodPara', 'defNoEmptyPara', 'genX'):
    rows = {k.split('/')[1]: v for k, v in summary.items() if k.split('/')[0] == arm}
    if rows: print(arm, rows, 'totals', {k: sum(r[k] for r in rows.values()) for k in ('n', 'all', 'no_announced', 'first2')})
