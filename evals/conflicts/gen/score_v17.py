"""Score PLAN v17: production prompt on whole histories (3 runs), announced vs unannounced split for every whole-history arm,
a history-cluster bootstrap, the closed-book probe, and TF-IDF partner ranks. Writes paper/results/v17_scores.json.
Run: uv run --with scikit-learn python evals/conflicts/gen/score_v17.py <repo root>"""
import json, sys, random, contextlib, io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
sys.path.insert(0, f'{sys.argv[1]}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'; D = f'{ROOT}/paper/data'
held = {c['id'] for c in json.load(open(f'{D}/realtext_cases2.json'))}

def raw(rid, run):
    try: t = open(f"{R}/haiku_raw/{rid.replace(':', '__')}.r{run}.txt").read()
    except FileNotFoundError: return None
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

hits, out = {}, {'missing': []}  # (arm, case, later) -> [hit per run]
for arm, f in (('naive', 'requests_v14.jsonl'), ('realX', 'requests_v15.jsonl'), ('production', 'requests_v17.jsonl')):
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] != 'realN': continue
        ids = {e['id'] for e in r['body']['excerpts']}
        for run in (1, 2, 3):
            g = raw(r['id'], run)
            if g is None: out['missing'].append(f"{r['id']}.r{run}"); continue
            ps = S.pairs(r, g)
            for later in ('announced', 'unannounced'):
                if f"{r['case']}_{later}" in ids: hits.setdefault((arm, r['case'], later), []).append(frozenset((f"{r['case']}_early", f"{r['case']}_{later}")) in ps)
maj = {k: sum(v) * 2 > len(v) for k, v in hits.items()}
arms = ('production', 'naive', 'realX')
out['majority'] = {arm: {sub: {'k': sum(maj[k] for k in maj if k[0] == arm and (sub == 'all' or k[2] == sub or (sub == 'held' and k[1] in held))),
                               'n': sum(1 for k in maj if k[0] == arm and (sub == 'all' or k[2] == sub or (sub == 'held' and k[1] in held)))}
                         for sub in ('all', 'announced', 'unannounced', 'held')} for arm in arms}
# history-cluster bootstrap of mean pairs found per run (shipped = 0 everywhere)
cases = sorted({k[1] for k in hits})
per = {arm: {c: sum(sum(v) / len(v) for k, v in hits.items() if k[0] == arm and k[1] == c) for c in cases} for arm in arms}
rng = random.Random(20261114); boot = {'realX-naive': [], 'realX-shipped': [], 'naive-shipped': [], 'production-shipped': [], 'realX-production': []}
for _ in range(10000):
    smp = [rng.choice(cases) for _ in cases]; s = {arm: sum(per[arm][c] for c in smp) for arm in arms}
    boot['realX-naive'].append(s['realX'] - s['naive']); boot['realX-shipped'].append(s['realX']); boot['naive-shipped'].append(s['naive'])
    boot['production-shipped'].append(s['production']); boot['realX-production'].append(s['realX'] - s['production'])
ci = lambda xs: [round(sorted(xs)[249], 2), round(sorted(xs)[9749], 2)]
out['cluster_bootstrap_pairs_per_run'] = {k: {'mean': round(sum(v) / len(v), 2), 'ci95': ci(v)} for k, v in boot.items()}
# closed-book probe
items = json.load(open(f'{R}/closedbook_items.json')); g = raw('closedbook:real', 1)
out['closed_book'] = {cid: a for cid, a in zip(items, (g or {}).get('answers', []))}
# TF-IDF cosine rank of the true later partner among all posts in the history
ranks = {}
for f in ('realtext_histories.json', 'realtext_histories2.json'):
    for h in json.load(open(f'{D}/{f}')):
        posts = h['posts']; idx = {p['id']: i for i, p in enumerate(posts)}; e = f"{h['case']}_early"
        if e not in idx: continue
        sims = cosine_similarity(TfidfVectorizer(stop_words='english').fit_transform([p['body'] for p in posts]))[idx[e]]
        order = sorted((i for i in range(len(posts)) if i != idx[e]), key=lambda i: -sims[i])
        for later in ('announced', 'unannounced'):
            l = f"{h['case']}_{later}"
            if l in idx: ranks[f"{h['case']}/{later}"] = {'rank': order.index(idx[l]) + 1, 'of': len(posts) - 1, 'cosine': round(float(sims[idx[l]]), 3)}
out['tfidf_partner_rank'] = ranks
rs = sorted(v['rank'] for v in ranks.values())
out['tfidf_summary'] = {'pairs': len(rs), 'median_rank': rs[len(rs) // 2], 'top5': sum(r <= 5 for r in rs), 'top20': sum(r <= 20 for r in rs)}
json.dump(out, open(f'{R}/v17_scores.json', 'w'), indent=1)
print('missing', len(out['missing'])); print(json.dumps(out['majority'])); print(json.dumps(out['cluster_bootstrap_pairs_per_run'])); print(out['tfidf_summary'])
