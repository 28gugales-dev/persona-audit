"""PLAN v20 scoring: cards per history and the share both blind labellers (Haiku, Sonnet) call a real change or tension, per arm.
Reads results/cost_cards_map.json and haiku_raw/label__cost<i>{,_s}.r1.txt. Writes results/cost_scores.json.
Run: python3 evals/conflicts/gen/score_cost.py <repo root> [map prefix: cost (default) | cost23]"""
import json, sys, collections
R = f'{sys.argv[1]}/paper/results'
P = sys.argv[2] if len(sys.argv) > 2 else 'cost'
M = json.load(open(f'{R}/{P}_cards_map.json'))
L = [{}, {}]
for f in M['files']:
    for i, suf in enumerate(('', '_s')):
        t = open(f'{R}/haiku_raw/{f}{suf}.r1.txt').read()
        L[i].update({x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']})
n = len(M['per_history']); out = {}
for arm in ('production', 'realX', 'deployed', 'ships', 'anchor_key', 'anchor_control'):
    if not any(c['arm'] == arm for c in M['cards']): continue
    cs = [c for c in M['cards'] if c['arm'] == arm]
    lab = [(L[0].get(c['card']), L[1].get(c['card'])) for c in cs]
    out[arm] = {'cards': len(cs), 'per_history': round(len(cs) / n, 2), 'both_real': sum(a == b == 'real' for a, b in lab),
                'haiku_real': sum(a == 'real' for a, _ in lab), 'sonnet_real': sum(b == 'real' for _, b in lab),
                'both_not': sum(a == b == 'not' for a, b in lab), 'missing': sum(None in x for x in lab),
                'agree': sum(a == b for a, b in lab)}
    o = out[arm]; o['both_real_share'] = round(o['both_real'] / max(len(cs), 1), 2); o['not_real_per_history'] = round((len(cs) - o['both_real']) / n, 2)
out['over_cap'] = sum(v.get('deployed_uncapped', v.get('uncapped', 0)) > 8 for v in M['per_history'].values())
json.dump(out, open(f'{R}/{P}_scores.json', 'w'), indent=1)
for k, v in out.items(): print(k, v)
