"""PLAN v18 step 1 scoring: thesis labels (Haiku, Sonnet) by card kind, and case-level whole-history results where an early-anchored
pair counts if its partner is a key passage or a returned later-work paragraph both labellers call "yes".
Writes paper/results/thesis_label_scores.json. Run: python3 evals/conflicts/gen/score_thesis_labels.py <repo root>"""
import json, sys, re, contextlib, io
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
cmap = json.load(open(f'{R}/thesis_cards_map.json'))
lab = {}
for who, f in (('haiku', 'label__thesis'), ('sonnet', 'label__thesis_s')):
    t = open(f'{R}/haiku_raw/{f}.r1.txt').read(); lab[who] = {x['card']: x['label'] for x in json.loads(t[t.find('{'):t.rfind('}') + 1])['labels']}
out = {'by_kind': {}, 'agree': sum(lab['haiku'].get(c['card']) == lab['sonnet'].get(c['card']) for c in cmap), 'n': len(cmap), 'missing': [c['card'] for c in cmap if c['card'] not in lab['haiku'] or c['card'] not in lab['sonnet']]}
for c in cmap:
    k = out['by_kind'].setdefault(c['kind'], {'n': 0, 'haiku_yes': 0, 'sonnet_yes': 0, 'both_yes': 0})
    h, s = lab['haiku'].get(c['card']) == 'yes', lab['sonnet'].get(c['card']) == 'yes'
    k['n'] += 1; k['haiku_yes'] += h; k['sonnet_yes'] += s; k['both_yes'] += h and s
ok = {(c['case'], c['later']) for c in cmap if c['kind'] == 'returned' and lab['haiku'].get(c['card']) == 'yes' and lab['sonnet'].get(c['card']) == 'yes'}
out['returned_confirmed'] = sorted(f'{a}/{b}' for a, b in ok)
case = {}
for arm, f in (('naive', 'requests_v14.jsonl'), ('realX', 'requests_v15.jsonl'), ('production', 'requests_v17.jsonl')):
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        c = r['case']; key, wide = [], []
        for run in (1, 2, 3):
            try: t = open(f"{R}/haiku_raw/{r['id'].replace(':', '__').replace('/', '_')}.r{run}.txt").read(); g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except FileNotFoundError: continue
            except Exception: g = {}
            ps = S.pairs(r, g); e = f'{c}_early'
            key.append(any(frozenset((e, f'{c}_{x}')) in ps for x in ('announced', 'unannounced')))
            wide.append(key[-1] or any(e in p and (c, next(iter(p - {e}))) in ok for p in ps))
        case.setdefault(arm, {})[c] = {'key': key, 'wide': wide}
out['case_level'] = {arm: {'n': len(v), 'key_majority': sum(sum(x['key']) * 2 > len(x['key']) for x in v.values()),
                           'wide_majority': sum(sum(x['wide']) * 2 > len(x['wide']) for x in v.values()),
                           'wide_any': sum(any(x['wide']) for x in v.values()), 'cases': v} for arm, v in case.items()}
json.dump(out, open(f'{R}/thesis_label_scores.json', 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('by_kind', 'agree', 'n', 'missing', 'returned_confirmed')}, indent=0))
for arm, v in out['case_level'].items(): print(arm, {k: v[k] for k in ('n', 'key_majority', 'wide_majority', 'wide_any')})
