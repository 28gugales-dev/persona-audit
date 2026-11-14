"""Score PLAN v15: whole history with realX on the 12 real histories, beside the v14 naive baseline.
Writes paper/results/v15_scores.json and, for blind labels, wh_cards_blind.json / wh_cards_map.json.
Run: python3 evals/conflicts/gen/score_v15.py <repo root>"""
import json, sys, os, random, hashlib, contextlib, io
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'
held = {c['id'] for c in json.load(open(f'{sys.argv[1]}/paper/data/realtext_cases2.json'))}
reqs = [json.loads(l) for l in open(f'{R}/requests_v15.jsonl')]
out = {'cases': {}}; cards = []
for r in reqs:
    g = S.raw(r['id'].replace(':', '__')); ps = S.pairs(r, g); text = {e['id']: e for e in r['body']['excerpts']}
    row = {'pairs_returned': len(ps), 'control_flagged': any(f"{r['case']}_control" in p for p in ps)}
    for later in ('announced', 'unannounced'):
        e, l = f"{r['case']}_early", f"{r['case']}_{later}"
        if l in text: row[later] = frozenset((e, l)) in ps
    out['cases'][r['case']] = row
    for p in ps:
        x, y = sorted(p, key=lambda i: text[i]['when'])
        cards.append({'card': hashlib.sha1(f"wh{(r['case'], x, y)}".encode()).hexdigest()[:8], 'case': r['case'], 'a': x, 'b': y,
                      'earlier': {'written': text[x]['when'], 'text': text[x]['text']}, 'later': {'written': text[y]['when'], 'text': text[y]['text']}})
pairs = [(c, k, v[k]) for c, v in out['cases'].items() for k in ('announced', 'unannounced') if k in v]
out['summary'] = {'surfaced': sum(p[2] for p in pairs), 'pairs': len(pairs), 'held_surfaced': sum(p[2] for p in pairs if p[0] in held),
                  'held_pairs': sum(p[0] in held for p in pairs), 'pairs_returned_per_history': sum(v['pairs_returned'] for v in out['cases'].values()) / len(reqs),
                  'controls_flagged': sum(v['control_flagged'] for v in out['cases'].values())}
blind = [{k: c[k] for k in ('card', 'earlier', 'later')} for c in cards]
random.Random(20261116).shuffle(blind)
json.dump(blind, open(f'{R}/wh_cards_blind.json', 'w'), indent=1)
json.dump([{k: c[k] for k in ('card', 'case', 'a', 'b')} for c in cards], open(f'{R}/wh_cards_map.json', 'w'), indent=1)
lab = {}
for f, who in (('label__whcards', 'haiku'), ('label__whcards_s', 'sonnet')):
    p = f'{R}/haiku_raw/{f}.r1.txt'
    if not os.path.exists(p): continue
    tt = open(p).read(); lab[who] = {x['card']: x['label'] for x in json.loads(tt[tt.find('{'):tt.rfind('}') + 1])['labels']}
cmap = {c['card']: c['case'] for c in cards}
out['cards'] = {who: {'real': sum(L.get(c) == 'real' for c in cmap), 'n': len(cmap), 'held_real': sum(L.get(c) == 'real' for c in cmap if cmap[c] in held),
                      'held_n': sum(cmap[c] in held for c in cmap)} for who, L in lab.items()}
json.dump(out, open(f'{R}/v15_scores.json', 'w'), indent=1)
print(json.dumps(out['summary'])); print(json.dumps(out['cards']))
for c, v in out['cases'].items(): print(c, v)
