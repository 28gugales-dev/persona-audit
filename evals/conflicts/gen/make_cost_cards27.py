"""PLAN v27 part 2: blind real/not labels for the cards every main prompt returns on its first run, all 30 histories, capped at 8
as Persona does, plus a keyed and a control anchor per history (same label prompt and layout as make_cost_cards23.py; one fresh batch).
Writes haiku_in/label__cost27_<i>{,_s}.txt and results/cost27_cards_map.json. Run: python3 evals/conflicts/gen/make_cost_cards27.py <repo root>"""
import json, sys, random, hashlib, collections, os, contextlib, io
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen'); sys.argv = [sys.argv[0], ROOT]
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
reqs = lambda *fs: {r['case']: r for f in fs for r in map(json.loads, open(f'{R}/{f}')) if r['kind'] == 'realN'}
def pairs(r, run=1):
    p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
    if not os.path.exists(p): return None
    t = open(p).read()
    try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: g = {}
    when = {e['id']: e['when'] + e['id'] for e in r['body']['excerpts']}
    return sorted({tuple(sorted(q, key=when.get)) for q in S.pairs(r, g)}, key=lambda q: (when[q[1]], when[q[0]]))
SYS = open(f'{R}/haiku_in/label__naivecards.txt').read().split('=== SYSTEM PROMPT ===\n')[1].split('\n\n=== USER MESSAGE ===')[0]
ARMS = {'shipped': ('requests_v17.jsonl', 'requests_v18_3_prod.jsonl', 'requests_v18c_prod.jsonl', 'requests_v21_prod.jsonl'),
        'naive400': ('requests_v14.jsonl', 'requests_v25_naive_f1.jsonl', 'requests_v19_fresh2_naive.jsonl', 'requests_v21_naive.jsonl'),
        'naiveLong': ('requests_v27_naive_long.jsonl',),
        'realX400': ('requests_v15.jsonl', 'requests_v18_3_realX.jsonl', 'requests_v19_fresh2_realX.jsonl', 'requests_v21_realX.jsonl'),
        'prodPara': ('requests_v24_prodpara.jsonl',), 'gs2': ('requests_v23_gs2.jsonl',),
        'ships': ('requests_v18b_long.jsonl', 'requests_v18c_realX.jsonl', 'requests_v21_dep_realX.jsonl')}
cards, per = [], collections.defaultdict(dict)
for arm, fs in ARMS.items():
    rq = reqs(*fs); assert len(rq) == 30, (arm, len(rq))
    for c, r in sorted(rq.items()):
        ps = pairs(r); assert ps is not None, (arm, c)
        per[c][arm] = min(len(ps), 8)
        T = {e['id']: (e['when'], e['text']) for e in r['body']['excerpts']}
        cards += [{'arm': arm, 'case': c, 'a': x, 'b': y, 'ta': T[x], 'tb': T[y]} for x, y in ps[:8]]
        if arm == 'ships':
            for kind, x in (('key', f'{c}_early'), ('control', f'{c}_control')):
                if x in T and f'{c}_announced' in T: cards.append({'arm': 'anchor_' + kind, 'case': c, 'a': x, 'b': f'{c}_announced', 'ta': T[x], 'tb': T[f'{c}_announced']})
for x in cards: x['card'] = hashlib.sha256(f"v27|{x['arm']}|{x['case']}|{x['a']}|{x['b']}".encode()).hexdigest()[:8]
random.Random('v27-order').shuffle(cards)
files = []
for i in range(0, len(cards), 50):
    n = f'label__cost27_{i // 50}'; files.append(n)
    user = '\n\n'.join(f'<card id="{x["card"]}">\n<earlier written="{x["ta"][0]}">\n{x["ta"][1]}\n</earlier>\n<later written="{x["tb"][0]}">\n{x["tb"][1]}\n</later>\n</card>' for x in cards[i:i + 50])
    for suf in ('', '_s'): open(f'{R}/haiku_in/{n}{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n{user}\n')
json.dump({'cards': [{k: v for k, v in x.items() if k not in ('ta', 'tb')} for x in cards], 'per_history': per, 'files': files}, open(f'{R}/cost27_cards_map.json', 'w'), indent=1)
print(collections.Counter(x['arm'] for x in cards), len(files), 'files')
