"""Score every detector against the answer key. Writes paper/results/scores.json and prints tables.

An item is FLAGGED by a detector when it flags a pair joining the item's post B with post A or one of the
item's fillers (fillers assert the same view as A). For a positive that is a hit; for a decoy a false flag.
Flags joining posts of different items are counted as stray flags per history.
95% CIs: percentile bootstrap over histories (1,000 resamples, seed 20261116)."""
import json, random, re, sys, os
from collections import defaultdict
ROOT = sys.argv[1]
R = f'{ROOT}/paper/results'
key = json.load(open(f'{ROOT}/paper/data/answer_key.json'))
hist = {h['history']: h for h in json.load(open(f'{ROOT}/paper/data/histories.json'))}
themes = json.load(open(f'{R}/themes.json'))
reqs = [json.loads(l) for l in open(f'{R}/requests.jsonl')]
item_of = {p['id']: p['item'] for h in hist.values() for p in h['posts']}

def partners(it):
    h = hist[it['history']]
    return {p['id'] for p in h['posts'] if p['item'] == it['item'] and p['role'] in ('a', 'filler')}

# ---- detectors: history -> set of frozenset pairs
def local_flags():
    loc = json.load(open(f'{R}/local.json'))
    return {h: {frozenset((c['a'], c['b'])) for c in cs} for h, cs in loc.items()}

def model_flags(name, kind):
    path = f'{R}/parsed/{name}.json'
    if not os.path.exists(path): return None, set()
    by_id = {r['id']: r for r in reqs}
    flags, seen_reqs = defaultdict(set), set()
    for row in json.load(open(path)):
        r = by_id.get(row['id'])
        if not r or r['kind'] != kind or row.get('run', 1) != 1: continue
        seen_reqs.add(r['history'])
        for c in row['conflicts']: flags[r['history']].add(frozenset((c['a'], c['b'])))
    return flags, seen_reqs

STOP = set('the a an and or but of to in on at for with from by as is are was were be been it its this that i me my we you they he she not no never do does did have has had so if then than just really only also about into what which who how would could should will can may might must there their them our your'.split())
NEG = re.compile(r"\b(not|no|never|isn't|aren't|doesn't|don't|didn't|can't|cannot|won't|nothing|none)\b|n't\b", re.I)
def words(t): return {w for w in re.findall(r"[a-z']+", t.lower()) if len(w) > 2 and w not in STOP}
def overlap_flags(tau=0.15):
    out = {}
    for h, hh in hist.items():
        ps = hh['posts']; fl = set()
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                a, b = ps[i], ps[j]
                wa, wb = words(a['body']), words(b['body'])
                if not wa or not wb: continue
                if len(wa & wb) / len(wa | wb) >= tau and bool(NEG.search(a['body'])) != bool(NEG.search(b['body'])):
                    fl.add(frozenset((a['id'], b['id'])))
        out[h] = fl
    return out

def item_hits(flags, restrict_reqs=None):
    hits = {}
    for it in key:
        f = flags.get(it['history'], set())
        b = it['b']
        hits[it['item']] = any(b in pair and (pair - {b}) & partners(it) for pair in f)
    return hits

def stray(flags):
    out = {}
    for h, f in flags.items():
        out[h] = sum(1 for pair in f if len({item_of.get(x) for x in pair}) > 1 or None in {item_of.get(x) for x in pair})
    return out

rng = random.Random(20261116)
def boot(rows, stat, n=1000):
    """rows: list of (history, value...) grouped by history; stat: fn(list rows) -> float"""
    by = defaultdict(list)
    for r in rows: by[r[0]].append(r)
    hs = list(by)
    if not hs: return None, None, None
    point = stat(rows)
    vals = []
    for _ in range(n):
        sample = [r for h in (rng.choice(hs) for _ in hs) for r in by[h]]
        v = stat(sample)
        if v is not None: vals.append(v)
    vals.sort()
    return point, vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]

def rate(rows):
    return sum(r[1] for r in rows) / len(rows) if rows else None

def table(name, hits, covered, sets=('test', 'adversarial', 'dev')):
    res = {}
    for s in sets:
        items = [it for it in key if it['set'] == s and it['history'] in covered]
        by_label = defaultdict(list)
        for it in items: by_label[it['label']].append((it['history'], hits[it['item']]))
        for lab, rows in sorted(by_label.items()):
            res[f'{s}/{lab}'] = (len(rows),) + boot(rows, rate)
        pos = [(it['history'], hits[it['item']]) for it in items if it['conflict']]
        neg = [(it['history'], hits[it['item']]) for it in items if not it['conflict']]
        res[f'{s}/ALL_POS_recall'] = (len(pos),) + boot(pos, rate)
        res[f'{s}/ALL_DECOY_flag'] = (len(neg),) + boot(neg, rate)
    return res

def staged():
    """P(theme together), P(both in the 20-excerpt window | together)."""
    out = []
    window = defaultdict(set)
    for r in reqs:
        if r['kind'] == 'pipeline':
            window[r['history']].add(frozenset(e['id'] for e in r['body']['excerpts']))
    for it in key:
        together = any(it['a'] in g['itemIds'] and it['b'] in g['itemIds'] for g in themes[it['history']])
        inwin = any(it['a'] in w and it['b'] in w for w in window[it['history']])
        out.append({'item': it['item'], 'set': it['set'], 'label': it['label'], 'conflict': it['conflict'], 'together': together, 'window': inwin})
    return out

if __name__ == '__main__':
    results = {}
    dets = {'local': (local_flags(), set(hist)), 'overlap': (overlap_flags(), set(hist))}
    for name in [f[:-5] for f in os.listdir(f'{R}/parsed') if f.endswith('.json')] if os.path.isdir(f'{R}/parsed') else []:
        for kind in ('pipeline', 'oracle', 'direct'):
            fl, seen = model_flags(name, kind)
            if fl is not None and seen: dets[f'{name}/{kind}'] = (fl, seen)
    nm_path = f'{R}/naive_map.json'
    if os.path.exists(nm_path):
        nm = json.load(open(nm_path)); fl = defaultdict(set); cov = set()
        for h, m in nm.items():
            f = f'{R}/haiku_raw/{h}__naive.r1.txt'
            if not os.path.exists(f): continue
            t = open(f).read(); cov.add(h)
            try: pairs = json.loads(t[t.find('{'):t.rfind('}') + 1])['pairs']
            except Exception: pairs = []
            for pr in pairs:
                if len(pr) == 2 and pr[0] in m and pr[1] in m: fl[h].add(frozenset((m[pr[0]], m[pr[1]])))
        if cov: dets['haiku/naive_whole_history'] = (fl, cov)
    for name, (fl, covered) in dets.items():
        hits = item_hits(fl)
        results[name] = {'items': table(name, hits, covered), 'covered': sorted(covered), 'stray_per_history': sum(stray(fl).values()) / max(1, len(covered))}
        results[name]['hits'] = hits
    results['staged'] = staged()
    json.dump(results, open(f'{R}/scores.json', 'w'), indent=0, default=list)
    for name in dets:
        print('\n==', name, 'stray/history', round(results[name]['stray_per_history'], 2))
        for k, (n, p, lo, hi) in results[name]['items'].items():
            if p is not None: print(f'  {k:28s} n={n:3d} {p:.2f} [{lo:.2f},{hi:.2f}]')
