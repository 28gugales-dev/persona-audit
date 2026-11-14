"""PLAN v13 P1: the frozen real-prose prompt (realX_v1) on sets it never saw. Writes paper/results/realx_prec_scores.json.
Planted decoys are scored as in score_mech7.py (item_hit); fresh, hw1 and adv2 items by the item's own (a, b) pair.
Run: python3 evals/conflicts/gen/score_realx_prec.py <repo root>"""
import json, sys, contextlib, io
from collections import defaultdict
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'
adv = {it['id']: it for it in json.load(open(f'{sys.argv[1]}/paper/data/adversarial.json'))['items']}
cells, missing = defaultdict(lambda: [0, 0]), []
for l in open(f'{R}/requests_realx_prec.jsonl'):
    r = json.loads(l); g = S.raw(r['id'].replace(':', '__').replace('/', '_'))
    if g is None: missing.append(r['id']); continue
    ps = S.pairs(r, g)
    if r['kind'] == 'decoy': cell, hit = 'planted_decoys', S.item_hit(S.key[r['item']], ps)
    else:
        hit = frozenset((f"{r['item']}_a", f"{r['item']}_b")) in ps
        cell = {'fresh': 'fresh_narrated' if r.get('label') == 'NR' else 'fresh_lookalikes'}.get(r['kind'], 'handwritten_decoys')
    cells[cell][0] += hit; cells[cell][1] += 1
out = {'missing': missing, **{k: {'k': v[0], 'n': v[1], 'wilson': S.wilson(*v)} for k, v in sorted(cells.items())}}
json.dump(out, open(f'{R}/realx_prec_scores.json', 'w'), indent=1)
for k, v in out.items(): print(k, v if k == 'missing' else f"{v['k']}/{v['n']}")
