"""v25: unseen histories (fresh sets 2-3) with the author's names and own-work titles masked and dates shifted so each history starts in 2001 (gaps kept).
Run: python3 evals/conflicts/gen/make_masked.py <repo root>"""
import json, sys, re, copy, datetime
import make_whole as W

ROOT = W.ROOT = sys.argv[1]
NAMES = {'lyell': ['Charles Lyell', 'Lyell'], 'besant': ['Annie Besant', 'Besant'], 'darwin': ['Charles Darwin', 'Darwin'], 'buckland': ['William Buckland', 'Buckland'],
         'sedgwick': ['Adam Sedgwick', 'Sedgwick'], 'newton': ['John Newton', 'Newton'], 'coleridge': ['Samuel Taylor Coleridge', 'S. T. Coleridge', 'Coleridge'],
         'miller': ['Hugh Miller', 'Miller'], 'ruskin': ['John Ruskin', 'Ruskin'], 'frazer': ['James George Frazer', 'J. G. Frazer', 'Frazer'], 'wordsworth': ['William Wordsworth', 'Wordsworth']}
TITLES = ['Principles of Geology', 'Antiquity of Man', 'My Path to Atheism', 'Origin of Species', 'Reliquiae Diluvianae', 'Bridgewater Treatise', 'Biographia Literaria',
          'Conciones ad Populum', 'The Watchman', 'Old Red Sandstone', 'Footprints of the Creator', 'Testimony of the Rocks', 'First Impressions of England',
          'Modern Painters', 'Golden Bough', 'Totemism and Exogamy']

def mask(text, case):
    n = 0
    for t in TITLES:
        text, k = re.subn(re.escape(t), 'an earlier work', text, flags=re.I); n += k
    for name in NAMES[case.split('_')[0]]:
        text, k = re.subn(r'\b' + re.escape(name) + r'\b', 'the author', text); n += k
    return text, n

def shift(h):
    first = min(datetime.datetime.fromtimestamp(p['createdUtc'], datetime.UTC).year for p in h['posts'])
    for p in h['posts']:
        d = datetime.datetime.fromtimestamp(p['createdUtc'], datetime.UTC)
        p['createdUtc'] = int(d.replace(year=d.year - first + 2001, day=min(d.day, 28)).timestamp())

if __name__ == '__main__':
    total = 0
    for prompt, prefix, out, cap, tot in (('realX_deployed', 'v25ms', 'requests_v25_masked_ships.jsonl', 1000, 120000), ('production', 'v25mp', 'requests_v25_masked_prod.jsonl', 400, None)):
        sysp = W.system(prompt)
        with open(f'{ROOT}/paper/results/{out}', 'w') as f:
            for suf in '45':
                for h in json.load(open(f'{ROOT}/paper/data/realtext_histories{suf}.json')):
                    h = copy.deepcopy(h); shift(h); c = 0
                    for p in h['posts']: p['body'], k = mask(p['body'], h['case']); c += k
                    if prompt == 'production': total += c; print(h['case'], 'masked', c)
                    r = W.build(h, sysp, prefix, f'set{suf}', cap, tot); r['prompt_version'] = prompt + '+masked'; f.write(json.dumps(r) + '\n')
                    open(f"{ROOT}/paper/results/haiku_in/{r['id'].replace(':', '__')}.txt", 'w').write(f"=== SYSTEM PROMPT ===\n{sysp}\n\n=== USER MESSAGE ===\n{r['prompt']}\n")
    print('masked spans', total)
