"""Score the Stage 6 mechanism reruns (requests_mech.jsonl) and the history-cluster bootstrap of the headline contrast.
Writes paper/results/mech_scores.json. Hit rules as in score_rerun.py.
Run: python3 evals/conflicts/gen/score_mech.py <repo root>"""
import json, sys, random
from collections import defaultdict
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
import contextlib, io  # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S  # re-scores the Stage 4 runs (deterministic) and gives us its helpers
raw, pairs, item_hit, mcnemar, wilson, key, rr_out = S.raw, S.pairs, S.item_hit, S.mcnemar, S.wilson, S.key, S.out

ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
reqs = [json.loads(l) for f in ('requests_mech.jsonl', 'requests_mech2.jsonl', 'requests_mech3.jsonl', 'requests_mech4.jsonl') for l in open(f'{R}/{f}')]
cells = defaultdict(lambda: {'k': 0, 'n': 0}); per = defaultdict(dict); missing = 0
for r in reqs:
    got = raw(r['id'].replace(':', '__'))
    if got is None: missing += 1; continue
    ps = pairs(r, got); pv = r['prompt_version']
    if r['kind'] == 'rev':
        c = r['case']; k = f"rev/{r['arm']}/{pv}"
        hit = frozenset((f'{c}_earlier', f'{c}_later')) in ps
        cells[k]['ctl'] = cells[k].get('ctl', 0) + any(f'{c}_ctl' in p for p in ps)
        cells[k]['hard'] = cells[k].get('hard', 0) + (frozenset((f'{c}_hard', f'{c}_later')) in ps)
        per[k][c] = hit
    else:
        it = key[r['item']]; hit = item_hit(it, ps)
        grp = 'P3' if it['label'] == 'P3' else ('DECOY' if it['label'].startswith('D') else 'P124')
        k = f"{r['kind']}/{grp}/{pv}"; per[k][r['item']] = hit
    cells[k]['k'] += hit; cells[k]['n'] += 1
out = {'missing_replies': missing, 'cells': {k: {**v, 'wilson': wilson(v['k'], v['n'])} for k, v in sorted(cells.items())}}

# paired: neutral prefix vs change marker, same items, production prompt
mp = rr_out['marker_positives']['per_item']
neu = per['neutralpos/P124/prod']
both = [i for i in neu if i in mp and 'prod' in mp[i]]
b = sum(neu[i] and not mp[i]['prod'] for i in both); c = sum(mp[i]['prod'] and not neu[i] for i in both)
out['neutral_vs_marker'] = {'n': len(both), 'neutral': sum(neu[i] for i in both), 'marker': sum(mp[i]['prod'] for i in both),
                            'neutral_only': b, 'marker_only': c, 'mcnemar_p': mcnemar(b, c)}

# history-cluster bootstrap of unmarked minus marked recall (production), and the held-out (t12-t23) subset alone
items = [i for i in mp if mp[i].get('unmarked_prod') is not None and 'prod' in mp[i]]
byh = defaultdict(list)
for i in items: byh[key[i]['history']].append(i)
hs = sorted(byh); rnd = random.Random(20261114); diffs = []
for _ in range(10000):
    s = [i for h in (rnd.choice(hs) for _ in hs) for i in byh[h]]
    diffs.append(sum(mp[i]['unmarked_prod'] - mp[i]['prod'] for i in s) / len(s))
diffs.sort()
held = [i for i in items if int(key[i]['history'][1:]) >= 12]
hb = sum(mp[i]['unmarked_prod'] and not mp[i]['prod'] for i in held); hc = sum(mp[i]['prod'] and not mp[i]['unmarked_prod'] for i in held)
out['headline_cluster'] = {'histories': len(hs), 'items': len(items), 'diff': sum(mp[i]['unmarked_prod'] - mp[i]['prod'] for i in items) / len(items),
                           'ci95': [diffs[249], diffs[9749]], 'share_of_resamples_le_0': sum(d <= 0 for d in diffs) / len(diffs)}
