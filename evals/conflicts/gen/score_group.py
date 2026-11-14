"""Score PLAN v12 end to end (model grouping + production / genX). Writes paper/results/group_scores_<tag>.json.
Planted (tag v1_test): positives found and decoys flagged, as in score_rerun.py, paired with the word-sort pipeline runs.
Real (tag v1_real, v2_real2): whether each early+later pair is surfaced; every card goes to group_cards_blind_<tag>.json for blind labels.
Run: python3 evals/conflicts/gen/score_group.py <repo root> <tag>"""
import json, os, sys, random, hashlib, contextlib, io
from collections import defaultdict
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
TAG = sys.argv[2]
R = f'{sys.argv[1]}/paper/results'
reqs = [json.loads(l) for l in open(f'{R}/requests_group_{TAG}.jsonl')]
safe = lambda i: i.replace(':', '__').replace('/', '_')
flags, missing, cards = defaultdict(set), [], []
for r in reqs:
    g = S.raw(safe(r['id']))
    if g is None: missing.append(r['id']); continue
    ps = S.pairs(r, g); flags[(r['prompt_version'], r['history'])] |= ps
    text = {e['id']: e for e in r['body']['excerpts']}
    for p in ps:
        x, y = sorted(p, key=lambda i: text[i]['when'])
        cards.append({'arm': r['prompt_version'], 'history': r['history'], 'a': x, 'b': y, 'a_text': text[x]['text'], 'a_when': text[x]['when'], 'b_text': text[y]['text'], 'b_when': text[y]['when']})
hists = sorted({r['history'] for r in reqs})
ARMS = sorted({r['prompt_version'] for r in reqs})
out = {'missing': missing, 'histories': len(hists), 'requests': len(reqs) // len(ARMS),
       'cards': {arm: sum(len(flags[(arm, h)]) for h in hists) for arm in ARMS}}
if TAG.endswith('test'):
    # word-sort pipeline flags on the same histories (production, PLAN v4 runs)
    word = defaultdict(set)
    for r in S.reqs:
        if r['kind'] == 'pipeline_heldout' and r['prompt_version'] == 'prod' and r['history'] in hists:
            g = S.raw(safe(r['id']))
            if g is not None: word[r['history']] |= S.pairs(r, g)
    for arm in ARMS:
        res = {'POS': [0, 0], 'DECOY': [0, 0]}; gained = lost = 0
        for it in S.key.values():
            if it['set'] != 'test' or it['history'] not in hists: continue
            h = S.item_hit(it, flags[(arm, it['history'])]); k = 'POS' if it['conflict'] else 'DECOY'
            res[k][0] += h; res[k][1] += 1
            if it['conflict']:
                w = S.item_hit(it, word[it['history']]); gained += h and not w; lost += w and not h
        out[arm] = {k: {'k': v[0], 'n': v[1], 'wilson': S.wilson(*v)} for k, v in res.items()}
        out[arm]['vs_word_prod'] = {'gained': gained, 'lost': lost, 'p': S.mcnemar(gained, lost)}
    # cards that join posts of two different planted items (cross-item), the cost the rewrite showed end to end
    item = {p['id']: p['item'] for h in S.hist.values() for p in h['posts']}
    out['cross_item_cards'] = {arm: sum(item.get(c['a']) != item.get(c['b']) for c in cards if c['arm'] == arm) for arm in ARMS}
else:
    hfile = 'realtext_histories.json' if TAG.endswith('real') else f'realtext_histories{TAG.split("real")[-1]}.json'
    present = {p['id'] for h in json.load(open(f'{sys.argv[1]}/paper/data/{hfile}')) for p in h['posts']}
    surfaced = {}
    for h in hists:
        for later in ('announced', 'unannounced'):
            e, l = f'{h}_early', f'{h}_{later}'
            if l not in present: continue
            surfaced[f'{h}/{later}'] = {arm: frozenset((e, l)) in flags[(arm, h)] for arm in ARMS}
    out['surfaced'] = surfaced
    out['surfaced_counts'] = {arm: sum(v[arm] for v in surfaced.values()) for arm in ARMS}
    uniq = {}
    for c in cards: uniq.setdefault((c['history'], c['a'], c['b']), c)
    blind = [{'card': hashlib.sha1(f'g{k}'.encode()).hexdigest()[:8], 'earlier': {'written': v['a_when'], 'text': v['a_text']}, 'later': {'written': v['b_when'], 'text': v['b_text']}} for k, v in uniq.items()]
    random.Random(20261115).shuffle(blind)
    json.dump(blind, open(f'{R}/group_cards_blind_{TAG}.json', 'w'), indent=1)
    json.dump([{'card': hashlib.sha1(f'g{(c["history"], c["a"], c["b"])}'.encode()).hexdigest()[:8], **{k: c[k] for k in ('arm', 'history', 'a', 'b')}} for c in cards],
              open(f'{R}/group_cards_map_{TAG}.json', 'w'), indent=1)
    out['cards_distinct'] = len(uniq)
json.dump(out, open(f'{R}/group_scores_{TAG}.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'surfaced'}, indent=1))
