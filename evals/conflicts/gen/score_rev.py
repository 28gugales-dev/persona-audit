"""Q1 (reversals) and the held-out prompt-fix comparison. Writes paper/results/reversals_scores.json.

Reversal hit: the model flags (earlier, later). False flags: any pair with the same-era control, or (hard control, later).
Held-out: production vs fixed prompt on the oracle requests of t12-t23 and the direct hand-written items,
scored per item exactly as score.py does (B joined to A or a filler of the same item)."""
import json, sys, os, math
from collections import defaultdict
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
cases = json.load(open(f'{ROOT}/paper/data/reversals.json'))

def reply(safe):
    f = f'{R}/haiku_raw/{safe}.r1.txt'
    if not os.path.exists(f): return None
    t = open(f).read()
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - s) / d, (c + s) / d)

out = {'reversals': {}, 'probe': {}, 'heldout': {}}
for pv in ('prod', 'fixed'):
    for arm in ('plain', 'marker'):
        hits = ctl = hard = 0; per = {}
        for c in cases:
            r = reply(f'rev__{pv}__{arm}__{c["id"]}')
            if r is None: continue
            ex = ['earlier'] + (['ctl'] if c['same_era_control'] else []) + (['hard'] if c['hard_control'] else []) + ['later']
            alias = {f'E{i + 1}': e for i, e in enumerate(ex)}
            pairs = {frozenset((alias.get(x['a']), alias.get(x['b']))) for x in r.get('conflicts', [])}
            h = frozenset(('earlier', 'later')) in pairs
            fc = any('ctl' in p for p in pairs); fh = frozenset(('hard', 'later')) in pairs
            hits += h; ctl += fc; hard += fh
            per[c['id']] = {'hit': h, 'ctl_flag': fc, 'hard_flag': fh, 'pairs': [sorted(p - {None}) for p in pairs]}
        n = len(per)
        out['reversals'][f'{pv}/{arm}'] = {'n': n, 'hits': hits, 'recall': hits / n if n else None, 'wilson': wilson(hits, n),
                                           'ctl_flags': ctl, 'n_ctl': sum(1 for c in cases if c['same_era_control'] and c['id'] in per),
                                           'hard_flags': hard, 'n_hard': sum(1 for c in cases if c['hard_control'] and c['id'] in per), 'per_case': per}
for c in cases:
    f = f'{R}/haiku_raw/probe__{c["id"]}.r1.txt'
    if os.path.exists(f):
        t = open(f).read(); surname = c['philosopher'].split()[-1].lower()
        out['probe'][c['id']] = {'reply': t.strip()[:200], 'recognised': surname in t.lower()}

# held-out prompt fix
key = {it['item']: it for it in json.load(open(f'{ROOT}/paper/data/answer_key.json'))}
hist = {h['history']: h for h in json.load(open(f'{ROOT}/paper/data/histories.json'))}
reqs = {json.loads(l)['id']: json.loads(l) for l in open(f'{R}/requests.jsonl')}
def item_hit(req, r):
    it = key[req['item']]
    part = {p['id'] for p in hist[it['history']]['posts'] if p['item'] == it['item'] and p['role'] in ('a', 'filler')}
    ids = [e['id'] for e in req['body']['excerpts']]
    for x in r.get('conflicts', []):
        try: a, b = ids[int(x['a'][1:]) - 1], ids[int(x['b'][1:]) - 1]
        except Exception: continue
        pr = {a, b}
        if it['b'] in pr and (pr - {it['b']}) & part: return True
    return False
rows = defaultdict(lambda: defaultdict(list))
for rid, req in reqs.items():
    if not ((req['kind'] == 'oracle' and req['set'] == 'test' and int(req['history'][1:]) >= 12) or req['kind'] == 'direct'): continue
    safe = rid.replace(':', '__')
    for pv, s in (('prod', safe), ('fixed', 'fixed__' + safe)):
        r = reply(s)
        if r is None: continue
        it = key[req['item']]
        rows[pv][f"{it['set']}/{it['label']}"].append(item_hit(req, r))
for pv in rows:
    out['heldout'][pv] = {k: {'n': len(v), 'k': sum(v), 'rate': sum(v) / len(v)} for k, v in sorted(rows[pv].items())}
json.dump(out, open(f'{R}/reversals_scores.json', 'w'), indent=1, default=list)
for k, v in out['reversals'].items():
    print(k, f"hits {v['hits']}/{v['n']}", 'wilson', [round(x, 2) for x in v['wilson']], f"ctl {v['ctl_flags']}/{v['n_ctl']}", f"hard {v['hard_flags']}/{v['n_hard']}")
print('probe recognised', sum(v['recognised'] for v in out['probe'].values()), '/', len(out['probe']))
for pv, d in out['heldout'].items():
    print('==', pv)
    for k, v in d.items(): print(f'  {k:18s} {v["k"]}/{v["n"]}')
