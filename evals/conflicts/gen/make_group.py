"""Model-based grouping (PLAN v12): a candidate replacement for the word-overlap theme sort.
Two passes, so it scales past one context window:
  label: each excerpt (the product's 400-character excerpt, >= 60 chars) gets the one question it takes a position on,
         in batches of 30 in date order;
  merge: when a history spans more than one batch, its distinct questions are grouped into same-question groups in one call;
         a one-batch history skips it and identical questions form the groups.
A theme is every excerpt whose question falls in one merged group; 'none' excerpts join no theme.
Stages (run in order, each after the previous stage's model replies are in):
  python3 evals/conflicts/gen/make_group.py <root> label <version> <set>     -> requests + haiku_in
  python3 evals/conflicts/gen/make_group.py <root> merge <version> <set>     -> requests + haiku_in
  python3 evals/conflicts/gen/make_group.py <root> themes <version> <set>    -> paper/results/group_themes_<version>_<set>.json + metrics
<set>: dev (t00-t11), test (t12-t23), real (the six v11 real-text histories) or real2 (the held-out set, PLAN v13)."""
import json, os, re, sys
ROOT, STAGE, V, SET = sys.argv[1:5]
R = f'{ROOT}/paper/results'
BATCH = 30
PROMPTS = json.load(open(f'{ROOT}/evals/conflicts/gen/group_prompts.json'))[V]
safe = lambda i: i.replace(':', '__').replace('/', '_')
norm = lambda s: re.sub(r'\s+', ' ', s).strip()

def histories():
    if SET.startswith('real'):
        f = 'realtext_histories.json' if SET == 'real' else f'realtext_histories{SET[4:]}.json'
        return [{'history': h['case'], 'posts': h['posts']} for h in json.load(open(f'{ROOT}/paper/data/{f}'))]
    lo, hi = (0, 11) if SET == 'dev' else (12, 23)
    return [h for h in json.load(open(f'{ROOT}/paper/data/histories.json')) if h['set'] == 'test' and lo <= int(h['history'][1:]) <= hi]

def excerpts(h):
    ps = sorted(h['posts'], key=lambda p: (p['createdUtc'], p['id']))
    out = [(p['id'], norm(p['body'])[:400]) for p in ps]
    return [(i, t) for i, t in out if len(t) >= 60]

def reply(rid):
    f = f'{R}/haiku_raw/{safe(rid)}.r1.txt'
    if not os.path.exists(f): return None
    t = open(f).read()
    try: return json.loads(t[t.find('{'):t.rfind('}') + 1])
    except Exception: return {}

def write(reqs, name):
    with open(f'{R}/{name}', 'w') as fh:
        for r in reqs:
            fh.write(json.dumps(r) + '\n')
            open(f'{R}/haiku_in/{safe(r["id"])}.txt', 'w').write(f"=== SYSTEM PROMPT ===\n{r['system']}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
    print(len(reqs), 'requests ->', name)

def batches(h):
    ex = excerpts(h)
    return [ex[i:i + BATCH] for i in range(0, len(ex), BATCH)]

def labels(h):
    out = {}
    for n, b in enumerate(batches(h)):
        got = reply(f'grp:{V}:label:{h["history"]}:{n}') or {}
        for x in got.get('labels', []):
            try: out[b[int(str(x['id']).lstrip('E')) - 1][0]] = norm(str(x['question']))
            except Exception: pass
    return out

if STAGE == 'label':
    reqs = []
    for h in histories():
        for n, b in enumerate(batches(h)):
            prompt = '\n'.join(f'<excerpt id="E{i + 1}">\n{t}\n</excerpt>' for i, (_, t) in enumerate(b))
            reqs.append({'id': f'grp:{V}:label:{h["history"]}:{n}', 'history': h['history'], 'system': PROMPTS['label'], 'prompt': prompt})
    write(reqs, f'requests_group_label_{V}_{SET}.jsonl')

elif STAGE == 'merge':
    reqs = []
    for h in histories():
        if len(batches(h)) < 2: continue
        qs = sorted({q for q in labels(h).values() if q.lower().strip('. ') != 'none'})
        prompt = '\n'.join(f'Q{i + 1}: {q}' for i, q in enumerate(qs))
        reqs.append({'id': f'grp:{V}:merge:{h["history"]}', 'history': h['history'], 'questions': qs, 'system': PROMPTS['merge'], 'prompt': prompt})
    write(reqs, f'requests_group_merge_{V}_{SET}.jsonl')

elif STAGE == 'themes':
    mf = f'{R}/requests_group_merge_{V}_{SET}.jsonl'
    merges = {json.loads(l)['history']: json.loads(l) for l in open(mf)} if os.path.exists(mf) else {}
    themes, cover = {}, {}
    for h in histories():
        lab = labels(h)
        qs = sorted({q for q in lab.values() if q.lower().strip('. ') != 'none'})
        m = merges.get(h['history'], {'id': None, 'questions': qs})
        got = (reply(m['id']) or {}) if m['id'] else {'groups': [{'name': q, 'members': [f'Q{i + 1}']} for i, q in enumerate(qs)]}
        qgroup = {}
        for g, grp in enumerate(got.get('groups', [])):
            for q in grp.get('members', []):
                try: qgroup.setdefault(m['questions'][int(str(q).lstrip('Q')) - 1], g)
                except Exception: pass
        groups = {}
        for pid, q in lab.items():
            if q in qgroup: groups.setdefault(qgroup[q], []).append(pid)
        names = {g: norm(str(grp.get('name', f'group {g}')))[:80] for g, grp in enumerate(got.get('groups', []))}
        themes[h['history']] = [{'term': names[g], 'itemIds': ids} for g, ids in sorted(groups.items()) if len(ids) >= 2]
        cover[h['history']] = (len({i for t in themes[h['history']] for i in t['itemIds']}), len(h['posts']))
    json.dump(themes, open(f'{R}/group_themes_{V}_{SET}.json', 'w'), indent=0)
    # metrics: do the pairs that matter land in one theme?
    together = lambda hid, a, b: any(a in t['itemIds'] and b in t['itemIds'] for t in themes.get(hid, []))
    if SET.startswith('real'):
        rows = [(h['history'], f'{h["history"]}_early', f'{h["history"]}_{k}') for h in histories() for k in ('announced', 'unannounced')
                if any(p['id'] == f'{h["history"]}_{k}' for p in h['posts'])]
        print('real pairs together', sum(together(*r) for r in rows), '/', len(rows), [r[2].split('_')[-1] + ':' + r[0][:6] for r in rows if together(*r)])
    else:
        key = [k for k in json.load(open(f'{ROOT}/paper/data/answer_key.json')) if k['history'] in themes]
        pos = [k for k in key if k['conflict']]; dec = [k for k in key if not k['conflict']]
        print('positives together', sum(together(k['history'], k['a'], k['b']) for k in pos), '/', len(pos),
              '| decoys together', sum(together(k['history'], k['a'], k['b']) for k in dec), '/', len(dec))
    print('coverage', sum(c for c, _ in cover.values()), '/', sum(n for _, n in cover.values()),
          '| themes per history', round(sum(len(t) for t in themes.values()) / max(1, len(themes)), 1),
          '| largest theme', max((len(t['itemIds']) for ts in themes.values() for t in ts), default=0))
