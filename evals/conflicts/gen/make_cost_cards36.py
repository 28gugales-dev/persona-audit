"""PLAN v36: two-work histories without the documented change; first-run cards of Persona now and naive, plus a control anchor (control x first later-work paragraph); one shuffled batch of every main prompt's first-run cards (real and no-change histories) by Sonnet (_s) and Opus (_o), no Haiku; adapted from make_cost_cards30.py.
: blind real/not labels for the cards every main prompt returns on its first run, all 30 histories, capped at 8
as Persona does, plus a keyed and a control anchor per history (same label prompt and layout as make_cost_cards23.py; one fresh batch).
Writes haiku_in/label__cost36_<i>{_s,_o}.txt and results/cost36_cards_map.json. Run: python3 evals/conflicts/gen/make_cost_cards36.py <repo root>"""
import json, sys, random, hashlib, collections, os, contextlib, io
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen'); sys.argv = [sys.argv[0], ROOT]
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
reqs = lambda *fs: {r['case']: r for f in fs for r in map(json.loads, open(f'{R}/{f}')) if r['kind'] in ('realN', 'nochange')}
def pairs(r, run=1):
    p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
    if not os.path.exists(p): return None
    t = open(p).read()
    try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: g = {}
    when = {e['id']: e['when'] + e['id'] for e in r['body']['excerpts']}
    return sorted({tuple(sorted(q, key=when.get)) for q in S.pairs(r, g)}, key=lambda q: (when[q[1]], when[q[0]]))
SYS = open(f'{R}/haiku_in/label__naivecards.txt').read().split('=== SYSTEM PROMPT ===\n')[1].split('\n\n=== USER MESSAGE ===')[0]
ARMS = {'tw_depNoCap': ('requests_v36_v36n.jsonl',), 'tw_naive': ('requests_v36_v36v.jsonl',)}
cards, per = [], collections.defaultdict(dict)
for arm, fs in ARMS.items():
    rq = reqs(*fs); assert len(rq) == 30, (arm, len(rq))
    for c, r in sorted(rq.items()):
        ps = pairs(r); assert ps is not None, (arm, c)
        per[c][arm] = min(len(ps), 8)
        T = {e['id']: (e['when'], e['text']) for e in r['body']['excerpts']}
        cards += [{'arm': arm, 'case': c, 'a': x, 'b': y, 'ta': T[x], 'tb': T[y]} for x, y in ps[:8]]
        if arm == 'tw_depNoCap' and f'{c}_control' in T:
            ls = sorted((e for e in r['body']['excerpts'] if e['id'].startswith(f'{c}_l')), key=lambda e: (e['when'], e['id']))
            cards.append({'arm': 'anchor_control', 'case': c, 'a': f'{c}_control', 'b': ls[0]['id'], 'ta': T[f'{c}_control'], 'tb': T[ls[0]['id']]})
for x in cards: x['card'] = hashlib.sha256(f"v36|{x['arm']}|{x['case']}|{x['a']}|{x['b']}".encode()).hexdigest()[:8]
assert len({x['card'] for x in cards}) == len(cards)
random.Random('v36-order').shuffle(cards)
files = []
for i in range(0, len(cards), 50):
    n = f'label__cost36_{i // 50}'; files.append(n)
    user = '\n\n'.join(f'<card id="{x["card"]}">\n<earlier written="{x["ta"][0]}">\n{x["ta"][1]}\n</earlier>\n<later written="{x["tb"][0]}">\n{x["tb"][1]}\n</later>\n</card>' for x in cards[i:i + 50])
    for suf in ('_s', '_o'): open(f'{R}/haiku_in/{n}{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n{user}\n')
json.dump({'cards': [{k: v for k, v in x.items() if k not in ('ta', 'tb')} for x in cards], 'per_history': per, 'files': files}, open(f'{R}/cost36_cards_map.json', 'w'), indent=1)
print(collections.Counter(x['arm'] for x in cards), len(files), 'files')
