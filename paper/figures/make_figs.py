"""Figures from paper/results only (no hand-entered numbers). Plain SVG, no dependencies.
Run: python3 paper/figures/make_figs.py <repo root>"""
import json, math, sys
ROOT = sys.argv[1]; R = f'{ROOT}/paper/results'; F = f'{ROOT}/paper/figures'
s = json.load(open(f'{R}/scores.json')); rv = json.load(open(f'{R}/reversals_scores.json')); rr = json.load(open(f'{R}/rerun_scores.json'))
win = json.load(open(f'{R}/q3_window_coverage.json')); me = json.load(open(f'{R}/mech_scores.json'))

INK, MUTED, GRID = '#1f2328', '#59636e', '#d0d7de'
C_PLAIN, C_NEU, C_MARK, C_FIX = '#8a8f98', '#cbd5e1', '#c2410c', '#1d4ed8'
FONT = "font-family='Helvetica, Arial, sans-serif'"

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); sd = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - sd) / d, (c + sd) / d

def svg(w, h, body):
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONT}><rect width='{w}' height='{h}' fill='white'/>{body}</svg>"

def text(x, y, t, size=12, anchor='start', fill=INK, weight='normal'):
    return f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' fill='{fill}' font-weight='{weight}'>{t}</text>"

# ---------- Figure 1: the marker effect (headline)
mp = rr['marker_positives']
rev_plain = rv['reversals']['prod/plain']
rev_mark_k = rv['reversals']['prod/marker']['hits'] + sum(rr['phrasings'][f'prod/ph{i}']['hits'] for i in (1, 2, 3))
rev_mark_n = rv['reversals']['prod/marker']['n'] + sum(rr['phrasings'][f'prod/ph{i}']['n'] for i in (1, 2, 3))
rev_fix_k = rv['reversals']['fixed/marker']['hits'] + sum(rr['phrasings'][f'fixed/ph{i}']['hits'] for i in (1, 2, 3))
rev_fix_n = rv['reversals']['fixed/marker']['n'] + sum(rr['phrasings'][f'fixed/ph{i}']['n'] for i in (1, 2, 3))
groups = [
    ('Planted reversals (GPT-written)', 'n = 36 items', [(mp['unmarked_prod'], mp['n']), (me['cells']['neutralpos/P124/prod']['k'], me['cells']['neutralpos/P124/prod']['n']), (mp['marked_prod'], mp['n']), (mp['marked_fixed'], mp['n_fixed'])]),
    ("Philosophers' published reversals", 'n = 10 cases; marked = 4 phrasings', [(rev_plain['hits'], rev_plain['n']), (me['cells']['rev/neutral/prod']['k'], me['cells']['rev/neutral/prod']['n']), (rev_mark_k, rev_mark_n), (rev_fix_k, rev_fix_n)]),
]
W, H = 640, 300; x0, y0, ph = 70, 40, 190
body = ''
for i in range(0, 101, 25):
    y = y0 + ph - ph * i / 100
    body += f"<line x1='{x0}' x2='{W - 20}' y1='{y}' y2='{y}' stroke='{GRID}'/>" + text(x0 - 8, y + 4, f'{i}%', 11, 'end', MUTED)
labels = [('Stated plainly', C_PLAIN), ('+ neutral sentence', C_NEU), ('+ "I’ve changed my mind"', C_MARK), ('+ marker, prompt fix', C_FIX)]
gw = (W - 20 - x0) / len(groups); bw = 40
for g, (name, sub, vals) in enumerate(groups):
    cx = x0 + gw * g + gw / 2
    for j, (k, n) in enumerate(vals):
        p = k / n; lo, hi = wilson(k, n)
        bx = cx + (j - 1.5) * (bw + 8) - bw / 2
        by = y0 + ph - ph * p
        body += f"<rect x='{bx}' y='{by}' width='{bw}' height='{ph * p}' fill='{labels[j][1]}'/>"
        body += f"<line x1='{bx + bw / 2}' x2='{bx + bw / 2}' y1='{y0 + ph - ph * lo}' y2='{y0 + ph - ph * hi}' stroke='{INK}' stroke-width='1.2'/>"
        body += text(bx + bw / 2, by - 6 if p < 0.93 else by + 14, f'{k}/{n}', 11, 'middle', INK if p < 0.93 or labels[j][1] == C_NEU else 'white', 'bold')
    body += text(cx, y0 + ph + 20, name, 12, 'middle', INK, 'bold') + text(cx, y0 + ph + 36, sub, 11, 'middle', MUTED)
lx = x0
for name, col in labels:
    body += f"<rect x='{lx}' y='14' width='12' height='12' fill='{col}'/>" + text(lx + 17, 24, name, 11)
    lx += 17 + 6 * len(name) + 18
