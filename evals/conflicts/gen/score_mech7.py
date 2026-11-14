"""Score the round-6 arms (PLAN v9, requests_mech7.jsonl): GPT-written strict prompts (unmarked vs marked planted items,
held-out decoys) and genX on the fresh, hand-written and marked-reversal sets. Writes paper/results/mech7_scores.json.
Run: python3 evals/conflicts/gen/score_mech7.py <repo root>"""
import json, sys, contextlib, io
from collections import defaultdict
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
safe = lambda i: i.replace(':', '__').replace('/', '_')
adv1 = {it['id']: it for it in json.load(open(f'{ROOT}/paper/data/adversarial.json'))['items']}
cells = defaultdict(lambda: [0, 0]); per = defaultdict(dict); missing = []
for r in map(json.loads, open(f'{R}/requests_mech7.jsonl')):
    g = S.raw(safe(r['id']))
    if g is None: missing.append(r['id']); continue
    ps = S.pairs(r, g); pv, k = r['prompt_version'], r['kind']
    if k in ('plainpos', 'markerpos', 'decoy'): hit = S.item_hit(S.key[r['item']], ps); c = f'{pv}/{k}'; per[c][r['item']] = hit
    elif k == 'fresh': hit = frozenset((f"{r['item']}_a", f"{r['item']}_b")) in ps; c = f"genX/fresh/{'NR' if r['label'] == 'NR' else 'lookalike'}"
    elif k in ('hw1', 'adv2'):
        it = r['item']; typ = adv1[it]['type'] if k == 'hw1' else r['type']
        hit = frozenset((f'{it}_a', f'{it}_b')) in ps; c = f'genX/hw/{typ}'
    elif k == 'rev':
        c0 = r['case']; hit = frozenset((f'{c0}_earlier', f'{c0}_later')) in ps; c = 'genX/rev_marked'
        cells['genX/rev_controls_flagged'][0] += any(f'{c0}_ctl' in p or frozenset((f'{c0}_hard', f'{c0}_later')) == p for p in ps); cells['genX/rev_controls_flagged'][1] += 1
    cells[c][0] += hit; cells[c][1] += 1
out = {'missing': missing, 'cells': {c: {'k': v[0], 'n': v[1], 'wilson': S.wilson(*v)} for c, v in sorted(cells.items())}}
out['strict_marker'] = {}
for pv in ('gs1', 'gs2', 'gs3'):
    u, m = per[f'{pv}/plainpos'], per[f'{pv}/markerpos']; g = [i for i in u if i in m]
    lost = sum(u[i] and not m[i] for i in g); gained = sum(m[i] and not u[i] for i in g)
    out['strict_marker'][pv] = {'n': len(g), 'unmarked': sum(u[i] for i in g), 'marked': sum(m[i] for i in g), 'lost': lost, 'gained': gained, 'p': S.mcnemar(lost, gained)}
json.dump(out, open(f'{R}/mech7_scores.json', 'w'), indent=1)
print('missing', len(missing))
for c, v in out['cells'].items(): print(c, v['k'], '/', v['n'])
print(out['strict_marker'])
