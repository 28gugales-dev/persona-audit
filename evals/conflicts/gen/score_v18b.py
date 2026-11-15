"""PLAN v18b scoring: case-level, cross-era. A run finds a case when it returns a key pair (early + announced/unannounced) or any pair
with one side from the early work and one from the later work that both thesis labellers (Haiku, Sonnet) called "yes" in any label
round (thesis_cards_map{,3,x,x3,x4}.json). Reported per arm for single runs and for disjoint merged looks of two runs, by set.
Writes paper/results/v18b_scores.json. Run: python3 evals/conflicts/gen/score_v18b.py <repo root>"""
import json, sys, re, os, contextlib, io
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
yes, labelled = set(), set()
for m, base in (('', 'label__thesis'), ('3', 'label__thesis3'), ('x', 'label__thesisx'), ('x3', 'label__thesisx3'), ('x4', 'label__thesisx4'), ('x5', 'label__thesisx5'), ('x6', 'label__thesisx6'), ('x7', 'label__thesisx7'), ('x8', 'label__thesisx8'), ('x9', 'label__thesisx9'), ('x10', 'label__thesisx10'), ('x11', 'label__thesisx11')):
    if not os.path.exists(f'{R}/thesis_cards_map{m}.json') or not os.path.exists(f'{R}/haiku_raw/{base}.r1.txt'): continue
    L = []
    for f in (base, base + '_s'):
        t = open(f'{R}/haiku_raw/{f}.r1.txt').read(); L.append({x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']})
    for c in json.load(open(f'{R}/thesis_cards_map{m}.json')):
        k = (c['case'], c.get('early', f"{c['case']}_early"), c['later']); labelled.add(k)
        if all(l.get(c['card']) == 'yes' for l in L): yes.add(k)
side = lambda c, x: 'E' if x == f'{c}_early' or re.fullmatch(f'{c}_e\\d+', x) else 'L' if re.fullmatch(f'{c}_(announced|unannounced|l\\d+)', x) else None
ARMS = [('production', 'requests_v17.jsonl'), ('naive', 'requests_v14.jsonl'), ('realX', 'requests_v15.jsonl'), ('changes', 'requests_v18.jsonl'), ('changes', 'requests_v18b_chg3.jsonl'),
        ('production', 'requests_v18_3_prod.jsonl'), ('realX', 'requests_v18_3_realX.jsonl'), ('realX_long', 'requests_v18b_long.jsonl'), ('changes_long', 'requests_v18b_chglong.jsonl'),
        ('production', 'requests_v18c_prod.jsonl'), ('final_realX', 'requests_v18c_realX.jsonl'), ('final_changes', 'requests_v18c_changes.jsonl'),
        ('naive', 'requests_v19_fresh2_naive.jsonl'), ('realX', 'requests_v19_fresh2_realX.jsonl'), ('changes', 'requests_v19_fresh2_changes.jsonl'),
        ('contradoc_style', 'requests_v19_contradoc.jsonl'), ('beliefshift_style', 'requests_v19_beliefshift.jsonl'),
        ('production', 'requests_v21_prod.jsonl'), ('naive', 'requests_v21_naive.jsonl'), ('realX', 'requests_v21_realX.jsonl'), ('changes', 'requests_v21_changes.jsonl'),
        ('beliefshift_style', 'requests_v21_beliefshift.jsonl'), ('final_realX', 'requests_v21_dep_realX.jsonl'), ('final_changes', 'requests_v21_dep_changes.jsonl'),
        ('defOnly', 'requests_v22_defonly.jsonl'), ('defNoEmpty', 'requests_v22_defnoempty.jsonl'),
        ('gs1', 'requests_v23_gs1.jsonl'), ('gs2', 'requests_v23_gs2.jsonl'), ('gs3', 'requests_v23_gs3.jsonl'),
        ('prodPara', 'requests_v24_prodpara.jsonl'), ('defNoEmptyPara', 'requests_v24_defnoemptypara.jsonl'), ('genX', 'requests_v24_genx.jsonl'), ('ships', 'requests_v24_ships.jsonl')]
SETS = {'': 'dev', '2': 'dev', '3': 'fresh1', '4': 'fresh2', '5': 'fresh3'}
setof = {c['id']: SETS[s] for s in SETS if os.path.exists(f'{ROOT}/paper/data/realtext_cases{s}.json') for c in json.load(open(f'{ROOT}/paper/data/realtext_cases{s}.json'))}
out, unl = {}, set()
for arm, f in ARMS:
    if not os.path.exists(f'{R}/{f}'): continue
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        c = r['case']; hits, ctl, npairs = [], [], []
        for run in range(1, 7):
            p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
            if not os.path.exists(p): continue
            t = open(p).read()
            try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: g = {}
            ps = S.pairs(r, g); h = False
            for q in ps:
                a, b = sorted(q, key=lambda x: side(c, x) or 'Z')
                if side(c, a) != 'E' or side(c, b) != 'L': continue
                if a == f'{c}_early' and b in (f'{c}_announced', f'{c}_unannounced'): h = True
                elif (c, a, b) in yes: h = True
                elif (c, a, b) not in labelled: unl.add(f'{arm}|{c}|{a}|{b}')
            hits.append(h); ctl.append(any(f'{c}_control' in q for q in ps)); npairs.append(len(ps))
        out.setdefault(arm, {})[c] = {'set': setof[c], 'hits': hits, 'controls': ctl, 'pairs': npairs}
for A, B, M in (('realX_long', 'changes_long', 'realX+changes_long'), ('final_realX', 'final_changes', 'final')):  # one look = A run i + B run i
    if A in out and B in out:
        out[M] = {c: {**x, 'hits': [], 'controls': [], 'pairs': [], 'mixed': [a or b for a, b in zip(x['hits'], out[B][c]['hits'])],
            'mctl': [a or b for a, b in zip(x['controls'], out[B][c]['controls'])]} for c, x in out[A].items() if c in out[B]}
summary = {}
for arm, cs in out.items():
    if arm in ('realX+changes_long', 'final'):
        for s in ('dev', 'fresh1', 'fresh2', 'fresh3'):
            v = {c: x for c, x in cs.items() if x['set'] == s}
            if v: summary[f'{arm}/{s}'] = {'n': len(v), 'looks': min(len(x['mixed']) for x in v.values()), 'merged_majority': sum(sum(x['mixed']) * 2 > len(x['mixed']) for x in v.values()),
                                           'merged_mean': round(sum(sum(x['mixed']) / max(len(x['mixed']), 1) for x in v.values()), 2), 'controls_per_look': round(sum(sum(x['mctl']) for x in v.values()) / max(min(len(x['mctl']) for x in v.values()), 1), 2),
                                           'merged_missed': [c for c, x in v.items() if sum(x['mixed']) * 2 <= len(x['mixed'])]}
        continue
    for s in ('dev', 'fresh1', 'fresh2', 'fresh3'):
        v = {c: x for c, x in cs.items() if x['set'] == s}
        if not v: continue
        n_runs = min(len(x['hits']) for x in v.values())
        row = {'n': len(v), 'runs': n_runs,
               'single_majority': sum(sum(x['hits']) * 2 > len(x['hits']) for x in v.values()),
               'single_any': sum(any(x['hits']) for x in v.values()),
               'single_mean': round(sum(sum(x['hits']) / len(x['hits']) for x in v.values() if x['hits']), 2),
               'controls_per_run': round(sum(sum(x['controls']) for x in v.values()) / max(n_runs, 1), 2),
               'pairs_per_history_run': round(sum(sum(x['pairs']) for x in v.values()) / max(n_runs, 1) / len(v), 1),
               'missed_majority': [c for c, x in v.items() if sum(x['hits']) * 2 <= len(x['hits'])]}
        if n_runs >= 2:
            looks = {c: [x['hits'][i] or x['hits'][i + 1] for i in range(0, len(x['hits']) - 1, 2)] for c, x in v.items()}
            row['merged_looks'] = len(next(iter(looks.values())))
            row['merged_majority'] = sum(sum(h) * 2 > len(h) for h in looks.values())
            row['merged_mean'] = round(sum(sum(h) / len(h) for h in looks.values()), 2)
            row['merged_missed'] = [c for c, h in looks.items() if sum(h) * 2 <= len(h)]
            row['merged_controls_per_look'] = round(sum(sum(x['controls'][i] or x['controls'][i + 1] for i in range(0, 2 * row['merged_looks'], 2)) for x in v.values()) / row['merged_looks'], 2)
        summary[f'{arm}/{s}'] = row
json.dump({'summary': summary, 'cases': out, 'unlabelled': sorted(unl)}, open(f'{R}/v18b_scores.json', 'w'), indent=1)
for k, v in summary.items(): print(k, {x: y for x, y in v.items()})
print('unlabelled cross-era pairs:', len(unl))
