"""PLAN v20: blind "real change or tension" labels for every card the shipped prompt, realX (400 characters) and the deployed
configuration (realX + changes, longer excerpts, merged and capped at 8) return on their first run or look, all 24 histories,
plus a keyed and a control anchor per history. Writes haiku_in/label__cost<i>{,_s}.txt and results/cost_cards_map.json.
Run: python3 evals/conflicts/gen/make_cost_cards.py <repo root>"""
import json, sys, os, random, hashlib, contextlib, io, collections
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen')
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
    out = []
    for q in S.pairs(r, g):
        q = sorted(q, key=when.get)
        if q not in out: out.append(q)
    return out
prod = reqs('requests_v17.jsonl', 'requests_v18_3_prod.jsonl', 'requests_v18c_prod.jsonl')
rx = reqs('requests_v15.jsonl', 'requests_v18_3_realX.jsonl', 'requests_v19_fresh2_realX.jsonl')
dA = reqs('requests_v18b_long.jsonl', 'requests_v18c_realX.jsonl')
dB = reqs('requests_v18b_chglong.jsonl', 'requests_v18c_changes.jsonl')
cards, per = [], {}
for c in sorted(set(prod) & set(rx) & set(dA) & set(dB)):
    a, b, d1, d2 = pairs(prod[c], 1), pairs(rx[c], 1), pairs(dA[c], 1), pairs(dB[c], 1)
    dep = (d1 or []) + [q for q in (d2 or []) if q not in (d1 or [])]
    per[c] = {'production': len(a or []), 'realX': len(b or []), 'deployed': min(len(dep), 8), 'deployed_uncapped': len(dep),
              'missing': [n for n, x in (('production', a), ('realX', b), ('realX_long', d1), ('changes_long', d2)) if x is None]}
    for arm, ps, src in (('production', a or [], prod[c]), ('realX', b or [], rx[c]), ('deployed', dep[:8], dA[c])):
        T = {e['id']: (e['when'], e['text']) for e in src['body']['excerpts']}
        cards += [{'arm': arm, 'case': c, 'a': x, 'b': y, 'ta': T[x], 'tb': T[y]} for x, y in ps]
    T = {e['id']: (e['when'], e['text']) for e in dA[c]['body']['excerpts']}
    for kind, x in (('key', f'{c}_early'), ('control', f'{c}_control')):
        if x in T and f'{c}_announced' in T: cards.append({'arm': 'anchor_' + kind, 'case': c, 'a': x, 'b': f'{c}_announced', 'ta': T[x], 'tb': T[f'{c}_announced']})
for x in cards: x['card'] = hashlib.sha256(f"v20|{x['arm']}|{x['case']}|{x['a']}|{x['b']}".encode()).hexdigest()[:8]
random.Random('v20-order').shuffle(cards)
SYS = open(f'{R}/haiku_in/label__naivecards.txt').read().split('=== SYSTEM PROMPT ===\n')[1].split('\n\n=== USER MESSAGE ===')[0]
files = []
for i in range(0, len(cards), 50):
    n = f'label__cost{i // 50}'; files.append(n)
    user = '\n\n'.join(f'<card id="{x["card"]}">\n<earlier written="{x["ta"][0]}">\n{x["ta"][1]}\n</earlier>\n<later written="{x["tb"][0]}">\n{x["tb"][1]}\n</later>\n</card>' for x in cards[i:i + 50])
    for suf in ('', '_s'): open(f'{R}/haiku_in/{n}{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n{user}\n')
json.dump({'cards': [{k: v for k, v in x.items() if k not in ('ta', 'tb')} for x in cards], 'per_history': per, 'files': files}, open(f'{R}/cost_cards_map.json', 'w'), indent=1)
print(len(per), 'histories', collections.Counter(x['arm'] for x in cards), files)
print({k: round(sum(v[k] for v in per.values()) / len(per), 2) for k in ('production', 'realX', 'deployed')}, 'over cap:', sum(v['deployed_uncapped'] > 8 for v in per.values()),
      'missing:', {c: v['missing'] for c, v in per.items() if v['missing']})
