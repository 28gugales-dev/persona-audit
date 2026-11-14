"""Score PLAN v16: whole history, naive vs realX, over 3 runs on the 19 real early+later pairs, with pair-level majority,
exact McNemar and Wilson intervals; plus the three-run Test A rate on the cases whose announced passage states the new view.
Writes paper/results/v16_scores.json. Run: python3 evals/conflicts/gen/score_v16.py <repo root>"""
import json, sys, contextlib, io
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'
held = {c['id'] for c in json.load(open(f'{sys.argv[1]}/paper/data/realtext_cases2.json'))}
newview = {c['id'] for f in ('realtext_cases.json', 'realtext_cases2.json') for c in json.load(open(f'{sys.argv[1]}/paper/data/{f}')) if c.get('announced_states_new_view')}

def raw(rid, run):
    try: t = open(f"{R}/haiku_raw/{rid.replace(':', '__').replace('/', '_')}.r{run}.txt").read()
    except FileNotFoundError: return None
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

out = {'missing': []}
hits = {}  # (arm, case/later) -> [hit per run]
per_run = {}  # (arm, run) -> {surfaced, controls, pairs}
for arm, f in (('naive', 'requests_v14.jsonl'), ('realX', 'requests_v15.jsonl')):
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        ids = {e['id'] for e in r['body']['excerpts']}
        for run in (1, 2, 3):
            g = raw(r['id'], run)
            if g is None: out['missing'].append(f"{r['id']}.r{run}"); continue
            ps = S.pairs(r, g); s = per_run.setdefault(f'{arm}/r{run}', {'surfaced': 0, 'held_surfaced': 0, 'controls': 0, 'pairs': 0})
            s['pairs'] += len(ps); s['controls'] += any(f"{r['case']}_control" in p for p in ps)
            for later in ('announced', 'unannounced'):
                e, x = f"{r['case']}_early", f"{r['case']}_{later}"
                if x not in ids: continue
                h = frozenset((e, x)) in ps; hits.setdefault((arm, f"{r['case']}/{later}"), []).append(h)
                s['surfaced'] += h; s['held_surfaced'] += h and r['case'] in held
out['per_run'] = per_run
pairs = sorted({k for _, k in hits})
maj = {arm: {k: sum(hits[(arm, k)]) * 2 > len(hits[(arm, k)]) for k in pairs} for arm in ('naive', 'realX')}
out['pairs'] = {k: {arm: hits[(arm, k)] for arm in ('naive', 'realX')} for k in pairs}
out['majority'] = {}
for arm in ('naive', 'realX'):
    for name, sel in (('all', pairs), ('held', [k for k in pairs if k.split('/')[0] in held]), ('dev', [k for k in pairs if k.split('/')[0] not in held])):
        k = sum(maj[arm][p] for p in sel); out['majority'][f'{arm}/{name}'] = {'k': k, 'n': len(sel), 'wilson': S.wilson(k, len(sel))}
gained = sum(maj['realX'][p] and not maj['naive'][p] for p in pairs); lost = sum(maj['naive'][p] and not maj['realX'][p] for p in pairs)
out['mcnemar_realX_vs_naive'] = {'gained': gained, 'lost': lost, 'p': S.mcnemar(gained, lost)}
# three-run Test A on cases whose announced passage states the new view (held-out)
nv = {}
for l in open(f'{R}/requests_real2.jsonl'):
    r = json.loads(l)
    if r['kind'] != 'realA' or r['pair'] != 'ann' or r['case'] not in newview: continue
    a, b = (e['id'] for e in r['body']['excerpts'])
    for run in (1, 2, 3):
        g = raw(r['id'], run)
        if g is None: continue
        v = nv.setdefault(r['prompt_version'], [0, 0]); v[0] += frozenset((a, b)) in S.pairs(r, g); v[1] += 1
out['held_newview_testA_3runs'] = nv
json.dump(out, open(f'{R}/v16_scores.json', 'w'), indent=1)
print('missing', len(out['missing']))
for k, v in per_run.items(): print(k, v)
for k, v in out['majority'].items(): print(k, v)
print(out['mcnemar_realX_vs_naive'], nv)
