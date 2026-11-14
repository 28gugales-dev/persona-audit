"""Collect Haiku (agent harness) replies written one file per request into paper/results/raw/haiku.jsonl.
File name: <safe id>.r<run>.txt in paper/results/haiku_raw/."""
import json, os, sys
ROOT = sys.argv[1]
d = f'{ROOT}/paper/results/haiku_raw'
ids = {r['id'].replace(':', '__').replace('/', '_'): r['id'] for r in map(json.loads, open(f'{ROOT}/paper/results/requests.jsonl'))}
rows = []
for f in sorted(os.listdir(d)):
    if not f.endswith('.txt'): continue
    stem, run = f[:-4].rsplit('.r', 1)
    if stem in ids:
        rows.append({'id': ids[stem], 'model': 'haiku-agent-harness', 'text': open(f'{d}/{f}').read(), 'run': int(run)})
with open(f'{ROOT}/paper/results/raw/haiku.jsonl', 'w') as out:
    for r in rows: out.write(json.dumps(r) + '\n')
print(len(rows), 'replies')
