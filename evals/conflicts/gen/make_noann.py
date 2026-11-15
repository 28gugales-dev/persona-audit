"""v31: each real history with its announced post deleted (unannounced and later-work paragraphs kept); depNoCap, longer excerpts, whole history.
Run: python3 evals/conflicts/gen/make_noann.py <repo root>"""
import json, sys
import make_whole as W
ROOT = W.ROOT = sys.argv[1]
sysp = W.system('depNoCap'); n = 0
with open(f'{ROOT}/paper/results/requests_v31_noann.jsonl', 'w') as f:
    for suf in ('', '2', '3', '4', '5'):
        for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{suf}.json')):
            k = len(h['posts']); h['posts'] = [p for p in h['posts'] if p['id'] != f"{h['case']}_announced"]; assert len(h['posts']) == k - 1, h['case']
            r = W.build(h, sysp, 'v31a', f'set{suf}', 1000, 120000); r['prompt_version'] = 'depNoCap+noann'; f.write(json.dumps(r) + '\n'); n += 1
            open(f"{ROOT}/paper/results/haiku_in/{r['id'].replace(':', '__')}.txt", 'w').write(f"=== SYSTEM PROMPT ===\n{sysp}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
print(n, 'histories')
