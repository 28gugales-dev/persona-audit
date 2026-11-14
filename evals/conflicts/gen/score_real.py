"""Score PLAN v11 (real text). Writes paper/results/real_scores.json and, for B3, paper/results/real_cards_blind.json
(pair texts only, shuffled, arm hidden) plus real_cards_map.json (card id -> arm, case, excerpt ids).
Run: python3 evals/conflicts/gen/score_real.py <repo root> [suffix]  (suffix 2: the PLAN v13 held-out set, Test A only, 2 runs)"""
import json, os, sys, random, hashlib, contextlib, io
from collections import defaultdict
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
R = f'{sys.argv[1]}/paper/results'
SUF = sys.argv[2] if len(sys.argv) > 2 else ''
RUNS = (1, 2) if SUF else (1, 2, 3)
reqs = [json.loads(l) for l in open(f'{R}/requests_real{SUF}.jsonl')]
if SUF: reqs = [r for r in reqs if r['kind'] == 'realA']  # v13: Test B runs through the model grouping instead
safe = lambda i: i.replace(':', '__').replace('/', '_')

def raw_run(rid, run):
    f = f'{R}/haiku_raw/{safe(rid)}.r{run}.txt'
    if not os.path.exists(f): return None
    t = open(f).read()
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

out = {'missing': []}
# Test A: hit = the case's two excerpts flagged as a pair
A = defaultdict(lambda: defaultdict(list))  # (arm, pair) -> case -> [hit per run]
for r in reqs:
    if r['kind'] != 'realA': continue
    a, b = (e['id'] for e in r['body']['excerpts'])
    for run in RUNS:
        got = raw_run(r['id'], run)
        if got is None: out['missing'].append(f"{r['id']}.r{run}"); continue
        A[(r['prompt_version'], r['pair'])][r['case']].append(frozenset((a, b)) in S.pairs(r, got))
out['A'] = {f'{arm}/{pair}': {'k': sum(sum(v) for v in cs.values()), 'n': sum(len(v) for v in cs.values()),
                              'per_case': {c: sum(v) for c, v in sorted(cs.items())},
                              'cases_majority': sum(sum(v) * 2 > len(v) for v in cs.values()), 'cases': len(cs)}
            for (arm, pair), cs in sorted(A.items())}
for k, v in out['A'].items(): v['wilson'] = S.wilson(v['k'], v['n'])

# Test B: same theme, reached the model (after the window), surfaced end to end, and every card
themes = json.load(open(f'{R}/real{SUF}_themes.json'))
flags = defaultdict(set); cards = []
for r in reqs:
    if r['kind'] != 'realB': continue
    got = raw_run(r['id'], 1)
    if got is None: out['missing'].append(f"{r['id']}.r1"); continue
    ps = S.pairs(r, got); flags[(r['prompt_version'], r['case'])] |= ps
    text = {e['id']: e for e in r['body']['excerpts']}
    for p in ps:
        x, y = sorted(p, key=lambda i: text[i]['when'])
        cards.append({'arm': r['prompt_version'], 'case': r['case'], 'a': x, 'b': y, 'a_text': text[x]['text'], 'a_when': text[x]['when'], 'b_text': text[y]['text'], 'b_when': text[y]['when']})
B = {}
for case, groups in themes.items():
    row = {}
    for later in ('announced', 'unannounced'):
        e, l = f'{case}_early', f'{case}_{later}'
        if not any(l in g['itemIds'] for g in groups): continue
        sent = any(r['kind'] == 'realB' and r['case'] == case and r['prompt_version'] == 'prod' and {e, l} <= {x['id'] for x in r['body']['excerpts']} for r in reqs)
        row[later] = {'same_theme': any(e in g['itemIds'] and l in g['itemIds'] for g in groups), 'sent': sent,
                      **{arm: frozenset((e, l)) in flags[(arm, case)] for arm in ('prod', 'defNoEmpty', 'genX')}}
    row['themes'] = len(groups)
    row['cards'] = {arm: len(flags[(arm, case)]) for arm in ('prod', 'defNoEmpty', 'genX') if not SUF}
    B[case] = row
out['B'] = B
# one blind row per distinct pair (arms that flagged the same pair share a label)
uniq = {}
for c in cards: uniq.setdefault((c['case'], c['a'], c['b']), c)
blind = [{'card': hashlib.sha1(f'{k}'.encode()).hexdigest()[:8], 'earlier': {'written': v['a_when'], 'text': v['a_text']}, 'later': {'written': v['b_when'], 'text': v['b_text']}} for k, v in uniq.items()]
random.Random(20261114).shuffle(blind)
if not SUF: json.dump(blind, open(f'{R}/real_cards_blind.json', 'w'), indent=1)
if not SUF: json.dump([{'card': hashlib.sha1(f'{(c["case"], c["a"], c["b"])}'.encode()).hexdigest()[:8], 'arm': c['arm'], 'case': c['case'], 'a': c['a'], 'b': c['b']} for c in cards],
          open(f'{R}/real_cards_map.json', 'w'), indent=1)
out['cards_total'] = {arm: sum(c['arm'] == arm for c in cards) for arm in ('prod', 'defNoEmpty', 'genX')}
out['cards_distinct'] = len(uniq)
lab = f'{R}/real_cards_labels.json'
if os.path.exists(lab) and not SUF:
    L = {x['card']: x['label'] for x in json.load(open(lab))}
    mp = json.load(open(f'{R}/real_cards_map.json'))
    out['cards_real'] = {arm: sum(L.get(m['card']) == 'real' for m in mp if m['arm'] == arm) for arm in ('prod', 'defNoEmpty', 'genX')}
json.dump(out, open(f'{R}/real{SUF}_scores.json', 'w'), indent=1)
print('missing', len(out['missing']))
for k, v in out['A'].items(): print('A', k, v['k'], '/', v['n'], 'cases majority', v['cases_majority'], '/', v['cases'])
for k, v in B.items(): print('B', k, v)
print('cards', out['cards_total'], 'distinct', out['cards_distinct'], out.get('cards_real'))
