"""v34: each real history plus one planted unsignalled test reversal (P1, P2, P4 in key order) as posts <case>_canary_a (25th percentile date)
and <case>_canary_b (75th); shipped prompt, 400 characters, whole history. Run: python3 evals/conflicts/gen/make_canary.py <repo root>"""
import json, sys
import make_whole as W
ROOT = W.ROOT = sys.argv[1]
key = [x for x in json.load(open(f'{ROOT}/paper/data/answer_key.json')) if x['set'] == 'test' and x['label'] in ('P1', 'P2', 'P4')]
body = {p['id']: p['body'] for h in json.load(open(f'{ROOT}/paper/data/histories.json')) for p in h['posts']}
sysp = W.system('production'); n = 0; used = {}
with open(f'{ROOT}/paper/results/requests_v34_canary.jsonl', 'w') as f:
    for suf in ('', '2', '3', '4', '5'):
        for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{suf}.json')):
            k = key[n]; c = h['case']; ts = sorted(p['createdUtc'] for p in h['posts'])
            h['posts'] += [{'id': f'{c}_canary_a', 'body': body[k['a']], 'createdUtc': ts[len(ts) // 4] + 1}, {'id': f'{c}_canary_b', 'body': body[k['b']], 'createdUtc': ts[3 * len(ts) // 4] + 1}]
            r = W.build(h, sysp, 'v34c', f'set{suf}'); r['prompt_version'] = 'production+canary'; r['canary_item'] = k['item']; f.write(json.dumps(r) + '\n'); n += 1
            open(f"{ROOT}/paper/results/haiku_in/{r['id'].replace(':', '__')}.txt", 'w').write(f"=== SYSTEM PROMPT ===\n{sysp}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
print(n, 'histories; canaries', sorted({x['label'] for x in key[:n]}))
