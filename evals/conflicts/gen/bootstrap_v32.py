"""v32: bootstrap over the 30 histories (10,000 resamples) of Persona now (depNoCap) minus naive (400): genuine share and non-genuine cards per history, single Sonnet+Opus batch.
Run: python3 evals/conflicts/gen/bootstrap_v32.py <repo root>  (writes paper/results/v32_bootstrap.json)"""
import json, sys, random
R = f'{sys.argv[1]}/paper/results'; M = json.load(open(f'{R}/cost32_cards_map.json')); L = [{}, {}]
for f in M['files']:
    for i, s in enumerate(('_s', '_o')):
        t = open(f'{R}/haiku_raw/{f}{s}.r1.txt').read(); L[i].update({x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']})
cases = sorted(M['per_history'])
def tally(arm):
    d = {c: [0, 0] for c in cases}
    for x in M['cards']:
        if x['arm'] == arm: d[x['case']][0] += 1; d[x['case']][1] += L[0][x['card']] == L[1][x['card']] == 'real'
    return d
A, B = tally('depNoCap'), tally('naive400')
def stat(cs):
    s = lambda d: (sum(d[c][1] for c in cs) / max(sum(d[c][0] for c in cs), 1), sum(d[c][0] - d[c][1] for c in cs) / len(cs))
    (sa, na), (sb, nb) = s(A), s(B); return sa - sb, na - nb
rng = random.Random('v32-boot'); bs = sorted(stat([rng.choice(cases) for _ in cases]) for _ in range(10000))
ci = lambda i: [round(sorted(b[i] for b in bs)[k], 2) for k in (250, 9749)]
out = {'point': [round(x, 2) for x in stat(cases)], 'share_ci': ci(0), 'nongenuine_ci': ci(1)}
json.dump(out, open(f'{R}/v32_bootstrap.json', 'w'), indent=1); print(out)
