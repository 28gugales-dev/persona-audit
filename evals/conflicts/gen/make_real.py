"""PLAN v11 Test B histories: per case, up to 60 paragraphs sampled from the early work and 60 from the later work (>= 200 chars,
seed 20261114:<case>), each dated in its work's year, plus the case's own passages. Writes paper/data/realtext_histories.json.
Each work is the line span in `b_spans` ([file, first line, end line or None], 1-indexed), set so editors' introductions,
other authors' articles and licence text are left out. Cases without spans (Mill: the abridgement mixes in the editor's text) are skipped.
Run: python3 -I evals/conflicts/gen/make_real.py <repo root> [suffix]  (suffix 2: realtext_cases2.json -> realtext_histories2.json)"""
import json, random, re, sys, calendar, datetime
ROOT = sys.argv[1]
SUF = sys.argv[2] if len(sys.argv) > 2 else ''
cases = json.load(open(f'{ROOT}/paper/data/realtext_cases{SUF}.json'))
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

hist = []
for c in cases:
    later = c.get('announced') or c.get('unannounced')
    if not later or not c.get('b_spans') or not all(c['b_spans'].get(k) for k in ('early', 'later')): continue
    keys = [c[k]['text'] for k in ('early', 'announced', 'unannounced', 'control') if c.get(k)]
    early_t, later_t = span(*c['b_spans']['early']), span(*c['b_spans']['later'])
    rng = random.Random(f"20261114:{c['id']}")
    posts = []
    for tag, text, year in (('e', early_t, c['early']['written']), ('l', later_t, later['written'])):
        pool = paras(text, keys)
        assert len(pool) >= 8, (c['id'], tag, len(pool))
        for n, p in enumerate(rng.sample(pool, min(60, len(pool)))):
            posts.append({'id': f"{c['id']}_{tag}{n}", 'body': p, 'createdUtc': ts(year, rng.randint(1, 12)), 'role': 'filler'})
    for k, month in (('early', 3), ('control', 6), ('announced', 3), ('unannounced', 6)):
        if c.get(k): posts.append({'id': f"{c['id']}_{k}", 'body': norm(c[k]['text']), 'createdUtc': ts(c[k]['written'], month), 'role': k})
    assert all(len(p['id']) <= 80 for p in posts)
    hist.append({'case': c['id'], 'posts': posts})
json.dump(hist, open(f'{ROOT}/paper/data/realtext_histories{SUF}.json', 'w'), indent=0)
print(len(hist), 'histories', [(h['case'], sum(p['id'].split('_')[-1][0] == 'e' and p['role'] == 'filler' for p in h['posts']), sum(p['id'].split('_')[-1][0] == 'l' and p['role'] == 'filler' for p in h['posts'])) for h in hist])
