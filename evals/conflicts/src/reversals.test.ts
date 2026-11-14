// Builds the reversal requests (production prompt and the fixed prompt; plain and with a change marker),
// runs the on-device detector on each reversal history, and writes the fixed-prompt variants of held-out requests.
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { findLocalConflicts } from '../../../apps/web/src/features/vault/localConflicts';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import { CONFLICTS_SYSTEM } from './shipped';
import { CONFLICTS_SYSTEM_FIXED } from './variant';

const MARKER = "I used to see this differently, but I've changed my mind. ";
const strip = (t: string) => t.replace(/^PARAPHRASE:\s*/, '').trim();
const ts = (m: string) => Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1, 15) / 1000;
const item = (id: string, body: string, month: string) => ({ id, kind: 'comment', site: 'reddit', subreddit: 'philosophy', title: '', body, permalink: '', createdUtc: ts(month), score: 1, parentId: null, linkId: null, source: 'backlog', philosophy: true }) as never;

test('reversals', () => {
  const cases = JSON.parse(readFileSync('../../paper/data/reversals.json', 'utf8'));
  const lines: string[] = [];
  const local: Record<string, unknown> = {};
  const histories: unknown[] = [];
  for (const c of cases) {
    for (const arm of ['plain', 'marker'] as const) {
      const ex = [
        { id: `${c.id}_earlier`, when: '2016-03', text: strip(c.earlier.claim.text) },
        ...(c.same_era_control ? [{ id: `${c.id}_ctl`, when: '2016-09', text: strip(c.same_era_control.claim) }] : []),
        ...(c.hard_control ? [{ id: `${c.id}_hard`, when: '2017-02', text: strip(c.hard_control.claim) }] : []),
        { id: `${c.id}_later`, when: '2023-03', text: (arm === 'marker' ? MARKER : '') + strip(c.later.claim.text) },
      ].map((e) => ({ ...e, text: e.text.slice(0, 400) }));
      histories.push({ case: c.id, arm, excerpts: ex });
      local[`${c.id}:${arm}`] = findLocalConflicts(ex.map((e) => item(e.id, e.text, e.when)));
      const body = { theme: 'philosophy', excerpts: ex };
      for (const [pname, sys] of [['prod', CONFLICTS_SYSTEM], ['fixed', CONFLICTS_SYSTEM_FIXED]] as const)
        lines.push(JSON.stringify({ id: `rev:${pname}:${arm}:${c.id}`, kind: 'reversal', prompt_version: pname, arm, case: c.id, system: sys, prompt: conflictsPrompt(body), body }));
    }
  }
  // Held-out fixed-prompt variants: oracle requests of t12-t23 and the hand-written decoys (direct).
  for (const l of readFileSync('../../paper/results/requests.jsonl', 'utf8').trim().split('\n')) {
    const r = JSON.parse(l);
    const heldOut = (r.kind === 'oracle' && r.set === 'test' && Number(r.history.slice(1)) >= 12) || r.kind === 'direct';
    if (heldOut) lines.push(JSON.stringify({ ...r, id: `fixed:${r.id}`, prompt_version: 'fixed', base: r.id, system: CONFLICTS_SYSTEM_FIXED }));
  }
  writeFileSync('../../paper/results/requests_rev.jsonl', lines.join('\n') + '\n');
  writeFileSync('../../paper/results/reversal_histories.json', JSON.stringify(histories, null, 1));
  writeFileSync('../../paper/results/local_reversals.json', JSON.stringify(local, null, 1));
  console.log(lines.length, 'requests');
});
