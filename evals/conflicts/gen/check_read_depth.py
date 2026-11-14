"""Harness read-depth check for the whole-history calls (PLAN v14-v16): the highest excerpt number each reply cites,
against the request's excerpt count. Writes paper/results/read_depth.json. Run: python3 evals/conflicts/gen/check_read_depth.py <repo root>"""
import json, re, os, sys
R = f'{sys.argv[1]}/paper/results'; out = []
for f, arm in (('requests_v14.jsonl', 'naive'), ('requests_v15.jsonl', 'realXwh')):
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        n = len(r['body']['excerpts'])
        for run in (1, 2, 3):
            p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
            ids = [int(x) for x in re.findall(r'"E(\d+)"', open(p).read())] if os.path.exists(p) else []
            out.append({'arm': arm, 'case': r['case'], 'run': run, 'excerpts': n, 'max_cited': max(ids, default=0)})
cited = [o for o in out if o['max_cited']]
summ = {'runs': len(out), 'runs_citing_any': len(cited), 'last_tenth': sum(o['max_cited'] >= 0.9 * o['excerpts'] for o in cited),
        'last_third': sum(o['max_cited'] >= 2 / 3 * o['excerpts'] for o in cited)}
json.dump({'summary': summ, 'rows': out}, open(f'{R}/read_depth.json', 'w'), indent=1); print(summ)
