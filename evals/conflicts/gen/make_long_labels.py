"""PLAN v18b: blind thesis labels (same prompt) for the cross-era pairs the long-excerpt arms returned that no earlier round labelled,
shown with the long text the model saw, plus each history's key pairs and 1 random e x l decoy, as anchors.
Reads the unlabelled list from v18b_scores.json. Writes haiku_in/label__thesisx4{,_s}.txt and results/thesis_cards_mapx4.json.
Run: python3 evals/conflicts/gen/make_long_labels.py <repo root> [map suffix, default x4] [request files, comma-separated] [arm]
(x5: changes_v1 at 400 characters on fresh1, requests_v18b_chg3.jsonl, arm "changes")"""
import json, sys, re, random, hashlib
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
M = sys.argv[2] if len(sys.argv) > 2 else 'x4'
FILES = sys.argv[3].split(',') if len(sys.argv) > 3 else ['requests_v18b_long.jsonl', 'requests_v18b_chglong.jsonl']
ARM = sys.argv[4] if len(sys.argv) > 4 else None
cases = {c['id']: c for f in ('realtext_cases.json', 'realtext_cases2.json', 'realtext_cases3.json', 'realtext_cases4.json') for c in json.load(open(f'{ROOT}/paper/data/{f}'))}
text = {}
for f in FILES:
    for l in open(f'{R}/{f}'):
        r = json.loads(l); text[r['case']] = {e['id']: e['text'] for e in r['body']['excerpts']}
want = {}
for u in json.load(open(f'{R}/v18b_scores.json'))['unlabelled']:
    arm, c, a, b = u.split('|')
    if (arm in ARM.split(',') if ARM else arm.endswith('_long')) and c in text: want[(c, a, b)] = 'returned'
for c, t in text.items():
    for k in ('announced', 'unannounced'):
        if f'{c}_{k}' in t: want.setdefault((c, f'{c}_early', f'{c}_{k}'), 'key')
    rng = random.Random(f'v18{M}:{c}')
    pr = (c, rng.choice([i for i in t if re.fullmatch(f'{c}_e\\d+', i)]), rng.choice([i for i in t if re.fullmatch(f'{c}_l\\d+', i)]))
    want.setdefault(pr, 'decoy')
rows = [{'card': hashlib.sha256(f'{M}|{c}|{a}|{b}'.encode()).hexdigest()[:8], 'case': c, 'early': a, 'later': b, 'kind': k} for (c, a, b), k in want.items()]
random.Random(f'v18{M}-order').shuffle(rows)
SYS = open(f'{R}/haiku_in/label__thesis.txt').read().split('=== SYSTEM PROMPT ===\n')[1].split('\n\n=== USER MESSAGE ===')[0]
user = '\n\n'.join(f'<card id="{x["card"]}">\n<question>{cases[x["case"]]["thesis"]}</question>\n<earlier>\n{text[x["case"]][x["early"]]}\n</earlier>\n<later>\n{text[x["case"]][x["later"]]}\n</later>\n</card>' for x in rows)
for suf in ('', '_s'):
    open(f'{R}/haiku_in/label__thesis{M}{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n{user}\n')
json.dump(rows, open(f'{R}/thesis_cards_map{M}.json', 'w'), indent=1)
from collections import Counter; print(len(rows), Counter(x['kind'] for x in rows))
