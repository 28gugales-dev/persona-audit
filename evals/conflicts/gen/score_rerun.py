"""Score the Stage 4 reruns (requests_rerun.jsonl). Writes paper/results/rerun_scores.json.
markerpos: paired with the unmarked oracle runs of the same items (haiku_raw/<history>__oracle__<item>.r1.txt).
phrasing: per phrasing, reversal hit = (earlier, later) flagged; controls as in score_rev.py.
adv2: hit = (a, b) flagged. pipeline_heldout: per test item, B joined to A or a filler, as score.py."""
import json, sys, os, math, random
from collections import defaultdict
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
reqs = [json.loads(l) for l in open(f'{R}/requests_rerun.jsonl')]
key = {it['item']: it for it in json.load(open(f'{ROOT}/paper/data/answer_key.json'))}
hist = {h['history']: h for h in json.load(open(f'{ROOT}/paper/data/histories.json'))}
oracle = {json.loads(l)['item']: json.loads(l) for l in open(f'{R}/requests.jsonl') if json.loads(l)['kind'] == 'oracle'}

def raw(safe):
    f = f'{R}/haiku_raw/{safe}.r1.txt'
    if not os.path.exists(f): return None
    t = open(f).read()
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

def pairs(req, r):
    ids = [e['id'] for e in req['body']['excerpts']]; out = set()
    for x in (r or {}).get('conflicts', []):
        try: out.add(frozenset((ids[int(x['a'][1:]) - 1], ids[int(x['b'][1:]) - 1])))
        except Exception: pass
    return out

def item_hit(it, ps):
    part = {p['id'] for p in hist[it['history']]['posts'] if p['item'] == it['item'] and p['role'] in ('a', 'filler')}
    return any(it['b'] in p and (p - {it['b']}) & part for p in ps)

def mcnemar(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)

def wilson(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [(c - s) / d, (c + s) / d]

out = {}
# 1. marker on unsignalled positives
mk = defaultdict(dict)
for r in reqs:
    if r['kind'] != 'markerpos': continue
    got = raw(r['id'].replace(':', '__'))
    if got is None: continue
    mk[r['item']][r['prompt_version']] = item_hit(key[r['item']], pairs(r, got))
for item in mk:
    base = raw(f"{oracle[item]['history']}__oracle__{item}")
    mk[item]['unmarked_prod'] = item_hit(key[item], pairs(oracle[item], base)) if base is not None else None
both = [i for i in mk if mk[i].get('unmarked_prod') is not None and 'prod' in mk[i]]
b = sum(mk[i]['unmarked_prod'] and not mk[i]['prod'] for i in both); c = sum(mk[i]['prod'] and not mk[i]['unmarked_prod'] for i in both)
fx = [i for i in both if 'fixed' in mk[i]]
out['marker_positives'] = {
    'n': len(both), 'unmarked_prod': sum(mk[i]['unmarked_prod'] for i in both), 'marked_prod': sum(mk[i]['prod'] for i in both),
    'marked_fixed': sum(mk[i]['fixed'] for i in fx), 'n_fixed': len(fx),
    'discordant_lost': b, 'discordant_gained': c, 'mcnemar_p': mcnemar(b, c),
    'by_label': {lab: {'n': len(v), 'unmarked': sum(mk[i]['unmarked_prod'] for i in v), 'marked_prod': sum(mk[i]['prod'] for i in v), 'marked_fixed': sum(mk[i].get('fixed', False) for i in v)}
                 for lab in ('P1', 'P2', 'P4') for v in [[i for i in both if key[i]['label'] == lab]]},
    'per_item': mk}
# 2. phrasings
cases = {c['id']: c for c in json.load(open(f'{ROOT}/paper/data/reversals.json'))}
ph = defaultdict(lambda: {'hits': 0, 'n': 0, 'ctl': 0, 'hard': 0})
for r in reqs:
    if r['kind'] != 'phrasing': continue
    got = raw(r['id'].replace(':', '__'))
    if got is None: continue
    ps = pairs(r, got); cid = r['case']; k = f"{r['prompt_version']}/ph{r['phrasing']}"
    ph[k]['n'] += 1
    ph[k]['hits'] += frozenset((f'{cid}_earlier', f'{cid}_later')) in ps
    ph[k]['ctl'] += any(f'{cid}_ctl' in p for p in ps)
    ph[k]['hard'] += frozenset((f'{cid}_hard', f'{cid}_later')) in ps
out['phrasings'] = {k: {**v, 'wilson': wilson(v['hits'], v['n'])} for k, v in sorted(ph.items())}
# 3. second hand-written set
a2 = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for r in reqs:
    if r['kind'] != 'adv2': continue
    got = raw(r['id'].replace(':', '__'))
    if got is None: continue
    hit = frozenset((f"{r['item']}_a", f"{r['item']}_b")) in pairs(r, got)
    a2[r['prompt_version']][r['type']][0] += hit; a2[r['prompt_version']][r['type']][1] += 1
out['adversarial2'] = {pv: {t: {'flagged': v[0], 'n': v[1]} for t, v in d.items()} for pv, d in a2.items()}
# 4. held-out pipeline, end to end
flags = defaultdict(lambda: defaultdict(set)); cov = defaultdict(set); nflags = defaultdict(int)
for r in reqs:
    if r['kind'] != 'pipeline_heldout': continue
    got = raw(r['id'].replace(':', '__').replace('/', '_'))
    if got is None: continue
    ps = pairs(r, got); flags[r['prompt_version']][r['history']] |= ps; cov[r['prompt_version']].add(r['history']); nflags[r['prompt_version']] += len(ps)
pipe = {}
for pv in flags:
    rows = defaultdict(lambda: [0, 0])
    for it in key.values():
        if it['set'] != 'test' or it['history'] not in cov[pv]: continue
        h = item_hit(it, flags[pv][it['history']])
        lab = it['label']; rows[lab][0] += h; rows[lab][1] += 1
        agg = 'POS' if it['conflict'] else 'DECOY'; rows[agg][0] += h; rows[agg][1] += 1
    pipe[pv] = {'histories': len(cov[pv]), 'flags_per_history': nflags[pv] / max(1, len(cov[pv])), **{k: {'k': v[0], 'n': v[1]} for k, v in sorted(rows.items())}}
out['pipeline_heldout'] = pipe
json.dump(out, open(f'{R}/rerun_scores.json', 'w'), indent=1, default=list)
m = out['marker_positives']
print('marker on unsignalled positives: unmarked', m['unmarked_prod'], '/', m['n'], '| marked prod', m['marked_prod'], '| marked fixed', m['marked_fixed'], '/', m['n_fixed'], '| lost', m['discordant_lost'], 'gained', m['discordant_gained'], 'p', round(m['mcnemar_p'], 6))
print('by label', m['by_label'])
for k, v in out['phrasings'].items(): print('phrasing', k, v['hits'], '/', v['n'], 'ctl', v['ctl'], 'hard', v['hard'])
for pv, d in out['adversarial2'].items(): print('adv2', pv, dict(d))
for pv, d in pipe.items(): print('pipeline held-out', pv, d)
