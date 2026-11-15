"""v34: per history, runs returning the canary pair, runs returning a pair joining a canary post to a real post, and documented-change credit
(as score_v18b.py: key pair or a both-yes labelled cross-era pair). Run: python3 evals/conflicts/gen/score_v34.py <repo root>  (writes paper/results/v34_scores.json)"""
import json, sys, os, contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    import score_v18b as V
out = {}
for l in open(f'{V.R}/requests_v34_canary.jsonl'):
    r = json.loads(l); c = r['case']; can, mix, hit, unl = [], [], [], 0
    A, B = f'{c}_canary_a', f'{c}_canary_b'
    for run in (1, 2, 3):
        t = open(f"{V.R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt").read()
        try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
        except Exception: g = {}
        ps = V.S.pairs(r, g); h = False
        can.append(frozenset((A, B)) in ps); mix.append(any(len(q & {A, B}) == 1 for q in ps))
        for q in ps:
            if q & {A, B}: continue
            a, b = sorted(q, key=lambda x: V.side(c, x) or 'Z')
            if V.side(c, a) != 'E' or V.side(c, b) != 'L': continue
            if (a == f'{c}_early' and b in (f'{c}_announced', f'{c}_unannounced')) or (c, a, b) in V.yes: h = True
            elif (c, a, b) not in V.labelled: unl += 1
        hit.append(h)
    out[c] = {'set': V.setof[c], 'canary': can, 'mixed': mix, 'hits': hit, 'unlabelled': unl}
maj = lambda x: sum(x) * 2 > len(x)
s = {'canary_majority': sum(maj(x['canary']) for x in out.values()), 'canary_any': sum(any(x['canary']) for x in out.values()),
     'documented_majority': sum(maj(x['hits']) for x in out.values()), 'mixed_per_run': round(sum(sum(x['mixed']) for x in out.values()) / 3, 2),
     'canary_missed': [c for c, x in out.items() if not maj(x['canary'])], 'found': [c for c, x in out.items() if maj(x['hits'])], 'unlabelled': sum(x['unlabelled'] for x in out.values())}
json.dump({'summary': s, 'cases': out}, open(f'{V.R}/v34_scores.json', 'w'), indent=1); print(s)
