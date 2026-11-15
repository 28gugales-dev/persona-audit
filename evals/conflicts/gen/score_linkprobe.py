"""PLAN v22 part 2: score the retraction-link probe. A run is credited when its top 3 includes the keyed early passage, or an early-work
paragraph that both thesis labellers called a match with the announcement (any label round). Unlabelled (early paragraph, announced)
candidates are listed for labelling. Writes results/v22_link_scores.json. Run: python3 evals/conflicts/gen/score_linkprobe.py <repo root>"""
import json, sys, os, re
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.argv = [sys.argv[0], ROOT]
import contextlib, io
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_v18b as V
out, unl = {}, set()
for r in map(json.loads, open(f'{R}/requests_v22_link.jsonl')):
    c = r['case']; ids = [e['id'] for e in r['body']['excerpts']]; runs = []
    for run in (1, 2, 3):
        p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
        if not os.path.exists(p): continue
        t = open(p).read()
        try: g = json.loads(t[t.find('{'):t.rfind('}') + 1]).get('candidates', [])
        except Exception: g = []
        top = [ids[int(x[1:]) - 1] for x in g[:3] if isinstance(x, str) and re.fullmatch(r'E\d+', x) and 0 < int(x[1:]) <= len(ids)]
        hit, top1 = False, False
        for i, x in enumerate(top):
            ok = x == f'{c}_early' or (c, x, f'{c}_announced') in V.yes
            if V.side(c, x) == 'E' and not ok and (c, x, f'{c}_announced') not in V.labelled: unl.add(f'link|{c}|{x}|{c}_announced')
            hit |= ok; top1 |= ok and i == 0
        runs.append({'top3': hit, 'top1': top1, 'early_keyed_rank': top.index(f'{c}_early') + 1 if f'{c}_early' in top else None})
    out[c] = runs
maj = lambda k: sorted(c for c, rs in out.items() if sum(x[k] for x in rs) * 2 > len(rs))
summary = {'n': len(out), 'top3_majority': maj('top3'), 'top1_majority': maj('top1'), 'unlabelled': sorted(unl)}
json.dump({'summary': summary, 'cases': out}, open(f'{R}/v22_link_scores.json', 'w'), indent=1)
print(len(summary['top3_majority']), 'of', len(out), 'top-3:', summary['top3_majority']); print(len(summary['top1_majority']), 'top-1'); print('unlabelled', len(unl))
