"""Naive whole-history prompt on merged (longer) histories: recall of planted positives, decoy flag rate, and flag count."""
import json, sys
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
key = [it for it in json.load(open(f'{ROOT}/paper/data/answer_key.json')) if it['set'] == 'test']
hist = {h['history']: h for h in json.load(open(f'{ROOT}/paper/data/histories.json'))}
nm = json.load(open(f'{R}/naive_map.json'))
out = {}
for name, members in [('single (26 posts)', None), ('Lt00_t01_t02', 3), ('Lt03_t04_t05', 3), ('Lt06_t07_t08', 3), ('Lt09_t10_t11', 3), ('L12', 12), ('L24', 24)]:
    runs = [f't{i:02d}' for i in range(12)] if members is None else [name]
    pos = neg = hp = hn = flags = 0
    for run in runs:
        t = open(f'{R}/haiku_raw/{run}__naive.r1.txt').read()
        try: pairs = json.loads(t[t.find('{'):t.rfind('}') + 1])['pairs']
        except Exception: pairs = []
        m = nm[run]
        fl = {frozenset((m[a], m[b])) for a, b in (p for p in pairs if len(p) == 2) if a in m and b in m}
        flags += len(fl)
        hs = [run] if members is None else [m[k].split('_')[0] for k in m]
        hs = set(hs)
        for it in key:
            if it['history'] not in hs: continue
            part = {p['id'] for p in hist[it['history']]['posts'] if p['item'] == it['item'] and p['role'] in ('a', 'filler')}
            hit = any(it['b'] in pr and (pr - {it['b']}) & part for pr in fl)
            if it['conflict']: pos += 1; hp += hit
            else: neg += 1; hn += hit
    out[name] = {'posts': sum(len(nm[r]) for r in runs) // len(runs), 'pos': pos, 'recall': hp / pos, 'decoys': neg, 'decoy_flag': hn / neg, 'flags_per_run': flags / len(runs)}
    print(name, out[name])
json.dump(out, open(f'{R}/naive_long.json', 'w'), indent=1)
