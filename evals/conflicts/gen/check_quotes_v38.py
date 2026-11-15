"""v38: share of returned quotes that appear verbatim (whitespace-normalised, case-sensitive) in the later excerpt of their pair, as Haiku saw it.
Run: python3 evals/conflicts/gen/check_quotes_v38.py <repo root>  (writes paper/results/v38_quotes.json)"""
import json, sys, re, os
R = f'{sys.argv[1]}/paper/results'; norm = lambda s: re.sub(r'\s+', ' ', s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')).strip()
out = {}
for f, runs in (('requests_v38_quote.jsonl', (1, 2, 3)), ('requests_v36_v38w.jsonl', (1,))):
    n = ok = missing = 0
    for l in open(f'{R}/{f}'):
        r = json.loads(l); ex = r['body']['excerpts']
        for run in runs:
            p = f"{R}/haiku_raw/{r['id'].replace(':', '__')}.r{run}.txt"
            if not os.path.exists(p): continue
            t = open(p).read()
            try: g = json.loads(t[t.find('{'):t.rfind('}') + 1])
            except Exception: continue
            for x in g.get('conflicts', []):
                try: a, b = sorted((int(x['a'][1:]) - 1, int(x['b'][1:]) - 1))
                except Exception: continue
                if not (0 <= a < len(ex) and 0 <= b < len(ex)): continue
                q = norm(x.get('quote', '')); n += 1
                if not q: missing += 1
                elif q.strip('.…" ') in norm(ex[b]['text']) or q in norm(ex[b]['text']): ok += 1
    out[f] = {'pairs': n, 'verbatim_in_later': ok, 'no_quote': missing, 'share': round(ok / max(n, 1), 2)}
json.dump(out, open(f'{R}/v38_quotes.json', 'w'), indent=1); print(out)
