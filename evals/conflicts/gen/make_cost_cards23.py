"""PLAN v23 part 2: blind real/not labels for every card the shipped configuration (realX, longer excerpts; deployed text on fresh
sets 2-3) returns on its first run, all 30 histories, capped at 8 as Persona does, plus a keyed and a control anchor per history.
Same label prompt and layout as make_cost_cards.py. Writes haiku_in/label__cost23_<i>{,_s}.txt and results/cost23_cards_map.json.
Run: python3 evals/conflicts/gen/make_cost_cards23.py <repo root>"""
import json, sys, random, hashlib, collections
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen')
import os, contextlib, io
sys.argv = [sys.argv[0], ROOT]
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
reqs = lambda *fs: {r['case']: r for f in fs for r in map(json.loads, open(f'{R}/{f}')) if r['kind'] == 'realN'}
def pairs(r, run):
    p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
    if not os.path.exists(p): return None
    t = open(p).read()
    try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: g = {}
    when = {e['id']: e['when'] + e['id'] for e in r['body']['excerpts']}
    return sorted({tuple(sorted(q, key=when.get)) for q in S.pairs(r, g)}, key=lambda q: (when[q[1]], when[q[0]]))
SYS = open(f'{R}/haiku_in/label__naivecards.txt').read().split('=== SYSTEM PROMPT ===\n')[1].split('\n\n=== USER MESSAGE ===')[0]
ships = reqs('requests_v18b_long.jsonl', 'requests_v18c_realX.jsonl', 'requests_v21_dep_realX.jsonl')
cards, per = [], {}
for c, r in sorted(ships.items()):
    ps = pairs(r, 1)
    per[c] = {'ships': min(len(ps or []), 8), 'uncapped': len(ps or []), 'missing': ps is None}
    T = {e['id']: (e['when'], e['text']) for e in r['body']['excerpts']}
    cards += [{'arm': 'ships', 'case': c, 'a': x, 'b': y, 'ta': T[x], 'tb': T[y]} for x, y in (ps or [])[:8]]
    for kind, x in (('key', f'{c}_early'), ('control', f'{c}_control')):
        if x in T and f'{c}_announced' in T: cards.append({'arm': 'anchor_' + kind, 'case': c, 'a': x, 'b': f'{c}_announced', 'ta': T[x], 'tb': T[f'{c}_announced']})
for x in cards: x['card'] = hashlib.sha256(f"v23|{x['arm']}|{x['case']}|{x['a']}|{x['b']}".encode()).hexdigest()[:8]
random.Random('v23-order').shuffle(cards)
files = []
for i in range(0, len(cards), 50):
    n = f'label__cost23_{i // 50}'; files.append(n)
    user = '\n\n'.join(f'<card id="{x["card"]}">\n<earlier written="{x["ta"][0]}">\n{x["ta"][1]}\n</earlier>\n<later written="{x["tb"][0]}">\n{x["tb"][1]}\n</later>\n</card>' for x in cards[i:i + 50])
    for suf in ('', '_s'): open(f'{R}/haiku_in/{n}{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n{user}\n')
json.dump({'cards': [{k: v for k, v in x.items() if k not in ('ta', 'tb')} for x in cards], 'per_history': per, 'files': files}, open(f'{R}/cost23_cards_map.json', 'w'), indent=1)
print(len(per), 'histories', collections.Counter(x['arm'] for x in cards), files, 'per history', round(sum(v['ships'] for v in per.values()) / len(per), 2),
      'over cap', sum(v['uncapped'] > 8 for v in per.values()), 'missing', [c for c, v in per.items() if v['missing']])
