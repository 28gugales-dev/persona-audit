"""PLAN v40 long histories: each history of realtext_histories{suf}.json grown to up to 120 filler posts per work.
The first 60 per work are rebuilt with make_real.py's exact random draws (same ids, text and dates, so earlier pair labels still
apply); extra posts come from the rest of the pool with a second seed (20261115:long:<case>) and are numbered from 60 up.
Kept only when the grown history has more than 160 posts (well past Persona's 124-post whole-history gate).
Run: python3 -I evals/conflicts/gen/make_longhist.py <repo root>  -> paper/data/realtext_histories{suf}L.json"""
import json, random, sys
ROOT = sys.argv[1]
import re, calendar, datetime
# helpers copied from make_real.py
norm = lambda s: re.sub(r'\s+', ' ', s).strip()

def span(path, start, end):
    lines = open(path, encoding='utf-8', errors='replace').read().split('\n')[start - 1:(end - 1) if end else None]
    t = '\n'.join(lines)
    return t[:t.find('*** END OF')] if '*** END OF' in t else t

def paras(text, keys):
    out = []
    for p in re.split(r'\n\s*\n', text):
        p = norm(p)
        letters = [ch for ch in p if ch.isalpha()]
        if len(p) < 200 or not letters or sum(ch.isupper() for ch in letters) > 0.5 * len(letters): continue
        if any(norm(k)[:60] in p for k in keys): continue
        out.append(p)
    return out

def ts(year, month):
    return int(calendar.timegm(datetime.datetime(year, month, 15, 12).timetuple()))

PER, MIN = 120, 160
total = 0
for suf in ('', '2', '3', '4', '5', '6'):
    cases = json.load(open(f'{ROOT}/paper/data/realtext_cases{suf}.json'))
    old = {h['case']: h for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{suf}.json'))}
    hist = []
    for c in cases:
        if c['id'] not in old: continue
        later = c.get('announced') or c.get('unannounced')
        keys = [c[k]['text'] for k in ('early', 'announced', 'unannounced', 'control') if c.get(k)]
        early_t, later_t = span(*c['b_spans']['early']), span(*c['b_spans']['later'])
        rng, rng2 = random.Random(f"20261114:{c['id']}"), random.Random(f"20261115:long:{c['id']}")
        posts = []
        for tag, text, year in (('e', early_t, c['early']['written']), ('l', later_t, later['written'])):
            pool = paras(text, keys)
            first = rng.sample(pool, min(60, len(pool)))
            for n, p in enumerate(first):
                posts.append({'id': f"{c['id']}_{tag}{n}", 'body': p, 'createdUtc': ts(year, rng.randint(1, 12)), 'role': 'filler'})
            rest = [p for p in pool if p not in first]
            for n, p in enumerate(rng2.sample(rest, min(PER - len(first), len(rest)))):
                posts.append({'id': f"{c['id']}_{tag}{60 + n}", 'body': p, 'createdUtc': ts(year, rng2.randint(1, 12)), 'role': 'filler'})
        for k, month in (('early', 3), ('control', 6), ('announced', 3), ('unannounced', 6)):
            if c.get(k): posts.append({'id': f"{c['id']}_{k}", 'body': norm(c[k]['text']), 'createdUtc': ts(c[k]['written'], month), 'role': k})
        same = {p['id']: p for p in posts}
        assert all(same.get(p['id']) == p for p in old[c['id']]['posts']), c['id']  # the short history is an exact subset
        if len(posts) > MIN: hist.append({'case': c['id'], 'posts': posts})
    json.dump(hist, open(f'{ROOT}/paper/data/realtext_histories{suf}L.json', 'w'), indent=0)
    total += len(hist); print(repr(suf), [(h['case'], len(h['posts'])) for h in hist])
print(total, 'long histories')
