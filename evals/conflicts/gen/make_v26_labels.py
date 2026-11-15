"""v26: hard-negative calibration (control x announced/unannounced) for Haiku+Sonnet, and an evidence-quoting third judge (Opus)
on the credited off-key pairs, the hard negatives and the keys. Passages are history paragraphs cut to 1,000 characters.
Run: python3 evals/conflicts/gen/make_v26_labels.py <repo root> <offkey_pairs.json>"""
import json, sys, random, hashlib, os
ROOT, OFF = sys.argv[1:3]; R = f'{ROOT}/paper/results'
cases = {c['id']: c for f in ('', '2', '3', '4', '5') if os.path.exists(f'{ROOT}/paper/data/realtext_cases{f}.json') for c in json.load(open(f'{ROOT}/paper/data/realtext_cases{f}.json'))}
text = {h['case']: {p['id']: p['body'][:1000] for p in h['posts']} for f in ('', '2', '3', '4', '5') if os.path.exists(f'{ROOT}/paper/data/realtext_histories{f}.json') for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{f}.json'))}
want = {}
for c, t in text.items():
    for k in ('announced', 'unannounced'):
        if f'{c}_{k}' in t:
            want[(c, f'{c}_early', f'{c}_{k}')] = 'key'
            if f'{c}_control' in t: want[(c, f'{c}_control', f'{c}_{k}')] = 'hardneg'
SYS = open(f'{R}/haiku_in/label__thesis.txt').read().split('=== SYSTEM PROMPT ===\n')[1].split('\n\n=== USER MESSAGE ===')[0]
card = lambda x: f'<card id="{x["card"]}">\n<question>{cases[x["case"]]["thesis"]}</question>\n<earlier>\n{text[x["case"]][x["early"]]}\n</earlier>\n<later>\n{text[x["case"]][x["later"]]}\n</later>\n</card>'
def rows_of(w, M):
    rows = [{'card': hashlib.sha256(f'{M}|{c}|{a}|{b}'.encode()).hexdigest()[:8], 'case': c, 'early': a, 'later': b, 'kind': k} for (c, a, b), k in w.items()]
    random.Random(f'v26{M}-order').shuffle(rows); return rows
# 1. Haiku + Sonnet: keys + hard negatives, usual prompt
rows = rows_of(want, 'x13')
for suf in ('', '_s'):
    open(f'{R}/haiku_in/label__thesisx13{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n' + '\n\n'.join(map(card, rows)) + '\n')
json.dump(rows, open(f'{R}/thesis_cards_mapx13.json', 'w'), indent=1)
# 2. Opus: + credited off-key pairs, with a verbatim quote for each yes; four files
w2 = dict(want)
for c, a, b in json.load(open(OFF)): w2.setdefault((c, a, b), 'offkey')
rows2 = rows_of(w2, 'opus26')
SYS2 = SYS + '\n\nFor each card you answer "yes", also give "quote": the words of the <later> passage that reject or abandon the earlier view, copied exactly (at most 30 words). Reply as JSON: {"labels": [{"card": "...", "label": "yes"|"no", "quote": "..."}]}'
for i in range(4):
    part = rows2[i::4]
    open(f'{R}/haiku_in/label__opus26_{i}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS2}\n\n=== USER MESSAGE ===\n' + '\n\n'.join(map(card, part)) + '\n')
json.dump(rows2, open(f'{R}/thesis_cards_mapopus26.json', 'w'), indent=1)
from collections import Counter; print(len(rows), Counter(x['kind'] for x in rows), len(rows2), Counter(x['kind'] for x in rows2))