out['headline_heldout_only'] = {'n': len(held), 'unmarked': sum(mp[i]['unmarked_prod'] for i in held), 'marked_prod': sum(mp[i]['prod'] for i in held),
                                'marked_fixed': sum(mp[i].get('fixed', False) for i in held), 'lost': hb, 'gained': hc, 'mcnemar_p': mcnemar(hb, hc)}
# held-out pipeline end to end, production vs fixed, paired on the same 20 positives
flags = defaultdict(lambda: defaultdict(set))
for r in S.reqs:
    if r['kind'] != 'pipeline_heldout': continue
    got = raw(r['id'].replace(':', '__').replace('/', '_'))
    if got is not None: flags[r['prompt_version']][r['history']] |= pairs(r, got)
pos = [it for it in key.values() if it['set'] == 'test' and it['conflict'] and int(it['history'][1:]) >= 12]
hp = {pv: {it['item']: item_hit(it, flags[pv][it['history']]) for it in pos} for pv in ('prod', 'fixed')}
fb = sum(hp['fixed'][i] and not hp['prod'][i] for i in hp['prod']); fc = sum(hp['prod'][i] and not hp['fixed'][i] for i in hp['prod'])
out['pipeline_heldout_fix_paired'] = {'n': len(pos), 'prod': sum(hp['prod'].values()), 'fixed': sum(hp['fixed'].values()), 'fixed_only': fb, 'prod_only': fc, 'mcnemar_p': mcnemar(fb, fc)}
# every ablation vs production on the same 36 marked planted items and 10 marked reversals (paired, exact)
rev_prod = {}
for r in (json.loads(l) for l in open(f'{R}/requests_rev.jsonl')):
    if r['kind'] == 'reversal' and r['prompt_version'] == 'prod' and r['arm'] == 'marker':
        rev_prod[r['case']] = frozenset((f"{r['case']}_earlier", f"{r['case']}_later")) in pairs(r, raw(r['id'].replace(':', '__')))
paired = {}
for pv in ('noDNC', 'noDoubt', 'noEmpty', 'defOnly', 'defNoEmpty'):
    a = per.get(f'markerpos/P124/{pv}', {}); g = [i for i in a if i in mp]
    pb = sum(a[i] and not mp[i]['prod'] for i in g); pc = sum(mp[i]['prod'] and not a[i] for i in g)
    ra = per.get(f'rev/marker/{pv}', {}); rg = [c for c in ra if c in rev_prod]
    rb = sum(ra[c] and not rev_prod[c] for c in rg); rc = sum(rev_prod[c] and not ra[c] for c in rg)
    paired[pv] = {'planted': {'n': len(g), 'gained': pb, 'lost': pc, 'p': mcnemar(pb, pc)}, 'reversals': {'n': len(rg), 'gained': rb, 'lost': rc, 'p': mcnemar(rb, rc)}}
out['ablation_vs_prod'] = paired

# pooled marked reversals (4 phrasings x 10 cases, production): case-level bootstrap instead of a pooled Wilson interval
case_hits = defaultdict(list)
for c, h in rev_prod.items(): case_hits[c].append(h)
for r in S.reqs:
    if r['kind'] == 'phrasing' and r['prompt_version'] == 'prod':
        got = raw(r['id'].replace(':', '__'))
        if got is not None: case_hits[r['case']].append(frozenset((f"{r['case']}_earlier", f"{r['case']}_later")) in pairs(r, got))
cs = sorted(case_hits); rb_ = []
for _ in range(10000):
    s = [case_hits[c] for c in (rnd.choice(cs) for _ in cs)]
    rb_.append(sum(map(sum, s)) / sum(map(len, s)))
