"""Whole-history requests (one call per real history, oldest first, 400-character excerpts, theme "everything"), as in v14-v17.
Checked to rebuild requests_v14.jsonl exactly from realtext_histories{,2}.json before use on new histories.
Run: python3 evals/conflicts/gen/make_whole.py <repo root> <history suffix> <prompt name: production|realX_v1|changes_v1> <id prefix> <out file> [cap total]
(cap total, v18b: each excerpt min(cap, total // n) characters instead of 400)"""
import json, sys, re, datetime
ROOT, SUF, PROMPT, PREFIX, OUT = sys.argv[1:6]
CAP, TOTAL = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (400, None)

def system(name):
    if name in ('realX_v1', 'changes_v1', 'realX_deployed'): return json.load(open(f'{ROOT}/evals/conflicts/gen/real_prompts.json'))[name]
    return json.loads(open(f'{ROOT}/paper/results/requests_v17.jsonl').readline())['system']  # the shipped prompt as sent in v17

defuse = lambda t: re.sub(r'<(/?)(excerpt|theme)', lambda m: '‹' + m.group(1) + m.group(2), t, flags=re.I)

def build(h, sysp, prefix, case_set, cap=400, total=None):
    posts = sorted(h['posts'], key=lambda p: (p['createdUtc'], p['id']))
    n = min(cap, total // len(posts)) if total else cap
    ex = [{'id': p['id'], 'when': datetime.datetime.fromtimestamp(p['createdUtc'], datetime.UTC).strftime('%Y-%m'), 'text': p['body'][:n]} for p in posts]
    prompt = '\n'.join(['<theme>everything</theme>'] + [f'<excerpt id="E{i + 1}" written="{e["when"]}">\n{defuse(e["text"])}\n</excerpt>' for i, e in enumerate(ex)])
    return {'id': f"{prefix}:realN:{h['case']}", 'kind': 'realN', 'case': h['case'], 'set': case_set, 'system': sysp, 'prompt': prompt, 'body': {'theme': 'everything', 'excerpts': ex}}

if __name__ == '__main__':
    old = {json.loads(l)['case']: json.loads(l) for l in open(f'{ROOT}/paper/results/requests_v14.jsonl') if json.loads(l)['kind'] == 'realN'}
    for suf in ('', '2'):
        for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{suf}.json')):
            r = build(h, '', 'naive', '')
            assert r['prompt'] == old[h['case']]['prompt'] and r['body']['excerpts'] == old[h['case']]['body']['excerpts'], h['case']
    sysp = system(PROMPT); n = 0
    with open(f'{ROOT}/paper/results/{OUT}', 'w') as f:
        for suf in SUF.split(','):
          for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{suf}.json')):
            r = build(h, sysp, PREFIX, f'fresh{suf}' if suf == '3' else 'dev' if suf == '' else f'set{suf}', CAP, TOTAL); r['prompt_version'] = PROMPT; f.write(json.dumps(r) + '\n'); n += 1
            open(f"{ROOT}/paper/results/haiku_in/{r['id'].replace(':', '__')}.txt", 'w').write(f"=== SYSTEM PROMPT ===\n{sysp}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
    print('rebuilt v14 exactly;', n, 'requests ->', OUT)
