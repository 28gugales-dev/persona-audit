"""Human check of the card labels behind the 88% vs 50% precision figure (cost32: depNoCap, naive400).
Samples 10 cards both Claude labellers called real and 10 they did not (seed fixed), blind to arm, author and labels.
Writes paper/human_check/cards.json (what the human sees) and key.json (arm + Claude labels, for scoring only).
Run: python3 evals/conflicts/gen/make_human_check.py <repo root>"""
import json, random, re, sys
root = sys.argv[1]; R = f'{root}/paper/results'
M = json.load(open(f'{R}/cost32_cards_map.json'))
L = [{}, {}]
for f in M['files']:
    for i, s in enumerate(('_s', '_o')):
        t = open(f'{R}/haiku_raw/{f}{s}.r1.txt').read()
        L[i].update({x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']})
text = {}
for f in M['files']:
    t = open(f'{R}/haiku_in/{f}_s.txt').read()
    for m in re.finditer(r'<card id="(\w+)">\s*<earlier written="([^"]+)">\s*(.*?)\s*</earlier>\s*<later written="([^"]+)">\s*(.*?)\s*</later>', t, re.S):
        text[m[1]] = dict(earlier_date=m[2], earlier=m[3], later_date=m[4], later=m[5])
pool = [c for c in M['cards'] if c['arm'] in ('depNoCap', 'naive400')]
real = [c for c in pool if L[0][c['card']] == L[1][c['card']] == 'real']
notr = [c for c in pool if c not in real]
rng = random.Random(20261115)
pick = rng.sample(real, 10) + rng.sample(notr, 10)
rng.shuffle(pick)
assert all(c['card'] in text for c in pick) and len({c['card'] for c in pick}) == 20
json.dump([dict(n=i + 1, card=c['card'], **text[c['card']]) for i, c in enumerate(pick)], open(f'{root}/paper/human_check/cards.json', 'w'), indent=1)
json.dump({c['card']: dict(arm=c['arm'], case=c['case'], sonnet=L[0][c['card']], opus=L[1][c['card']]) for c in pick}, open(f'{root}/paper/human_check/key.json', 'w'), indent=1)
print(len(real), len(notr), sum(len(text[c['card']]['earlier']) + len(text[c['card']]['later']) for c in pick), 'chars')
