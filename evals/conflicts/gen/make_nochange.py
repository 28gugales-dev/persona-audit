"""v28: no-change histories. For each real case, the early work's sampled paragraphs only (keyed early and control passages removed),
in original order, redated evenly across six years from 2001-01. One request per arm per history.
Run: python3 evals/conflicts/gen/make_nochange.py <repo root>"""
import json, sys, re, copy, datetime, os
import make_whole as W
ROOT = W.ROOT = sys.argv[1]
ARMS = [('production', 'v28zp', 400, None), ('naive', 'v28zn', 400, None), ('realX_v1', 'v28zx', 400, None), ('realX_deployed', 'v28zs', 1000, 120000), ('naiveChange', 'v28zc', 400, None)]
hist = []
for suf in ('', '2', '3', '4', '5'):
    for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{suf}.json')):
        c = h['case']; ps = sorted((p for p in h['posts'] if re.fullmatch(f'{c}_e\\d+', p['id'])), key=lambda p: (p['createdUtc'], p['id']))
        ps = copy.deepcopy(ps); n = len(ps)
        for i, p in enumerate(ps):
            m = i * 72 // n; p['createdUtc'] = int(datetime.datetime(2001 + m // 12, m % 12 + 1, 15, tzinfo=datetime.UTC).timestamp())
        hist.append(({'case': c, 'posts': ps}, suf))
for prompt, prefix, cap, tot in ARMS:
    sysp = W.system(prompt)
    with open(f'{ROOT}/paper/results/requests_v28_nochange_{prefix}.jsonl', 'w') as f:
        for h, suf in hist:
            r = W.build(h, sysp, prefix, 'nochange', cap, tot); r['kind'] = 'nochange'; r['prompt_version'] = prompt + '+nochange'; f.write(json.dumps(r) + '\n')
            open(f"{ROOT}/paper/results/haiku_in/{r['id'].replace(':', '__')}.txt", 'w').write(f"=== SYSTEM PROMPT ===\n{sysp}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
print(len(hist), 'histories; posts per history', min(len(h['posts']) for h, _ in hist), '-', max(len(h['posts']) for h, _ in hist))