body += text(18, y0 + ph / 2, 'Pairs found', 11, 'middle', MUTED).replace('<text', f"<text transform='rotate(-90 18 {y0 + ph / 2})'", 1)
open(f'{F}/fig1_marker.svg', 'w').write(svg(W, H, body))


# ---------- Figure 2: what each prompt buys (marked-reversal recall vs false flags on the 40 held-out decoys)
hp = rv['heldout']; dec = lambda pv: sum(hp[pv][f'test/D{i}']['k'] for i in range(1, 8))
assert sum(hp['prod'][f'test/D{i}']['n'] for i in range(1, 8)) == 40
cl = me['cells']
pts = [('Production', dec('prod'), mp['marked_prod'], C_MARK, 'shipped'),
       ('Production + fix line', dec('fixed'), mp['marked_fixed'], C_FIX, 'fix'),
       ('Rewritten definition, no empty-list line', cl['oracle/DECOY/defNoEmpty']['k'], cl['markerpos/P124/defNoEmpty']['k'], C_FIX, 'fix'),
       ('Rewritten definition', cl['oracle/DECOY/defOnly']['k'], cl['markerpos/P124/defOnly']['k'], '#6b7280', 'abl'),
       ('No empty-list line', cl['oracle/DECOY/noEmpty']['k'], cl['markerpos/P124/noEmpty']['k'], '#6b7280', 'abl'),
       ('No doubt line', cl['oracle/DECOY/noDoubt']['k'], cl['markerpos/P124/noDoubt']['k'], '#6b7280', 'abl'),
       ('No exclusion list', cl['oracle/DECOY/noDNC']['k'], cl['markerpos/P124/noDNC']['k'], '#6b7280', 'abl')]
cf = json.load(open(f'{R}/confirm_scores.json'))['cells']
pts.append(('Generic A + exclusion list', cf['gendecoy/genX']['k'], cf['genmarked/genX']['k'], '#111827', 'gen'))
for g, nm in (('genA', 'Generic A'), ('genB', 'Generic B'), ('genC', 'Generic C')):
    pts.append((nm, cl[f'gendecoy/DECOY/{g}']['k'], cl[f'genmarked/P124/{g}']['k'], '#111827', 'gen'))
m7 = json.load(open(f'{R}/mech7_scores.json'))['cells']
for g, nm in (('gs1', 'GPT strict 1'), ('gs2', 'GPT strict 2'), ('gs3', 'GPT strict 3')):
    pts.append((nm, m7[f'{g}/decoy']['k'], m7[f'{g}/markerpos']['k'], '#0f766e', 'gpt'))
W, H = 660, 330; x0, y0, pw, ph = 60, 20, 300, 260
body = ''
for i in range(0, 101, 25):
    y = y0 + ph - ph * i / 100
    body += f"<line x1='{x0}' x2='{x0 + pw}' y1='{y}' y2='{y}' stroke='{GRID}'/>" + text(x0 - 8, y + 4, f'{i}%', 11, 'end', MUTED)
for i in range(0, 26, 5):
    x = x0 + pw * i / 25
    body += f"<line x1='{x}' x2='{x}' y1='{y0}' y2='{y0 + ph}' stroke='{GRID}'/>" + text(x, y0 + ph + 16, f'{i}%', 11, 'middle', MUTED)
body += text(x0 + pw / 2, y0 + ph + 34, 'Held-out decoys flagged (n = 40)', 12, 'middle', MUTED)
body += text(16, y0 + ph / 2, 'Marked reversals found (n = 36)', 11, 'middle', MUTED).replace('<text', f"<text transform='rotate(-90 16 {y0 + ph / 2})'", 1)
ly = y0 + 6
for name, fx, ry, col, kind in sorted(pts, key=lambda q: (-q[2], -q[1])):
    cx, cy = x0 + pw * (fx / 40) / 0.25, y0 + ph - ph * ry / 36
    shape = (f"<rect x='{cx - 5}' y='{cy - 5}' width='10' height='10' fill='{col}'/>" if kind == 'gen' else
             f"<polygon points='{cx},{cy - 7} {cx - 6},{cy + 5} {cx + 6},{cy + 5}' fill='{col}'/>" if kind == 'gpt' else
             f"<circle cx='{cx}' cy='{cy}' r='6' fill='{col}' stroke='white' stroke-width='1.5'/>")
    body += shape
    body += f"<line x1='{cx}' y1='{cy}' x2='{x0 + pw + 18}' y2='{ly - 4}' stroke='{GRID}' stroke-width='0.8'/>"
    body += text(x0 + pw + 22, ly, f'{name}: {ry}/36, {fx}/40', 11, 'start', col if col != '#6b7280' else INK)
    ly += 21
open(f'{F}/fig2_tradeoff.svg', 'w').write(svg(W, H, body))

