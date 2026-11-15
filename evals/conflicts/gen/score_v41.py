"""PLAN v41: the word-theme path on the 30 long histories (requests_v41_themes.jsonl, one run). A case is found when any theme
request returns its key pair or a cross-era pair both thesis labellers call yes (maps through x24, plus x25 for this round).
Writes paper/results/v41_scores.json with per-case finds, cards per history and the still-unlabelled cross-era pairs.
Run: python3 evals/conflicts/gen/score_v41.py <repo root>"""
import json, sys, re, os, contextlib, io, collections
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen'); sys.argv = [sys.argv[0], ROOT]
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
yes, labelled = set(), set()
for m in ['', '3'] + [f'x{i}' for i in range(3, 26)]:
    base = f'label__thesis{m}'
    if not os.path.exists(f'{R}/thesis_cards_map{m}.json') or not os.path.exists(f'{R}/haiku_raw/{base}.r1.txt') or not os.path.exists(f'{R}/haiku_raw/{base}_s.r1.txt'): continue
    L = []
    for f in (base, base + '_s'):
        t = open(f'{R}/haiku_raw/{f}.r1.txt').read(); L.append({x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']})
    for c in json.load(open(f'{R}/thesis_cards_map{m}.json')):
        k = (c['case'], c.get('early', f"{c['case']}_early"), c['later']); labelled.add(k)
        if all(l.get(c['card']) == 'yes' for l in L): yes.add(k)
side = lambda c, x: 'E' if x == f'{c}_early' or re.fullmatch(f'{c}_e\\d+', x) else 'L' if re.fullmatch(f'{c}_(announced|unannounced|l\\d+)', x) else None
found, cards, ctl, unl, missing = collections.defaultdict(bool), collections.defaultdict(set), collections.Counter(), set(), 0
for l in open(f'{R}/requests_v41_themes.jsonl'):
    r = json.loads(l); c = r['case']; found[c] |= False
    p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r1.txt"
    if not os.path.exists(p): missing += 1; continue
    t = open(p).read()
    try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: g = {}
    ps = S.pairs(r, g); cards[c] |= ps  # one card per pair, as mergeFound files a pair once
    for q in ps:
        if f'{c}_control' in q: ctl[c] += 1
        a, b = sorted(q, key=lambda x: side(c, x) or 'Z')
        if side(c, a) != 'E' or side(c, b) != 'L': continue
        if a == f'{c}_early' and b in (f'{c}_announced', f'{c}_unannounced'): found[c] = True
        elif (c, a, b) in yes: found[c] = True
        elif (c, a, b) not in labelled: unl.add(f'themes|{c}|{a}|{b}')
out = {'found': sum(found.values()), 'cases': len(found), 'found_cases': sorted(c for c, v in found.items() if v), 'cards': sum(map(len, cards.values())),
       'cards_per_history': round(sum(map(len, cards.values())) / len(found), 2), 'control_pairs': sum(ctl.values()), 'missing_runs': missing, 'unlabelled': sorted(unl)}
json.dump(out, open(f'{R}/v41_scores.json', 'w'), indent=1)
print({k: v for k, v in out.items() if k != 'unlabelled'}, 'unlabelled:', len(unl))
