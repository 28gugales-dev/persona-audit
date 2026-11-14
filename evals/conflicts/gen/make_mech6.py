"""Round-5 controls (PLAN v8): the placebo definition arms, written as requests_mech6.jsonl plus one haiku_in file per request.
Run: python3 evals/conflicts/gen/make_mech6.py <repo root>"""
import json, sys
R = f'{sys.argv[1]}/paper/results'
DEF = 'Count a pair only when the person asserts both as their own view, on the same point, and they clash.'
PLACEBO = 'Count a pair only when the person asserts both excerpts as their own view, about the very same point, and the two of them clash.'
EMPTY = 'Most themes have none, and an empty list is the right answer then. '
src = [json.loads(l) for l in open(f'{R}/requests_rerun.jsonl')]
src = [r for r in src if r['kind'] == 'markerpos' and r['prompt_version'] == 'prod']
assert len(src) == 36 and all(DEF in r['system'] and EMPTY in r['system'] for r in src)
out = []
for pv, f in (('placebo', lambda s: s.replace(DEF, PLACEBO)), ('placeboNoEmpty', lambda s: s.replace(DEF, PLACEBO).replace(EMPTY, ''))):
    for r in src:
        out.append({**r, 'id': r['id'].replace('prod:', f'{pv}:', 1), 'prompt_version': pv, 'system': f(r['system'])})
with open(f'{R}/requests_mech6.jsonl', 'w') as fh:
    for r in out:
        fh.write(json.dumps(r) + '\n')
        safe = r['id'].replace(':', '__').replace('/', '_')
        open(f'{R}/haiku_in/{safe}.txt', 'w').write(f"=== SYSTEM PROMPT ===\n{r['system']}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
print(len(out), 'requests')
