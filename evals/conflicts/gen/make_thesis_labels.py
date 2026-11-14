"""PLAN v18 step 1: blind thesis labels for every early-anchored cross-era pair the whole-history arms returned (naive v14,
realX v15, production v17) that is not in the answer key, mixed with the key pairs (expected yes) and two random early + later-work
paragraphs per case that no arm returned (expected no). Writes haiku_in/label__thesis{,_s}.txt and results/thesis_cards_map.json.
Run: python3 evals/conflicts/gen/make_thesis_labels.py <repo root> [suffix]  (3: fresh held-out, labels label__thesis3*)"""
import json, sys, re, random, hashlib, contextlib, io
ROOT = sys.argv[1]; SUF = sys.argv[2] if len(sys.argv) > 2 else ''; R = f'{ROOT}/paper/results'
sys.path.insert(0, f'{ROOT}/evals/conflicts/gen')
with contextlib.redirect_stdout(io.StringIO()):
    import score_rerun as S
cases = {c['id']: c for f in ('realtext_cases.json', 'realtext_cases2.json', 'realtext_cases3.json') for c in json.load(open(f'{ROOT}/paper/data/{f}'))}
reqs = {}
for f in {'': ('requests_v14.jsonl', 'requests_v15.jsonl', 'requests_v17.jsonl'), '3': ('requests_v18_3_realX.jsonl', 'requests_v18_3_prod.jsonl')}[SUF]:
    for l in open(f'{R}/{f}'):
        r = json.loads(l)
        if r['kind'] == 'realN': reqs.setdefault(r['case'], []).append(r)
seen = {}  # (case, later id) -> kind
for c, rs in reqs.items():
    for r in rs:
        for run in range(1, 7):
            try: t = open(f"{R}/haiku_raw/{r['id'].replace(':', '__').replace('/', '_')}.r{run}.txt").read(); g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: continue
            for p in S.pairs(r, g):
                if f'{c}_early' not in p: continue
                (x,) = p - {f'{c}_early'}
                if re.fullmatch(f'{c}_l\\d+', x): seen[(c, x)] = 'returned'
    ex = {e['id']: e for e in rs[0]['body']['excerpts']}
    for k in ('announced', 'unannounced'):
        if f'{c}_{k}' in ex: seen[(c, f'{c}_{k}')] = 'key'
    rng = random.Random(f'v18:{c}')
    pool = sorted(i for i in ex if re.fullmatch(f'{c}_l\\d+', i) and (c, i) not in seen)
    for i in rng.sample(pool, 2): seen[(c, i)] = 'decoy'
rows = []
for (c, x), kind in seen.items():
    ex = {e['id']: e for e in reqs[c][0]['body']['excerpts']}
    card = hashlib.sha256(f'{c}|{x}'.encode()).hexdigest()[:8]
    rows.append({'card': card, 'case': c, 'later': x, 'kind': kind, 'thesis': cases[c]['thesis'], 'early': ex[f'{c}_early']['text'], 'other': ex[x]['text']})
random.Random('v18-order').shuffle(rows)
SYS = ("You check pairs of passages by one author against a documented change of mind. Each card gives the QUESTION the author changed "
       "his mind on, an EARLIER passage stating his earlier view, and a LATER passage. Answer \"yes\" only if the later passage, speaking for the "
       "author, rejects, abandons, retracts or contradicts the earlier passage's view on that question (stating the new view, or saying the old "
       "one was wrong). Answer \"no\" if the later passage is on another point, merely mentions the topic, describes someone else's view without "
       "taking a side, or is consistent with the earlier view. Judge only from the two passages and the question.\n\n"
       "Return only JSON: {\"labels\": [{\"card\": \"<id>\", \"label\": \"yes\" | \"no\"}]} with one entry per card.")
user = '\n\n'.join(f'<card id="{r["card"]}">\n<question>{r["thesis"]}</question>\n<earlier>\n{r["early"]}\n</earlier>\n<later>\n{r["other"]}\n</later>\n</card>' for r in rows)
for suf in ('', '_s'):
    open(f'{R}/haiku_in/label__thesis{SUF}{suf}.txt', 'w').write(f'=== SYSTEM PROMPT ===\n{SYS}\n\n=== USER MESSAGE ===\n{user}\n')
json.dump([{k: r[k] for k in ('card', 'case', 'later', 'kind')} for r in rows], open(f'{R}/thesis_cards_map{SUF}.json', 'w'), indent=1)
from collections import Counter; print(len(rows), Counter(r['kind'] for r in rows))
