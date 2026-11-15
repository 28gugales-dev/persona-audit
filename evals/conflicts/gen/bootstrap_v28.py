"""v28 item 3: bootstrap over histories (10,000 resamples) of realX (400) minus naive (400): genuine share (pooled) and non-genuine
cards per history, from the round-27 cost labels. Run: python3 evals/conflicts/gen/bootstrap_v28.py <repo root>"""
import json, sys, random, collections
R = f'{sys.argv[1]}/paper/results'; M = json.load(open(f'{R}/cost27_cards_map.json'))
L = [{}, {}]
for f in M['files']:
    for i, suf in enumerate(('', '_s')):
        t = open(f'{R}/haiku_raw/{f}{suf}.r1.txt').read(); L[i].update({x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']})
by = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))  # arm -> case -> [cards, genuine]
for c in M['cards']:
    v = by[c['arm']][c['case']]; v[0] += 1; v[1] += L[0].get(c['card']) == L[1].get(c['card']) == 'real'
cases = sorted(M['per_history'])
def stats(arm, cs):
    n = sum(by[arm][c][0] for c in cs); g = sum(by[arm][c][1] for c in cs)
    return (g / n if n else 0), (n - g) / len(cs)
rng = random.Random(28); d_share, d_not = [], []
for _ in range(10000):
    cs = [rng.choice(cases) for _ in cases]
    (sa, na), (sb, nb) = stats('realX400', cs), stats('naive400', cs)
    d_share.append(sa - sb); d_not.append(na - nb)
ci = lambda xs: (round(sorted(xs)[249], 3), round(sorted(xs)[9749], 3))
out = {'point': {'share': [round(x, 3) for x in (stats('realX400', cases)[0], stats('naive400', cases)[0])], 'not_per_history': [round(x, 2) for x in (stats('realX400', cases)[1], stats('naive400', cases)[1])]},
       'ci95_share_diff': ci(d_share), 'ci95_not_per_history_diff': ci(d_not)}
json.dump(out, open(f'{R}/v28_bootstrap.json', 'w'), indent=1); print(out)
