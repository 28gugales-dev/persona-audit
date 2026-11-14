"""Extra-card audit (PLAN v8, item 4): every pair flagged end to end on held-out histories t12-t23 by production (run 1) and by
the rewrite (defNoEmpty, run 1) that is not a planted positive or planted decoy. Writes a blind, shuffled set for labelling and
a private map back to arms. Run: python3 evals/conflicts/gen/extra_cards.py <repo root>"""
import json, sys, random, contextlib, io
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'
safe = lambda i: i.replace(':', '__').replace('/', '_')
reqs = [r for r in S.reqs if r['kind'] == 'pipeline_heldout' and r['prompt_version'] == 'prod']
reqs += [json.loads(l) for l in open(f'{R}/requests_mech5.jsonl') if '"pipeline_heldout"' in l]
test = [it for it in S.key.values() if it['set'] == 'test']
found = {}  # pair -> {'arms': set, 'texts': {...}, 'history'}
for r in reqs:
    g = S.raw(safe(r['id']))
    if g is None: continue
    ex = {e['id']: e for e in r['body']['excerpts']}
    for p in S.pairs(r, g):
        if any(S.item_hit(it, {p}) for it in test if it['history'] == r['history']): continue  # planted positive or decoy
        a, b = sorted(p)
        e = found.setdefault((a, b), {'history': r['history'], 'arms': set(), 'ex': [ex[a], ex[b]]})
        e['arms'].add(r['prompt_version'])
rows = list(found.items()); random.Random(20261115).shuffle(rows)
blind = [{'row': n, 'a': {'written': v['ex'][0]['when'], 'text': v['ex'][0]['text']}, 'b': {'written': v['ex'][1]['when'], 'text': v['ex'][1]['text']}}
         for n, (_, v) in enumerate(rows)]
json.dump(blind, open(f'{R}/extra_cards_blind.json', 'w'), indent=1)
json.dump({n: {'pair': list(k), 'history': v['history'], 'arms': sorted(v['arms'])} for n, (k, v) in enumerate(rows)}, open(f'{R}/extra_cards_map.json', 'w'), indent=1)
from collections import Counter
print(len(rows), 'pairs', Counter(tuple(sorted(v['arms'])) for _, v in rows))
