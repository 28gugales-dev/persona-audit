"""PLAN v40: split the x22 thesis-label batch (197 cards, 3x the largest earlier batch) into x22, x23, x24 in the same shuffled
order, so each labeller reads about 120 KB. Same system prompt and card layout. Run after make_long_labels.py ... x22.
Run: python3 evals/conflicts/gen/split_labels_v40.py <repo root>"""
import json, sys
R = f'{sys.argv[1]}/paper/results'
rows = json.load(open(f'{R}/thesis_cards_mapx22.json'))
whole = open(f'{R}/haiku_in/label__thesisx22.txt').read()
head, user = whole.split('\n\n=== USER MESSAGE ===\n')
cards = {c[c.find('id="') + 4:c.find('id="') + 12]: c for c in ('<card' + x for x in user.rstrip('\n').split('<card')[1:])}
assert len(cards) == len(rows)
k = -(-len(rows) // 3)
for i, m in enumerate(('x22', 'x23', 'x24')):
    part = rows[i * k:(i + 1) * k]
    body = '\n\n'.join(cards[r['card']].rstrip() for r in part)
    for suf in ('', '_s'): open(f'{R}/haiku_in/label__thesis{m}{suf}.txt', 'w').write(f'{head}\n\n=== USER MESSAGE ===\n{body}\n')
    json.dump(part, open(f'{R}/thesis_cards_map{m}.json', 'w'), indent=1)
    print(m, len(part))
