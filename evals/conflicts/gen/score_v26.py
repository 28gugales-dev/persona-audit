"""v26: hard-negative calibration and the Opus evidence judge; rescore case credit requiring Opus agreement on off-key pairs.
Run: python3 evals/conflicts/gen/score_v26.py <repo root>  (writes paper/results/v26_scores.json)"""
import json, sys, os, re, math, contextlib, io
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
with contextlib.redirect_stdout(io.StringIO()):
    import score_v18b as V
read = lambda f: (lambda t: json.loads(t[t.find('{'):t.rfind('}') + 1])['labels'])(open(f'{R}/haiku_raw/{f}.r1.txt').read())
from collections import Counter
m13 = json.load(open(f'{R}/thesis_cards_mapx13.json'))
h = {x['card']: x['label'] for x in read('label__thesisx13')}; s = {x['card']: x['label'] for x in read('label__thesisx13_s')}
cal = Counter(); n13 = Counter()
for x in m13: n13[x['kind']] += 1; cal[x['kind']] += h.get(x['card']) == 'yes' and s.get(x['card']) == 'yes'
mo = json.load(open(f'{R}/thesis_cards_mapopus26.json'))
cases = {c['id']: c for f in ('', '2', '3', '4', '5') if os.path.exists(f'{ROOT}/paper/data/realtext_cases{f}.json') for c in json.load(open(f'{ROOT}/paper/data/realtext_cases{f}.json'))}
text = {hh['case']: {p['id']: p['body'][:1000] for p in hh['posts']} for f in ('', '2', '3', '4', '5') if os.path.exists(f'{ROOT}/paper/data/realtext_histories{f}.json') for hh in json.load(open(f'{ROOT}/paper/data/realtext_histories{f}.json'))}
norm = lambda t: re.sub(r'\s+', ' ', re.sub(r'[“”"‘’\'`]', '', t)).strip().lower()
op = {}
for i in range(4):
    for x in read(f'label__opus26_{i}'): op[x['card']] = x
ok = Counter(); n = Counter(); unq = Counter(); opus_yes = set()
for x in mo:
    n[x['kind']] += 1; o = op.get(x['card'], {})
    if o.get('label') == 'yes':
        q = norm(o.get('quote', ''))
        verbatim = bool(q) and all(part in norm(text[x['case']][x['later']]) for part in re.split(r'\s*(?:\.\.\.|…)\s*', q) if part)
        if verbatim: ok[x['kind']] += 1; opus_yes.add((x['case'], x['early'], x['later']))
        else: unq[x['kind']] += 1
print('missing opus labels', sum(1 for x in mo if x['card'] not in op))
print('Haiku+Sonnet both-yes', dict(cal), 'of', dict(n13))
print('Opus yes with verbatim quote', dict(ok), 'yes without verbatim quote', dict(unq), 'of', dict(n))
# rescore: off-key credit needs Opus agreement too
maj = lambda xs: sum(xs) * 2 > len(xs)
def mc(b, c):
    t = b + c; return 1.0 if t == 0 else min(1, 2 * sum(math.comb(t, i) for i in range(min(b, c) + 1)) / 2 ** t)
res = {}
for arm, f in V.ARMS:
    if arm not in ('production', 'naive', 'realX', 'ships', 'realX_long', 'ships_masked', 'production_masked', 'prodPara'): continue
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        c = r['case']; a2, a3 = [], []
        for run in range(1, 7):
            p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
            if not os.path.exists(p): continue
            t = open(p).read()
            try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: g = {}
            two = three = False
            for q in V.S.pairs(r, g):
                a, b = sorted(q, key=lambda z: V.side(c, z) or 'Z')
                if V.side(c, a) != 'E' or V.side(c, b) != 'L': continue
                if a == f'{c}_early' and b in (f'{c}_announced', f'{c}_unannounced'): two = three = True
                elif (c, a, b) in V.yes:
                    two = True; three = three or (c, a, b) in opus_yes
            a2.append(two); a3.append(three)
        res.setdefault(arm, {})[c] = (V.setof[c], maj(a2), maj(a3))
out = {}
for arm, cs in res.items():
    by = Counter(); by3 = Counter()
    for c, (st, x2, x3) in cs.items(): by[st] += x2; by3[st] += x3
    out[arm] = {'two_labellers': dict(by), 'plus_opus': dict(by3), 'total': [sum(by.values()), sum(by3.values()), len(cs)]}
    print(arm, out[arm])
f3 = lambda arm: {c for c, v in res[arm].items() if v[2]}
rx, nv = f3('realX'), f3('naive'); print('realX vs naive (plus Opus):', len(rx - nv), len(nv - rx), 'p', mc(len(rx - nv), len(nv - rx)))
sh = {c for c, v in res['ships'].items() if v[2]}; pr = {c for c, v in res['production'].items() if v[2] and c in res['ships']}
print('ships vs shipped unseen (plus Opus):', len(sh), len(pr), 'p', mc(len(sh - pr), len(pr - sh)))
json.dump({'calibration': {'both_yes': cal, 'n': n13}, 'opus': {'verbatim_yes': ok, 'unquoted_yes': unq, 'n': n}, 'rescored': out}, open(f'{R}/v26_scores.json', 'w'), indent=1)
