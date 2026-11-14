"""Score the round-4 confirmation runs (requests_mech5.jsonl) and the variance reruns. Writes paper/results/confirm_scores.json.
fresh / hw1 / adv2: hit = (a, b) flagged. pipeline_heldout: per held-out test item, as score_rerun.py. genX: as score_mech.py.
Run: python3 evals/conflicts/gen/score_confirm.py <repo root>"""
import json, os, sys, contextlib, io
from collections import defaultdict
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'
reqs = [json.loads(l) for l in open(f'{R}/requests_mech5.jsonl')]
safe = lambda i: i.replace(':', '__').replace('/', '_')

def raw_run(sid, run):
    f = f'{R}/haiku_raw/{sid}.r{run}.txt'
    if not os.path.exists(f): return None
    t = open(f).read()
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

out = {'missing': 0}
cells = defaultdict(lambda: [0, 0])
adv1 = {it['id']: it for it in json.load(open(f'{sys.argv[1]}/paper/data/adversarial.json'))['items']}
flags = defaultdict(set); cov = set(); prod_nr = {}
for r in reqs:
    got = raw_run(safe(r['id']), 1)
    if got is None: out['missing'] += 1; continue
    ps = S.pairs(r, got); pv = r['prompt_version']
    if r['kind'] == 'fresh':
        hit = frozenset((f"{r['item']}_a", f"{r['item']}_b")) in ps
        grp = 'NR' if r['label'] == 'NR' else 'lookalike'
        for k in {f'fresh/{grp}/{pv}', f"fresh/{r['label']}/{pv}"}: cells[k][0] += hit; cells[k][1] += 1
        if pv == 'prod' and r['label'] == 'NR': prod_nr[r['item']] = hit
    elif r['kind'] in ('hw1', 'adv2'):
        it = r['item']; typ = adv1[it]['type'] if r['kind'] == 'hw1' else r['type']
        hit = frozenset((f'{it}_a', f'{it}_b')) in ps
        cells[f'hw/{typ}/{pv}'][0] += hit; cells[f'hw/{typ}/{pv}'][1] += 1
    elif r['kind'] == 'pipeline_heldout':
        flags[r['history']] |= ps; cov.add(r['history'])
    elif r['kind'] in ('genmarked', 'gendecoy'):
        hit = S.item_hit(S.key[r['item']], ps)
        cells[f"{r['kind']}/{pv}"][0] += hit; cells[f"{r['kind']}/{pv}"][1] += 1
# rewrite end to end on held-out histories, paired with production on the same items
prod_flags = defaultdict(set)
for r in S.reqs:
    if r['kind'] == 'pipeline_heldout' and r['prompt_version'] == 'prod':
        g = S.raw(safe(r['id']))
        if g is not None: prod_flags[r['history']] |= S.pairs(r, g)
pos = defaultdict(lambda: [0, 0]); pair = [0, 0]
for it in S.key.values():
    if it['set'] != 'test' or it['history'] not in cov: continue
    h = S.item_hit(it, flags[it['history']]); hp = S.item_hit(it, prod_flags[it['history']])
    k = 'POS' if it['conflict'] else 'DECOY'; pos[k][0] += h; pos[k][1] += 1
    if it['conflict']: pair[0] += h and not hp; pair[1] += hp and not h
out['pipeline_heldout_defNoEmpty'] = {'histories': len(cov), **{k: {'k': v[0], 'n': v[1]} for k, v in pos.items()},
                                      'vs_prod_gained': pair[0], 'vs_prod_lost': pair[1], 'p': S.mcnemar(*pair),
                                      'flags_per_history': sum(len(v) for v in flags.values()) / max(1, len(cov))}
# which fresh narrated reversals production missed, and whether they say "changed my mind" / "wrong" outright
fresh = {x['id']: x for x in json.load(open(f'{sys.argv[1]}/paper/data/fresh_narrated.json'))}
explicit = lambda i: any(w in fresh[i]['b'].lower() for w in ('changed my mind', 'i was wrong', 'i used to'))
out['fresh_prod_nr'] = {'explicit': {'found': sum(v for i, v in prod_nr.items() if explicit(i)), 'n': sum(explicit(i) for i in prod_nr)},
                        'other': {'found': sum(v for i, v in prod_nr.items() if not explicit(i)), 'n': sum(not explicit(i) for i in prod_nr)},
                        'missed': sorted(i for i, v in prod_nr.items() if not v)}
out['cells'] = {k: {'k': v[0], 'n': v[1], 'wilson': S.wilson(v[0], v[1])} for k, v in sorted(cells.items())}
# variance, same wrapper (the run-3 harness check uses another wrapper and is reported apart): marked planted items, production (runs 1, 4, 5) and rewrite without empty-list line (runs 1, 2, 3)
mk_prod = {r['item']: r for r in S.reqs if r['kind'] == 'markerpos' and r['prompt_version'] == 'prod'}
mech = {json.loads(l)['item']: json.loads(l) for l in open(f'{R}/requests_mech2.jsonl') if json.loads(l)['kind'] == 'markerpos' and json.loads(l)['prompt_version'] == 'defNoEmpty'}
var = {}
for name, reqmap, prefix, runs in (('prod', mk_prod, 'prod__mk__', (1, 4, 5)), ('defNoEmpty', mech, 'defNoEmpty__mk__', (1, 2, 3))):
    per = {run: {} for run in runs}
    for run in runs:
        for i, r in reqmap.items():
            g = raw_run(f'{prefix}{i}', run)
            if g is not None: per[run][i] = S.item_hit(S.key[i], S.pairs(r, g))
    totals = {run: sum(v.values()) for run, v in per.items()}
    items = set.intersection(*(set(v) for v in per.values()))
    stable = sum(len({per[run][i] for run in runs}) == 1 for i in items)
    var[name] = {'runs': {str(k): {'k': totals[k], 'n': len(per[k])} for k in runs}, 'items_same_all_runs': stable, 'items': len(items)}
out['variance_marked'] = var
json.dump(out, open(f'{R}/confirm_scores.json', 'w'), indent=1)
print('missing', out['missing'])
for k, v in out['cells'].items(): print(k, v['k'], '/', v['n'])
print('pipeline defNoEmpty', out['pipeline_heldout_defNoEmpty']); print('variance', var)
