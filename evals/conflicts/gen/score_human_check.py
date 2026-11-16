"""Agreement of the author's hand labels with the Claude card labels (Sonnet, Opus, both-real) on the 20 sampled cards.
Run: python3 evals/conflicts/gen/score_human_check.py <repo root>"""
import json, sys
D = f'{sys.argv[1]}/paper/human_check'
cards, key, H = json.load(open(f'{D}/cards.json')), json.load(open(f'{D}/key.json')), json.load(open(f'{D}/human.json'))['marks']
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(v) / n) * (b.count(v) / n) for v in ('real', 'not'))
    return round((po - pe) / (1 - pe), 2)
h = [H[str(c['n'])] for c in cards]
k = [key[c['card']] for c in cards]
out = {'n': len(h), 'human_real': h.count('real')}
for name, lab in (('both', ['real' if x['sonnet'] == x['opus'] == 'real' else 'not' for x in k]), ('sonnet', [x['sonnet'] for x in k]), ('opus', [x['opus'] for x in k])):
    out[name] = {'agree': sum(a == b for a, b in zip(h, lab)), 'kappa': kappa(h, lab), 'claude_real': lab.count('real'),
                 'disagree': [(c['n'], key[c['card']]['arm'], key[c['card']]['case'], hh, ll) for c, hh, ll in zip(cards, h, lab) if hh != ll]}
# precision of 'both real' as judged by the human: of cards Claude called genuine, how many the human called real
both = out['both']
cr = [hh for hh, x in zip(h, k) if x['sonnet'] == x['opus'] == 'real']
out['human_real_given_both_real'] = f"{cr.count('real')}/{len(cr)}"
cn = [hh for hh, x in zip(h, k) if not x['sonnet'] == x['opus'] == 'real']
out['human_not_given_not_both'] = f"{cn.count('not')}/{len(cn)}"
json.dump(out, open(f'{D}/scores.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
