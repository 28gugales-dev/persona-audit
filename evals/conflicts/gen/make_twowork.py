"""v36/v38: each real history without its keyed early, announced and unannounced posts (control kept); Persona now (depNoCap, longer) and naive (400).
Run: python3 evals/conflicts/gen/make_twowork.py <repo root> [v36|v38]"""
import json, sys
import make_whole as W
ROOT = W.ROOT = sys.argv[1]
ARMS = {'v36': (('depNoCap', 'v36n', 1000, 120000), ('naive', 'v36v', 400, None)), 'v38': (('depQuote', 'v38w', 1000, 120000),)}
for prompt, prefix, cap, tot in ARMS[sys.argv[2] if len(sys.argv) > 2 else 'v36']:
    sysp = W.system(prompt)
    with open(f'{ROOT}/paper/results/requests_v36_{prefix}.jsonl', 'w') as f:
        for suf in ('', '2', '3', '4', '5'):
            for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{suf}.json')):
                c = h['case']; h['posts'] = [p for p in h['posts'] if p['id'] not in (f'{c}_early', f'{c}_announced', f'{c}_unannounced')]
                r = W.build(h, sysp, prefix, f'set{suf}', cap, tot); r['kind'] = 'nochange'; r['prompt_version'] = prompt + '+twowork'; f.write(json.dumps(r) + '\n')
                open(f"{ROOT}/paper/results/haiku_in/{r['id'].replace(':', '__')}.txt", 'w').write(f"=== SYSTEM PROMPT ===\n{sysp}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
print('ok')