# ---------- Figure 3: where the shipped pipeline loses planted conflicts (all 46 test positives)
st = [x for x in s['staged'] if x['set'] == 'test' and x['conflict']]
together = sum(x['together'] for x in st)
orc_lo = s['haiku/oracle']['items']['test/ALL_POS_recall']; orc_k = round(orc_lo[0] * orc_lo[1])
ho = rv['heldout']['prod']; orc_k += sum(ho[f'test/{l}']['k'] for l in ('P1', 'P2', 'P3', 'P4'))
pl = s['haiku/pipeline']['items']['test/ALL_POS_recall']; pipe_k = round(pl[0] * pl[1]) + rr['pipeline_heldout']['prod']['POS']['k']
local_k = round(s['local']['items']['test/ALL_POS_recall'][1] * 46)
overlap_k = round(s['overlap']['items']['test/ALL_POS_recall'][1] * 46)
rows = [('Planted conflicts', 46, '#e5e7eb'), ('Found by the model shown the item alone (oracle)', orc_k, '#6b7280'),
        ('Both posts land in one theme (theme sort)', together, '#9ca3af'), ('Found end to end by the shipped pipeline', pipe_k, C_MARK),
        ('Found by the on-device detector', local_k, '#111827'), ('Word-overlap baseline', overlap_k, '#111827')]
W, H = 640, 250; x0 = 300; bwmax = W - x0 - 100
body = ''
for i, (name, k, col) in enumerate(rows):
    y = 18 + i * 37
    body += text(x0 - 10, y + 17, name, 12, 'end')
    body += f"<rect x='{x0}' y='{y}' width='{max(1.5, bwmax * k / 46)}' height='24' fill='{col}'/>"
    body += text(x0 + max(1.5, bwmax * k / 46) + 6, y + 17, f'{k}/46 ({100 * k / 46:.0f}%)', 12, 'start', INK, 'bold')
open(f'{F}/fig3_funnel.svg', 'w').write(svg(W, H, body))

# ---------- Figure 4 (appendix): 20-excerpt window coverage
W, H = 640, 220; x0, y0, pw, ph = 60, 20, 540, 150
body = ''
xs = [r['n'] for r in win]; xmax = 200
for i in range(0, 101, 25):
    y = y0 + ph - ph * i / 100
    body += f"<line x1='{x0}' x2='{x0 + pw}' y1='{y}' y2='{y}' stroke='{GRID}'/>" + text(x0 - 8, y + 4, f'{i}%', 11, 'end', MUTED)
pts = ' '.join(f"{x0 + pw * r['n'] / xmax},{y0 + ph - ph * r['pairCoverage']}" for r in win)
body += f"<polyline points='{pts}' fill='none' stroke='{C_MARK}' stroke-width='2.5'/>"
for r in win:
    body += f"<circle cx='{x0 + pw * r['n'] / xmax}' cy='{y0 + ph - ph * r['pairCoverage']}' r='3.5' fill='{C_MARK}'/>"
    if r['n'] in (20, 30, 60, 120, 200): body += text(x0 + pw * r['n'] / xmax + 6, y0 + ph - ph * r['pairCoverage'] - 6, f"{100 * r['pairCoverage']:.0f}%", 11, 'start', INK)
for n in (0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200):
    body += text(x0 + pw * n / xmax, y0 + ph + 16, str(n), 11, 'middle', MUTED)
body += text(x0 + pw / 2, y0 + ph + 36, 'Entries in one theme', 12, 'middle', MUTED)
open(f'{F}/fig4_window.svg', 'w').write(svg(W, H, body))
print('fig1', groups, '\nfig2', rows)

# ---------- Figure 0: real text, grouping x prompt (PLAN v14-v17)
v17 = json.load(open(f'{R}/v17_scores.json')); v16 = json.load(open(f'{R}/v16_scores.json'))
runs = {'naive': [v16['per_run'][f'naive/r{i}']['surfaced'] for i in (1, 2, 3)], 'realX': [v16['per_run'][f'realX/r{i}']['surfaced'] for i in (1, 2, 3)], 'production': [0, 0, 0]}
prompts = [('production', 'Shipped prompt'), ('naive', 'Naive prompt'), ('realX', 'realX prompt')]
C_WORD, C_WHOLE = '#8a8f98', '#1d4ed8'
W, H = 640, 235; x0, y0, ph = 70, 36, 130; n = 19
body = ''
for i in range(0, 101, 25):
    y = y0 + ph - ph * i / 100
    body += f"<line x1='{x0}' x2='{W - 20}' y1='{y}' y2='{y}' stroke='{GRID}'/>" + text(x0 - 8, y + 4, f'{i}%', 11, 'end', MUTED)
