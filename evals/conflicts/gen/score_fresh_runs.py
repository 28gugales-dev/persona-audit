"""Score the fresh-set repeats (PLAN v10): production, rewrite (defNoEmpty) and genX on the 40 fresh items, runs 1-3.
Writes paper/results/fresh_runs_scores.json. Run: python3 evals/conflicts/gen/score_fresh_runs.py <repo root>"""
import json, os, sys, random
R = f'{sys.argv[1]}/paper/results'
items = {x['id']: x['label'] for x in json.load(open(f'{sys.argv[1]}/paper/data/fresh_narrated.json'))}

def hit(pv, i, run):
    t = open(f'{R}/haiku_raw/{pv}__fresh__{i}.r{run}.txt').read()
    try: r = json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return False
    return any({x.get('a'), x.get('b')} == {'E1', 'E2'} for x in r.get('conflicts', []))

assert all(os.path.exists(f'{R}/haiku_raw/{pv}__fresh__{i}.r{run}.txt') for pv in ('prod', 'defNoEmpty', 'genX') for i in items for run in (1, 2, 3))
h = {pv: {i: [hit(pv, i, run) for run in (1, 2, 3)] for i in items} for pv in ('prod', 'defNoEmpty', 'genX')}
out = {}
for pv, v in h.items():
    out[pv] = {grp: {'runs': [sum(v[i][k] for i in items if (items[i] == 'NR') == (grp == 'NR')) for k in range(3)],
                     'items_same_all_runs': sum(len(set(v[i])) == 1 for i in items if (items[i] == 'NR') == (grp == 'NR'))} for grp in ('NR', 'lookalike')}
nr = [i for i in items if items[i] == 'NR']; rnd = random.Random(20261115)
m = lambda pv, i: sum(h[pv][i]) / 3
for pv in ('defNoEmpty', 'genX'):
    d = sorted(sum(m(pv, i) - m('prod', i) for i in s) for s in ([rnd.choice(nr) for _ in nr] for _ in range(10000)))
    out[f'{pv}_minus_prod_NR'] = {'diff_items_of_20': sum(m(pv, i) - m('prod', i) for i in nr), 'ci95': [d[249], d[9749]]}
json.dump(out, open(f'{R}/fresh_runs_scores.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
