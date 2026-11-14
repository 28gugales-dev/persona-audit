"""PLAN v18 scoring: case-level whole-history results per arm and for merged two-call arms. An early-anchored pair counts when its partner
is a key passage (announced/unannounced) or a later-work paragraph both thesis labellers called "yes" (label__thesis*, label__thesis2*).
Also: key pairs (19-pair score), controls, pairs returned, and the early-anchored pairs still unlabelled.
Run: python3 evals/conflicts/gen/score_v18.py <repo root> [suffix]   (suffix 3: fresh held-out requests_v18_3 / realX3 / prod3)"""
import json, sys, re, os, contextlib, io
ROOT = sys.argv[1]; SUF = sys.argv[2] if len(sys.argv) > 2 else ''; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
yes = set()
for base in ('label__thesis', 'label__thesis2', 'label__thesis3'):
    if not os.path.exists(f'{R}/thesis_cards_map{base[len("label__thesis"):]}.json'): continue
    cmap = json.load(open(f'{R}/thesis_cards_map{base[len("label__thesis"):]}.json')); L = []
    for f in (base, base + '_s'):
        t = open(f'{R}/haiku_raw/{f}.r1.txt').read(); L.append({x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']})
    yes |= {(c['case'], c['later']) for c in cmap if all(l.get(c['card']) == 'yes' for l in L)}
labelled = set()
for m in ('', '2', '3'):
    if os.path.exists(f'{R}/thesis_cards_map{m}.json'): labelled |= {(c['case'], c['later']) for c in json.load(open(f'{R}/thesis_cards_map{m}.json'))}
ARMS = {'': {'naive': 'requests_v14.jsonl', 'realX': 'requests_v15.jsonl', 'production': 'requests_v17.jsonl', 'changes': 'requests_v18.jsonl'},
        '3': {'realX': 'requests_v18_3_realX.jsonl', 'production': 'requests_v18_3_prod.jsonl'}}[SUF]
runs = {}  # arm -> case -> [set of pairs per run or None]
for arm, f in ARMS.items():
    if not os.path.exists(f'{R}/{f}'): continue
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        rr = []
        for run in range(1, 7 if SUF == '3' else 4):
            p = f"{R}/haiku_raw/{r['id'].replace(':', '__').replace('/', '_')}.r{run}.txt"
            if not os.path.exists(p): continue
            t = open(p).read()
            try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: g = {}
            rr.append(S.pairs(r, g))
        runs.setdefault(arm, {})[r['case']] = rr
merged = {}
if 'changes' in runs and 'realX' in runs:
    merged['realX+changes'] = {c: [a | b for a, b in zip(runs['realX'][c], runs['changes'][c])] for c in runs['changes']}
if 'realX' in runs and all(len(v) == 3 for v in runs['realX'].values()):  # dev: pairs of 3 runs, not independent
    merged['realX+realX'] = {c: [v[0] | v[1], v[1] | v[2], v[0] | v[2]] for c, v in runs['realX'].items()}
if 'realX' in runs and all(len(v) == 6 for v in runs['realX'].values()):  # fresh: 3 disjoint pairs of 6 runs
    merged['realX+realX'] = {c: [v[0] | v[1], v[2] | v[3], v[4] | v[5]] for c, v in runs['realX'].items()}
out = {'arms': {}, 'unlabelled': set()}
for arm, cases in {**runs, **merged}.items():
    row = {'cases': {}, 'key_pairs_majority': 0, 'pairs_total': 0, 'controls': [0] * 6}
    for c, rr in cases.items():
        e = f'{c}_early'; key, wide, kp = [], [], {}
        for i, ps in enumerate(rr):
            row['pairs_total'] += len(ps); row['controls'][i] += any(f'{c}_control' in p for p in ps)
            k = [x for x in ('announced', 'unannounced') if frozenset((e, f'{c}_{x}')) in ps]
            for x in k: kp.setdefault(x, []).append(True)
            key.append(bool(k)); hit = bool(k)
            for p in ps:
                if e in p:
                    (o,) = p - {e}
                    if re.fullmatch(f'{c}_l\\d+', o):
                        hit |= (c, o) in yes
                        if (c, o) not in labelled: out['unlabelled'].add((c, o))
            wide.append(hit)
        row['key_pairs_majority'] += sum(len(v) * 2 > len(rr) for v in kp.values())
        row['cases'][c] = {'key': key, 'wide': wide}
    v = row['cases'].values()
    row.update(n=len(row['cases']), key_majority=sum(sum(x['key']) * 2 > len(x['key']) for x in v), wide_majority=sum(sum(x['wide']) * 2 > len(x['wide']) for x in v),
               wide_any=sum(any(x['wide']) for x in v), runs=len(next(iter(v))['wide']) if row['cases'] else 0)
    out['arms'][arm] = row
out['unlabelled'] = sorted(f'{a}|{b}' for a, b in out['unlabelled'])
json.dump(out, open(f'{R}/v18{SUF}_scores.json', 'w'), indent=1)
for arm, r in out['arms'].items():
    print(f"{arm:14} n={r['n']} runs={r['runs']} wide_majority={r['wide_majority']} wide_any={r['wide_any']} key_majority={r['key_majority']} key_pairs_majority={r['key_pairs_majority']} controls/run={r['controls'][:r['runs']]} pairs/run={r['pairs_total'] / max(r['runs'], 1):.0f}")
    print('   missed (majority):', [c for c, x in r['cases'].items() if sum(x['wide']) * 2 <= len(x['wide'])])
print('unlabelled early-anchored pairs:', len(out['unlabelled']))
