"""PLAN v41: one fresh shuffled Sonnet (_s) + Opus (_o) batch, round-27 real/not prompt: longBig's first-run cards on the 30 long
histories (cap 8, as round 40) and every card the word-theme path returned on the same histories (one card per pair, first 8 per
request as the API keeps them), each shown with the text the model saw, plus a keyed and a control anchor per history.
Writes haiku_in/label__cost41_<i>{_s,_o}.txt and results/cost41_cards_map.json. Run: python3 evals/conflicts/gen/make_cost_cards41.py <repo root>"""
import json, sys, random, hashlib, collections, os, contextlib, io
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen'); sys.argv = [sys.argv[0], ROOT]
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
def raw(r, run=1):
    p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
    t = open(p).read()
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}
def ordered(r, g):  # pairs in the model's order, as readConflicts keeps the first 8
    ids = [e['id'] for e in r['body']['excerpts']]; out = []
    for x in (g or {}).get('conflicts', []):
        try: q = frozenset((ids[int(x['a'][1:]) - 1], ids[int(x['b'][1:]) - 1]))
        except Exception: continue
        if len(q) == 2 and q not in out: out.append(q)
    return out[:8]
SYS = open(f'{R}/haiku_in/label__naivecards.txt').read().split('=== SYSTEM PROMPT ===\n')[1].split('\n\n=== USER MESSAGE ===')[0]
cards, per = [], collections.defaultdict(dict)
big = {r['case']: r for r in map(json.loads, open(f'{R}/requests_v40_longbig.jsonl'))}
for c, r in sorted(big.items()):
    T = {e['id']: (e['when'], e['text']) for e in r['body']['excerpts']}
    when = {e['id']: e['when'] + e['id'] for e in r['body']['excerpts']}
    ps = [tuple(sorted(q, key=when.get)) for q in ordered(r, raw(r))]
    per[c]['longBig'] = len(ps)
    cards += [{'arm': 'longBig', 'case': c, 'a': x, 'b': y, 'ta': T[x], 'tb': T[y]} for x, y in ps]
    for kind, x in (('key', f'{c}_early'), ('control', f'{c}_control')):
        y = f'{c}_announced' if f'{c}_announced' in T else f'{c}_unannounced'
        if x in T and y in T: cards.append({'arm': 'anchor_' + kind, 'case': c, 'a': x, 'b': y, 'ta': T[x], 'tb': T[y]})
seen = collections.defaultdict(set)
for r in map(json.loads, open(f'{R}/requests_v41_themes.jsonl')):
    c = r['case']; per[c].setdefault('themes', 0)
    T = {e['id']: (e['when'], e['text']) for e in r['body']['excerpts']}
    when = {e['id']: e['when'] + e['id'] for e in r['body']['excerpts']}
    for q in ordered(r, raw(r)):
        if q in seen[c]: continue
        seen[c].add(q); x, y = sorted(q, key=when.get); per[c]['themes'] += 1
        cards.append({'arm': 'themes', 'case': c, 'a': x, 'b': y, 'ta': T[x], 'tb': T[y]})
for x in cards: x['card'] = hashlib.sha256(f"v41|{x['arm']}|{x['case']}|{x['a']}|{x['b']}".encode()).hexdigest()[:8]
assert len({x['card'] for x in cards}) == len(cards) and len(per) == 30
random.Random('v41-order').shuffle(cards)
files = []
for i in range(0, len(cards), 50):
    n = f'label__cost41_{i // 50}'; files.append(n)
    user = '\n\n'.join(f'<card id="{x["card"]}">\n<earlier written="{x["ta"][0]}">\n{x["ta"][1]}\n</earlier>\n<later written="{x["tb"][0]}">\n{x["tb"][1]}\n</later>\n</card>' for x in cards[i:i + 50])
    for suf in ('_s', '_o'): open(f'{R}/haiku_in/{n}{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n{user}\n')
json.dump({'cards': [{k: v for k, v in x.items() if k not in ('ta', 'tb')} for x in cards], 'per_history': per, 'files': files}, open(f'{R}/cost41_cards_map.json', 'w'), indent=1)
print(collections.Counter(x['arm'] for x in cards), len(files), 'files')
