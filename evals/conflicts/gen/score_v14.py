"""Score PLAN v14: whole-history baseline on the 12 real histories, the author probe, and case-level real-text rates.
Writes paper/results/v14_scores.json. Run: python3 evals/conflicts/gen/score_v14.py <repo root>"""
import json, sys, contextlib, io
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'
reqs = [json.loads(l) for l in open(f'{R}/requests_v14.jsonl')]
out = {'naive': {}, 'probe': {}}
for r in reqs:
    if r['kind'] != 'realN': continue
    g = S.raw(r['id'].replace(':', '__')); ps = S.pairs(r, g); ids = {e['id'] for e in r['body']['excerpts']}
    row = {'pairs_returned': len(ps)}
    for later in ('announced', 'unannounced'):
        e, l = f"{r['case']}_early", f"{r['case']}_{later}"
        if l in ids: row[later] = frozenset((e, l)) in ps
    out['naive'][r['case']] = row
probe = next(r for r in reqs if r['kind'] == 'probe')
t = open(f'{R}/haiku_raw/probe__author__real.r1.txt').read()
ans = {a['id']: a for a in json.loads(t[t.find('{'):t.rfind('}') + 1])['answers']}
surname = {'hume': 'hume', 'peirce': 'peirce', 'nietzsche': 'nietzsche', 'kant': 'kant', 'mill': 'mill', 'russell': 'russell', 'wittgenstein': 'wittgenstein',
           'darwin': 'darwin', 'newman': 'newman', 'spencer': 'spencer', 'huxley': 'huxley'}
for i, key in enumerate(probe['items']):
    a = ans.get(f'P{i + 1}', {}); who = str(a.get('author', '')).lower()
    out['probe'][key] = {'author': a.get('author'), 'work': a.get('work'), 'correct': surname[key.split('_')[0]] in who}
pairs = [v[k] for v in out['naive'].values() for k in ('announced', 'unannounced') if k in v]
out['naive_summary'] = {'surfaced': sum(pairs), 'pairs': len(pairs), 'pairs_returned_per_history': sum(v['pairs_returned'] for v in out['naive'].values()) / len(out['naive'])}
out['probe_summary'] = {'correct': sum(v['correct'] for v in out['probe'].values()), 'n': len(out['probe'])}
# case-level real-text rates (Test A): a case counts if found on a majority of runs / on any run
case = {}
for tag, runs in (('', (1, 2, 3)), ('2', (1, 2, 3))):
    for l in open(f'{R}/requests_real{tag}.jsonl'):
        r = json.loads(l)
        if r['kind'] != 'realA': continue
        a, b = (e['id'] for e in r['body']['excerpts']); hits = []
        for run in runs:
            g = S.raw(r['id'].replace(':', '__').replace('/', '_')) if run == 1 else None
            f = f"{R}/haiku_raw/{r['id'].replace(':', '__').replace('/', '_')}.r{run}.txt"
            try:
                tt = open(f).read(); g = json.loads(tt[tt.find('{'):tt.rfind('}') + 1])
            except FileNotFoundError: continue
            except Exception: g = {}
            hits.append(frozenset((a, b)) in S.pairs(r, g))
        case[f"{'held' if tag else 'dev'}/{r['prompt_version']}/{r['pair']}/{r['case']}"] = hits
agg = {}
for k, h in case.items():
    s, pv, pair, _ = k.split('/'); a = agg.setdefault(f'{s}/{pv}/{pair}', {'tries': [0, 0], 'majority': [0, 0], 'any': [0, 0]})
    a['tries'][0] += sum(h); a['tries'][1] += len(h); a['majority'][0] += sum(h) * 2 > len(h); a['majority'][1] += 1; a['any'][0] += any(h); a['any'][1] += 1
out['case_level'] = agg
# blind labels for the whole-history baseline's cards (same label prompt as real_cards_labels_*)
held = {c['id'] for c in json.load(open(f'{sys.argv[1]}/paper/data/realtext_cases2.json'))}
cmap = {x['card']: x['case'] for x in json.load(open(f'{R}/naive_cards_map.json'))}
lab = {}
for f, who in (('label__naivecards', 'haiku'), ('label__naivecards_s', 'sonnet')):
    tt = open(f'{R}/haiku_raw/{f}.r1.txt').read(); lab[who] = {x['card']: x['label'] for x in json.loads(tt[tt.find('{'):tt.rfind('}') + 1])['labels']}
out['naive_cards'] = {who: {'real': sum(L[c] == 'real' for c in cmap), 'n': len(cmap),
                            'held_real': sum(L[c] == 'real' for c in cmap if cmap[c] in held), 'held_n': sum(cmap[c] in held for c in cmap)} for who, L in lab.items()}
out['naive_cards']['agree'] = sum(lab['haiku'][c] == lab['sonnet'][c] for c in cmap)
json.dump(out, open(f'{R}/v14_scores.json', 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('naive_summary', 'probe_summary')}))
for k, v in out['naive'].items(): print('naive', k, v)
for k, v in sorted(agg.items()): print(k, v)
print([ (k, v['author']) for k, v in out['probe'].items() if not v['correct']])