gw = (W - 20 - x0) / 3; bw = 56
for g, (key, name) in enumerate(prompts):
    cx = x0 + gw * g + gw / 2
    for j, (k, col, sub) in enumerate([(0, C_WORD, ''), (v17['majority'][key]['all']['k'], C_WHOLE, f"runs {', '.join(map(str, runs[key]))}")]):
        p = k / n; lo, hi = wilson(k, n); bx = cx + (j - 0.5) * (bw + 10) - bw / 2; by = y0 + ph - ph * p
        body += f"<rect x='{bx}' y='{by}' width='{bw}' height='{ph * p}' fill='{col}'/>"
        body += f"<line x1='{bx + bw / 2}' x2='{bx + bw / 2}' y1='{y0 + ph - ph * lo}' y2='{y0 + ph - ph * hi}' stroke='{INK}' stroke-width='1.2'/>"
        body += text(bx + bw / 2, by - 6 if hi < 0.9 else y0 + ph - ph * hi - 6, f'{k}/{n}', 11, 'middle', INK, 'bold')
        if sub: body += text(bx + bw / 2, y0 + ph + 34, sub, 10, 'middle', MUTED)
    body += text(cx, y0 + ph + 18, name, 12, 'middle', INK, 'bold')
body += f"<rect x='{x0}' y='14' width='12' height='12' fill='{C_WORD}'/>" + text(x0 + 17, 24, 'Word-overlap themes (shipped grouping)', 11)
body += f"<rect x='{x0 + 270}' y='14' width='12' height='12' fill='{C_WHOLE}'/>" + text(x0 + 287, 24, 'Whole history in one call', 11)
body += text(18, y0 + ph / 2, 'Pairs surfaced', 11, 'middle', MUTED).replace('<text', f"<text transform='rotate(-90 18 {y0 + ph / 2})'", 1)
open(f'{F}/fig0_real.svg', 'w').write(svg(W, H, body))

# ---------- Figure 1 (round 18): documented changes of mind found, by set (case level, cross-era, blind labels)
S18 = json.load(open(f'{R}/v18b_scores.json'))['summary']
sets = [('dev', 'Development', '12 cases, tuned on'), ('fresh1', 'Fresh set 1', '6 cases, diagnosed on'), ('fresh2', 'Fresh set 2', '6 cases, untouched')]
arms = [('Shipped prompt, whole history', '#8a8f98', lambda s: S18.get(f'production/{s}', {}).get('single_majority')),
        ('realX, one call', '#93c5fd', lambda s: S18.get(f'realX/{s}', {}).get('single_majority')),
        ('Deployed fix', '#1d4ed8', lambda s: S18.get('final/fresh2' if s == 'fresh2' else f'realX+changes_long/{s}', {}).get('merged_majority'))]
W, H = 640, 250; x0, y0, ph = 70, 40, 130
body = ''
for i in range(0, 101, 25):
    y = y0 + ph - ph * i / 100
    body += f"<line x1='{x0}' x2='{W - 20}' y1='{y}' y2='{y}' stroke='{GRID}'/>" + text(x0 - 8, y + 4, f'{i}%', 11, 'end', MUTED)
gw = (W - 20 - x0) / 3; bw = 44
for g, (key, name, sub) in enumerate(sets):
    cx = x0 + gw * g + gw / 2; n = S18[f'production/{key}']['n']
    for j, (_, col, get) in enumerate(arms):
        k = get(key); bx = cx + (j - 1) * (bw + 8) - bw / 2
        if k is None:
            body += text(bx + bw / 2, y0 + ph - 6, 'not run', 10, 'middle', MUTED); continue
        p = k / n; lo, hi = wilson(k, n); by = y0 + ph - ph * p
        body += f"<rect x='{bx}' y='{by}' width='{bw}' height='{ph * p}' fill='{col}'/>"
        body += f"<line x1='{bx + bw / 2}' x2='{bx + bw / 2}' y1='{y0 + ph - ph * lo}' y2='{y0 + ph - ph * hi}' stroke='{INK}' stroke-width='1.2'/>"
        body += text(bx + bw / 2, min(by, y0 + ph - ph * hi) - 5, f'{k}/{n}', 11, 'middle', INK, 'bold')
    body += text(cx, y0 + ph + 18, name, 12, 'middle', INK, 'bold') + text(cx, y0 + ph + 33, sub, 10, 'middle', MUTED)
lx = x0
for name, col, _ in arms:
    body += f"<rect x='{lx}' y='12' width='12' height='12' fill='{col}'/>" + text(lx + 17, 22, name, 11); lx += 17 + len(name) * 6.1 + 22
body += text(18, y0 + ph / 2, 'Cases found', 11, 'middle', MUTED).replace('<text', f"<text transform='rotate(-90 18 {y0 + ph / 2})'", 1)
open(f'{F}/fig_cases.svg', 'w').write(svg(W, H, body))
print('fig_cases', {s: [get(s) for _, _, get in arms] for s, _, _ in sets})