rb_.sort()
out['reversals_marked_case_bootstrap'] = {'k': sum(map(sum, case_hits.values())), 'n': sum(map(len, case_hits.values())), 'ci95': [rb_[249], rb_[9749]],
                                         'per_case': {c: sum(v) for c, v in case_hits.items()}}

# harness check: same production requests, different wrapper and effort "medium" (run 3)
def raw3(safe):
    import os
    f = f'{R}/haiku_raw/{safe}.r3.txt'
    if not os.path.exists(f): return None
    x = open(f).read()
    try: return json.loads(x[x.find('{'):x.rfind('}') + 1])
    except Exception: return {}
mk_req = {r['item']: r for r in S.reqs if r['kind'] == 'markerpos' and r['prompt_version'] == 'prod'}
hm = {}; hu = {}
for i in mp:
    g = raw3(f'prod__mk__{i}')
    if g is not None: hm[i] = item_hit(key[i], pairs(mk_req[i], g))
    o = S.oracle[i]; g = raw3(f"{o['history']}__oracle__{i}")
    if g is not None: hu[i] = item_hit(key[i], pairs(o, g))
hg = [i for i in hm if i in hu]
out['harness_check'] = {'n': len(hg), 'unmarked': sum(hu[i] for i in hg), 'marked': sum(hm[i] for i in hg),
                        'lost': sum(hu[i] and not hm[i] for i in hg), 'gained': sum(hm[i] and not hu[i] for i in hg),
                        'mcnemar_p': mcnemar(sum(hu[i] and not hm[i] for i in hg), sum(hm[i] and not hu[i] for i in hg)),
                        'agree_with_run1_marked': sum(hm[i] == mp[i]['prod'] for i in hg)}
# generic prompts: unmarked vs marked on the same 36 items
gen = {}
for pv in ('genA', 'genB', 'genC'):
    u = per.get(f'genplain/P124/{pv}', {}); m = per.get(f'genmarked/P124/{pv}', {}); g = [i for i in u if i in m]
    gb = sum(u[i] and not m[i] for i in g); gc = sum(m[i] and not u[i] for i in g)
    gen[pv] = {'n': len(g), 'unmarked': sum(u[i] for i in g), 'marked': sum(m[i] for i in g), 'lost': gb, 'gained': gc, 'p': mcnemar(gb, gc)}
out['generic_prompts'] = gen
# Holm correction over the five exploratory prompt-variant tests on planted items (the two marker contrasts are the confirmatory ones)
ps = sorted((v['planted']['p'], k) for k, v in paired.items())
adj, run = {}, 0
for j, (pv_, k) in enumerate(ps):
    run = max(run, min(1, (len(ps) - j) * pv_)); adj[k] = run
out['ablation_holm_planted'] = adj
# which decoy types the generic prompts flag (pooled over the three prompts)
gd = defaultdict(lambda: [0, 0])
for r in reqs:
    if r['kind'] != 'gendecoy': continue
    it = key[r['item']]; h = item_hit(it, pairs(r, raw(r['id'].replace(':', '__'))))
    gd[it['label']][0] += h; gd[it['label']][1] += 1
out['generic_decoys_by_type'] = {k: {'flagged': v[0], 'n': v[1]} for k, v in sorted(gd.items())}
json.dump(out, open(f'{R}/mech_scores.json', 'w'), indent=1)
print('missing', missing)
for k, v in out['cells'].items(): print(k, v['k'], '/', v['n'], {x: v[x] for x in ('ctl', 'hard') if x in v})
print('neutral vs marker', out['neutral_vs_marker']); print('cluster', out['headline_cluster']); print('held-out only', out['headline_heldout_only']); print('pipeline fix paired', out['pipeline_heldout_fix_paired']); print('ablation vs prod', out['ablation_vs_prod']); print('rev case boot', {k: v for k, v in out['reversals_marked_case_bootstrap'].items() if k != 'per_case'}); print('harness', out['harness_check']); print('generic', out['generic_prompts']); print('holm', out['ablation_holm_planted'])
