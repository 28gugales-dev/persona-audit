"""Send each request (system + prompt, verbatim) to a model through `opencode run`, one fresh session per call.
Usage: run_opencode.py <requests.jsonl> <out.jsonl> <model> [kind-filter] [workers]
Appends {id, model, text, run}; skips ids already done (crash-safe). The system prompt is passed as the first
block of the message because opencode does not take a separate system prompt; this is disclosed in the paper."""
import json, subprocess, sys, os, concurrent.futures as cf, threading, tempfile
reqs_path, out_path, model = sys.argv[1], sys.argv[2], sys.argv[3]
kind = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != 'all' else None
workers = int(sys.argv[5]) if len(sys.argv) > 5 else 4
done = set()
if os.path.exists(out_path):
    done = {json.loads(l)['id'] for l in open(out_path) if l.strip()}
reqs = [json.loads(l) for l in open(reqs_path) if l.strip()]
reqs = [r for r in reqs if r['id'] not in done and (kind is None or r['kind'] == kind)]
lock = threading.Lock()
cwd = tempfile.mkdtemp()
def call(r):
    msg = f"Follow these instructions exactly.\n\n<instructions>\n{r['system']}\n</instructions>\n\n{r['prompt']}\n\nDo not use any tools. Reply with only the JSON."
    for attempt in range(3):
        try:
            p = subprocess.run(['opencode', 'run', '--archived', '--format', 'json', '-m', model, msg], capture_output=True, text=True, timeout=240, cwd=cwd)
        except subprocess.TimeoutExpired:
            continue
        text = ''.join(json.loads(l)['part'].get('text', '') for l in p.stdout.splitlines() if l.startswith('{') and json.loads(l).get('type') == 'text')
        if text.strip():
            return text
        err = (p.stderr or p.stdout)[-300:]
        if 'limit' in err.lower():
            print('LIMIT', r['id'], err, file=sys.stderr); return None
    return None
def work(r):
    text = call(r)
    if text is None: return
    with lock, open(out_path, 'a') as f:
        f.write(json.dumps({'id': r['id'], 'model': model, 'text': text, 'run': 1}) + '\n')
with cf.ThreadPoolExecutor(workers) as ex:
    list(ex.map(work, reqs))
print('done', len(reqs), 'attempted')
