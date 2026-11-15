"""Rounds 32-40: real/not card labels by Sonnet (_s) and Opus (_o); a card is genuine when both say real.
Reads results/<prefix>_cards_map.json and haiku_raw/label__<prefix>_<i>{_s,_o}.r1.txt. Writes results/<prefix>_scores.json.
Run: python3 evals/conflicts/gen/score_cost_so.py <repo root> <prefix: cost40>"""
import json, sys
R, P = f'{sys.argv[1]}/paper/results', sys.argv[2]
M = json.load(open(f'{R}/{P}_cards_map.json'))
L = [{}, {}]
for f in M['files']:
    for i, s in enumerate(('_s', '_o')):
        t = open(f'{R}/haiku_raw/{f}{s}.r1.txt').read()
        L[i].update({x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']})
n = len(M['per_history']); out = {}
for arm in sorted({c['arm'] for c in M['cards']}):
    cs = [c for c in M['cards'] if c['arm'] == arm]
    lab = [(L[0].get(c['card']), L[1].get(c['card'])) for c in cs]
    real = sum(a == b == 'real' for a, b in lab)
    out[arm] = {'cards': len(cs), 'both_real': real, 'share': round(real / max(len(cs), 1), 2), 'not_per_history': round((len(cs) - real) / n, 2),
                'genuine_per_history': round(real / n, 2), 'missing': sum(None in x for x in lab)}
json.dump(out, open(f'{R}/{P}_scores.json', 'w'), indent=1)
for k, v in out.items(): print(k, v)
