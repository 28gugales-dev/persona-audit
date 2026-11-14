"""Score the round-5 controls (PLAN v8): the definition x empty-list 2x2 plus placebo at three runs per cell, the Sonnet
second-model check, and the extra-card audit. Writes paper/results/mech6_scores.json.
Run: python3 evals/conflicts/gen/score_mech6.py <repo root>"""
import json, os, sys, random, contextlib, io
from collections import defaultdict
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'
safe = lambda i: i.replace(':', '__').replace('/', '_')
load = lambda f: [json.loads(l) for l in open(f'{R}/{f}')]

def raw_run(sid, run):
    f = f'{R}/haiku_raw/{sid}.r{run}.txt'
    if not os.path.exists(f): return None
    t = open(f).read()
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

marked = {}  # prompt_version -> item -> request
for f in ('requests_rerun.jsonl', 'requests_mech.jsonl', 'requests_mech2.jsonl', 'requests_mech6.jsonl'):
    for r in load(f):
        if r['kind'] == 'markerpos': marked.setdefault(r['prompt_version'], {})[r['item']] = r
RUNS = {'prod': (1, 4, 5), 'noEmpty': (1, 2, 3), 'defOnly': (1, 2, 3), 'defNoEmpty': (1, 2, 3), 'placebo': (1, 2, 3), 'placeboNoEmpty': (1, 2, 3)}
out = {'missing': []}
hits = {}  # arm -> item -> [hit per run]
for pv, runs in RUNS.items():
    hits[pv] = {}
    for i, r in marked[pv].items():
        hs = []
        for run in runs:
            g = raw_run(safe(r['id']), run)
            if g is None: out['missing'].append(f'{pv}:{i}.r{run}'); continue
            hs.append(S.item_hit(S.key[i], S.pairs(r, g)))
        hits[pv][i] = hs
items = sorted(set.intersection(*(set(v) for v in hits.values())))
mean = {pv: {i: sum(v[i]) / len(v[i]) for i in items if v[i]} for pv, v in hits.items()}
out['cells'] = {pv: {'runs': [sum(hits[pv][i][k] for i in items if len(hits[pv][i]) > k) for k in range(3)],
                     'mean_of_36': sum(mean[pv].values()), 'items_same_all_runs': sum(len(set(hits[pv][i])) == 1 for i in items)} for pv in RUNS}
# history-cluster bootstrap of differences in item-mean recall (all runs used, items nested in histories)
byh = defaultdict(list)
for i in items: byh[S.key[i]['history']].append(i)
hs = sorted(byh); rnd = random.Random(20261115)
CONTRASTS = {'definition | default kept': ('defOnly', 'prod'), 'definition | default removed': ('defNoEmpty', 'noEmpty'),
             'default removed | old definition': ('noEmpty', 'prod'), 'default removed | new definition': ('defNoEmpty', 'defOnly'),
             'placebo vs production': ('placebo', 'prod'), 'placebo no default vs no default': ('placeboNoEmpty', 'noEmpty'),
             'rewrite vs placebo no default': ('defNoEmpty', 'placeboNoEmpty'), 'definition only vs placebo': ('defOnly', 'placebo')}
boots = {k: [] for k in CONTRASTS}
for _ in range(10000):
    s = [i for h in (rnd.choice(hs) for _ in hs) for i in byh[h]]
    for k, (a, b) in CONTRASTS.items(): boots[k].append(sum(mean[a][i] - mean[b][i] for i in s) * 36 / len(s))
out['contrasts_items_of_36'] = {}
for k, (a, b) in CONTRASTS.items():
    d = sorted(boots[k]); out['contrasts_items_of_36'][k] = {'diff': sum(mean[a][i] - mean[b][i] for i in items), 'ci95': [d[249], d[9749]]}
# Sonnet, one run ('s1')
son = {}
oracle = S.oracle
neu = {r['item']: r for r in load('requests_mech.jsonl') if r['kind'] == 'neutralpos'}
dec = [i for i, v in S.key.items() if v['set'] == 'test' and v['label'].startswith('D') and int(v['history'][1:]) >= 12]
or2 = {r['item']: r for r in load('requests_mech2.jsonl') if r['kind'] == 'oracle' and r['prompt_version'] == 'defNoEmpty'}
arms = {'unmarked': {i: oracle[i] for i in items}, 'neutral': {i: neu[i] for i in items}, 'marked': {i: marked['prod'][i] for i in items},
        'rewrite_marked': {i: marked['defNoEmpty'][i] for i in items}, 'decoys_prod': {i: oracle[i] for i in dec}, 'decoys_rewrite': {i: or2[i] for i in dec}}
for a, m in arms.items():
    son[a] = {}
    for i, r in m.items():
        g = raw_run(safe(r['id']), 's1')
        if g is None: out['missing'].append(f'sonnet:{a}:{i}'); continue
        son[a][i] = S.item_hit(S.key[i], S.pairs(r, g))
out['sonnet'] = {a: {'k': sum(v.values()), 'n': len(v), 'wilson': S.wilson(sum(v.values()), len(v))} for a, v in son.items()}
for a in ('neutral', 'marked'):
    g = [i for i in son[a] if i in son['unmarked']]
    lost = sum(son['unmarked'][i] and not son[a][i] for i in g); gained = sum(son[a][i] and not son['unmarked'][i] for i in g)
    out['sonnet'][f'unmarked_vs_{a}'] = {'n': len(g), 'lost': lost, 'gained': gained, 'p': S.mcnemar(lost, gained)}
# extra-card audit (blind labels on non-planted end-to-end pairs)
mp = json.load(open(f'{R}/extra_cards_map.json')); lab = {str(x['row']): x['label'] for x in json.load(open(f'{R}/extra_cards_labels.json'))}
out['extra_cards'] = {'non_planted_pairs': {pv: sum(pv in v['arms'] for v in mp.values()) for pv in ('prod', 'defNoEmpty')},
                      'labels': {pv: {l: sum(pv in v['arms'] and lab[n] == l for n, v in mp.items()) for l in ('clash', 'not', 'unsure')} for pv in ('prod', 'defNoEmpty')},
                      'histories': sorted({v['history'] for v in mp.values()})}
json.dump(out, open(f'{R}/mech6_scores.json', 'w'), indent=1)
print('missing', len(out['missing']), out['missing'][:5])
for pv, v in out['cells'].items(): print(pv, v)
for k, v in out['contrasts_items_of_36'].items(): print(k, round(v['diff'], 2), [round(x, 2) for x in v['ci95']])
print('sonnet', {a: (v.get('k'), v.get('n')) if 'k' in v else v for a, v in out['sonnet'].items()})
print('extra', out['extra_cards'])
