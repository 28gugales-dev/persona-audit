"""Per-case table of real-text results (paper Table 4b): announced pairs, hits over runs for each arm.
Run: python3 evals/conflicts/gen/table_cases.py <repo root>  -> prints a markdown table and writes paper/results/table_cases.json"""
import json, sys, contextlib, io
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'; D = f'{sys.argv[1]}/paper/data'

def raw(rid, run):
    try: t = open(f"{R}/haiku_raw/{rid.replace(':', '__').replace('/', '_')}.r{run}.txt").read()
    except FileNotFoundError: return None
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

def testA(file, pv, case):
    for l in open(f'{R}/{file}'):
        r = json.loads(l)
        if r['kind'] == 'realA' and r['prompt_version'] == pv and r['case'] == case and r['pair'] == 'ann':
            a, b = (e['id'] for e in r['body']['excerpts']); h = [frozenset((a, b)) in S.pairs(r, g) for g in (raw(r['id'], k) for k in (1, 2, 3)) if g is not None]
            return f'{sum(h)}/{len(h)}'
    return '–'
cases = [(c, 'dev') for c in json.load(open(f'{D}/realtext_cases.json'))] + [(c, 'held') for c in json.load(open(f'{D}/realtext_cases2.json'))]
v16 = json.load(open(f'{R}/v16_scores.json'))['pairs']; grp = json.load(open(f'{R}/group_scores_v2_real2.json'))['surfaced']
rows = []
for c, st in cases:
    k = f"{c['id']}/announced"; real = 'requests_real.jsonl' if st == 'dev' else 'requests_real2.jsonl'
    row = {'case': c['id'], 'set': st, 'states_new_view': c.get('announced_states_new_view'),
           'prod_alone': testA(real, 'prod', c['id']), 'realX_alone': testA('requests_realx_dev.jsonl', 'realX1', c['id']) if st == 'dev' else testA(real, 'realX', c['id']),
           'whole_naive': f"{sum(v16[k]['naive'])}/{len(v16[k]['naive'])}" if k in v16 else 'no history',
           'whole_realX': f"{sum(v16[k]['realX'])}/{len(v16[k]['realX'])}" if k in v16 else 'no history',
           'grouping_realX': ('1/1' if grp[k]['realX'] else '0/1') if k in grp else '–'}
    rows.append(row)
json.dump(rows, open(f'{R}/table_cases.json', 'w'), indent=1)
for r in rows: print('|', ' | '.join(str(r[x]) for x in r), '|')
