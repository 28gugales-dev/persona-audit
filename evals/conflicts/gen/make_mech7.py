"""Round-6 arms (PLAN v9), written as requests_mech7.jsonl plus one haiku_in file per request.
(1) Three strict conflict prompts written by GPT (Codex) from a product brief that never mentions changes of mind
    (paper/data/strict_prompts_gpt.json): 36 planted items unmarked and marked, and the 40 held-out decoys.
(2) genX (generic A + production exclusion list) on the fresh set, both hand-written sets and the marked reversals.
Run: python3 evals/conflicts/gen/make_mech7.py <repo root>"""
import json, sys
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
load = lambda f: [json.loads(l) for l in open(f'{R}/{f}')]
strict = json.load(open(f'{ROOT}/paper/data/strict_prompts_gpt.json'))
key = {i['item']: i for i in json.load(open(f'{ROOT}/paper/data/answer_key.json'))}
oracle = {r['item']: r for r in load('requests.jsonl') if r['kind'] == 'oracle'}
marked = {r['item']: r for r in load('requests_rerun.jsonl') if r['kind'] == 'markerpos' and r['prompt_version'] == 'prod'}
decoys = [i for i, v in key.items() if v['set'] == 'test' and v['label'].startswith('D') and int(v['history'][1:]) >= 12]
m5 = load('requests_mech5.jsonl')
genx = next(r['system'] for r in m5 if r['prompt_version'] == 'genX')
out = []
def add(r, pv, sys_, kind=None):
    rid = f"{pv}:{kind or r['kind']}:{r['item'] if 'item' in r else r['case']}"
    out.append({**r, 'id': rid, 'prompt_version': pv, 'system': sys_, **({'kind': kind} if kind else {})})
for n, s in enumerate(strict, 1):
    pv = f'gs{n}'
    for i in marked: add(oracle[i], pv, s, 'plainpos'); add(marked[i], pv, s, 'markerpos')
    for i in decoys: add(oracle[i], pv, s, 'decoy')
for r in m5:
    if r['prompt_version'] == 'defNoEmpty' and r['kind'] in ('fresh', 'hw1', 'adv2'): add(r, 'genX', genx)
for r in load('requests_mech.jsonl'):
    if r['kind'] == 'rev' and r['arm'] == 'marker' and r['prompt_version'] == 'noDNC': add(r, 'genX', genx)
assert len({r['id'] for r in out}) == len(out)
with open(f'{R}/requests_mech7.jsonl', 'w') as fh:
    for r in out:
        fh.write(json.dumps(r) + '\n')
        safe = r['id'].replace(':', '__').replace('/', '_')
        open(f'{R}/haiku_in/{safe}.txt', 'w').write(f"=== SYSTEM PROMPT ===\n{r['system']}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
from collections import Counter
print(len(out), Counter((r['prompt_version'], r['kind']) for r in out))
