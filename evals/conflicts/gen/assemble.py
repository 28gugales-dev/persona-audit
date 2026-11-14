"""Turn the writer's output (test), the hand-written items (adversarial) and templates (dev)
into dated histories of posts, plus an answer key. Seeded; same input, same output."""
import json, random, sys, glob, calendar, datetime
ROOT, WRITER = sys.argv[1], sys.argv[2]
rng = random.Random(7)
POS = {'P1', 'P2', 'P3', 'P4', 'H1', 'H2', 'N1'}

def ts(month, day=None):
    y, m = map(int, month.split('-'))
    d = day or rng.randint(1, 28)
    return int(calendar.timegm(datetime.datetime(y, m, d, rng.randint(8, 22), rng.randint(0, 59)).timetuple()))

def add_months(month, k):
    y, m = map(int, month.split('-')); t = y * 12 + m - 1 + k
    return f'{t // 12}-{t % 12 + 1:02d}'

def post(pid, body, t, role, item=None):
    return {'id': pid, 'body': body, 'createdUtc': t, 'role': role, 'item': item}

def build_test():
    spec = {h['history']: h for h in json.load(open(f'{ROOT}/paper/data/test_spec.json'))['histories']}
    hist, key = [], []
    for f in sorted(glob.glob(f'{WRITER}/out*.json')):
        for h in json.load(open(f))['histories']:
            s = {i['item']: i for i in spec[h['history']]['items']}
            posts = []
            for it in h['items']:
                sp = s[it['item']]
                ta, tb = ts(sp['a_month']), ts(sp['b_month'])
                posts.append(post(f"{it['item']}_a", it['post_a'], ta, 'a', it['item']))
                posts.append(post(f"{it['item']}_b", it['post_b'], tb, 'b', it['item']))
                for j, fb in enumerate(it['fillers']):
                    posts.append(post(f"{it['item']}_f{j}", fb, ts(add_months(sp['a_month'], rng.randint(-6, 2))), 'filler', it['item']))
                key.append({'set': 'test', 'history': h['history'], 'item': it['item'], 'label': sp['label'], 'conflict': sp['label'] in POS,
                            'a': f"{it['item']}_a", 'b': f"{it['item']}_b", 'gap_months': sp['gap_months'], 'question_id': sp['question_id']})
            for j, ob in enumerate(h['offtopic']):
                posts.append(post(f"{h['history']}_o{j}", ob, ts(f"{rng.randint(2021, 2024)}-{rng.randint(1, 12):02d}"), 'offtopic'))
            hist.append({'set': 'test', 'history': h['history'], 'posts': posts})
    return hist, key

def build_adversarial(offtopic_pool):
    items = json.load(open(f'{ROOT}/paper/data/adversarial.json'))['items']
    hist, key = [], []
    for h in range(6):
        posts = []
        for it in items[h * 5:(h + 1) * 5]:
            posts.append(post(f"{it['id']}_a", it['a'], ts(it['a_month']), 'a', it['id']))
            posts.append(post(f"{it['id']}_b", it['b'], ts(it['b_month']), 'b', it['id']))
            y1, m1 = map(int, it['a_month'].split('-')); y2, m2 = map(int, it['b_month'].split('-'))
            key.append({'set': 'adversarial', 'history': f'x{h}', 'item': it['id'], 'label': it['type'], 'conflict': it['conflict'],
                        'a': f"{it['id']}_a", 'b': f"{it['id']}_b", 'gap_months': (y2 - y1) * 12 + m2 - m1})
        for j, ob in enumerate(rng.sample(offtopic_pool, 6)):
            posts.append(post(f'x{h}_o{j}', ob, ts(f"{rng.randint(2021, 2024)}-{rng.randint(1, 12):02d}"), 'offtopic'))
        hist.append({'set': 'adversarial', 'history': f'x{h}', 'posts': posts})
    return hist, key

TEMPLATES = {
    'P1': ('I am convinced of this: {x}', 'I am convinced of this: {y}'),
    'P3': ('I am convinced of this: {x}', 'I used to think otherwise, but now I believe {yl}'),
    'D1': ('I am convinced of this: {x}', 'My professor says {yl} I do not buy it.'),
    'D2': ('I am convinced of this: {x}', 'I am less sure now that {xl}'),
    'D3': ('I am convinced of this: {x}', 'Is it true that {yq}?'),
    'D7': ('I am convinced of this: {x}', 'Still my view: {x}'),
}
def build_dev():
    spec = json.load(open(f'{ROOT}/paper/data/test_spec.json'))['histories']
    labels = [l for l in TEMPLATES for _ in range(10)]
    rng.shuffle(labels)
    hist, key, k = [], [], 0
    for h in range(12):
        posts = []
        for it in spec[h]['items']:
            lab = labels[k]; k += 1
            x, y = it['view_X'], it['view_Y']
            ta_t, tb_t = TEMPLATES[lab]
            fmt = dict(x=x, y=y, xl=x[0].lower() + x[1:], yl=y[0].lower() + y[1:], yq=(y[0].lower() + y[1:]).rstrip('.'))
            iid = f"d{h:02d}_{it['item'][-1]}"
            posts.append(post(f'{iid}_a', ta_t.format(**fmt), ts(it['a_month']), 'a', iid))
            posts.append(post(f'{iid}_b', tb_t.format(**fmt), ts(it['b_month']), 'b', iid))
            key.append({'set': 'dev', 'history': f'd{h:02d}', 'item': iid, 'label': lab, 'conflict': lab in POS,
                        'a': f'{iid}_a', 'b': f'{iid}_b', 'gap_months': it['gap_months'], 'question_id': it['question_id']})
        hist.append({'set': 'dev', 'history': f'd{h:02d}', 'posts': posts})
    return hist, key

th, tk = build_test()
pool = [p['body'] for h in th for p in h['posts'] if p['role'] == 'offtopic']
ah, ak = build_adversarial(pool)
dh, dk = build_dev()
json.dump(th + ah + dh, open(f'{ROOT}/paper/data/histories.json', 'w'), indent=0)
json.dump(tk + ak + dk, open(f'{ROOT}/paper/data/answer_key.json', 'w'), indent=0)
print(len(th), len(ah), len(dh), 'histories;', len(tk), len(ak), len(dk), 'items')
