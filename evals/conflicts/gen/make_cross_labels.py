"""PLAN v18b: blind thesis labels for every CROSS-ERA pair (one side from the early work: the early passage or an e-paragraph; the other
from the later work: announced, unannounced or an l-paragraph) that a whole-history arm returned and no earlier label round covered,
plus 2 random unreturned e x l decoys per case and the key pairs as anchors. Same label prompt as make_thesis_labels.py.
Writes haiku_in/label__thesisx{SUF}{,_s}.txt and results/thesis_cards_mapx{SUF}.json.
Run: python3 evals/conflicts/gen/make_cross_labels.py <repo root> [3]"""
import json, sys, re, random, hashlib, os, contextlib, io
ROOT = sys.argv[1]; SUF = sys.argv[2] if len(sys.argv) > 2 else ''; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
cases = {c['id']: c for f in ('realtext_cases.json', 'realtext_cases2.json', 'realtext_cases3.json') for c in json.load(open(f'{ROOT}/paper/data/{f}'))}
FILES = {'': ('requests_v14.jsonl', 'requests_v15.jsonl', 'requests_v17.jsonl', 'requests_v18.jsonl'), '3': ('requests_v18_3_realX.jsonl', 'requests_v18_3_prod.jsonl')}[SUF]
done = set()
for m in ('', '3', 'x', 'x3'):
    p = f'{R}/thesis_cards_map{m}.json'
    if os.path.exists(p): done |= {(c['case'], c.get('early', f"{c['case']}_early"), c['later']) for c in json.load(open(p))}
side = lambda c, x: 'E' if x == f'{c}_early' or re.fullmatch(f'{c}_e\\d+', x) else 'L' if re.fullmatch(f'{c}_(announced|unannounced|l\\d+)', x) else None
reqs, want = {}, {}
for f in FILES:
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        c = r['case']; reqs[c] = r
        for run in range(1, 7):
            try: t = open(f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt").read(); g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: continue
            for p in S.pairs(r, g):
                a, b = sorted(p, key=lambda x: side(c, x) or 'Z')
                if side(c, a) == 'E' and side(c, b) == 'L' and (c, a, b) not in done: want[(c, a, b)] = 'returned'
for c, r in reqs.items():
    ids = [e['id'] for e in r['body']['excerpts']]
    for k in ('announced', 'unannounced'):
        if f'{c}_{k}' in ids: want[(c, f'{c}_early', f'{c}_{k}')] = 'key'
    rng = random.Random(f'v18x:{c}')
    es = [i for i in ids if re.fullmatch(f'{c}_e\\d+', i)]; ls = [i for i in ids if re.fullmatch(f'{c}_l\\d+', i)]
    for _ in range(2):
        pr = (c, rng.choice(es), rng.choice(ls))
        if pr not in want and pr not in done: want[pr] = 'decoy'
text = {c: {e['id']: e['text'] for e in r['body']['excerpts']} for c, r in reqs.items()}
rows = [{'card': hashlib.sha256(f'x|{c}|{a}|{b}'.encode()).hexdigest()[:8], 'case': c, 'early': a, 'later': b, 'kind': k} for (c, a, b), k in want.items()]
random.Random(f'v18x-order{SUF}').shuffle(rows)
SYS = open(f'{R}/haiku_in/label__thesis.txt').read().split('=== SYSTEM PROMPT ===\n')[1].split('\n\n=== USER MESSAGE ===')[0]
user = '\n\n'.join(f'<card id="{x["card"]}">\n<question>{cases[x["case"]]["thesis"]}</question>\n<earlier>\n{text[x["case"]][x["early"]]}\n</earlier>\n<later>\n{text[x["case"]][x["later"]]}\n</later>\n</card>' for x in rows)
for suf in ('', '_s'):
    open(f'{R}/haiku_in/label__thesisx{SUF}{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n{user}\n')
json.dump(rows, open(f'{R}/thesis_cards_mapx{SUF}.json', 'w'), indent=1)
from collections import Counter; print(len(rows), Counter(x['kind'] for x in rows))
