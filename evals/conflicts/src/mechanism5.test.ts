// Stage 6 round-4 reruns, built 2026-11-14 after mock judging round 4 and before any run. The cue-free rewrite was chosen after
// seeing the ablations, so it is confirmed here on items it was not chosen on:
// (1) 40 fresh narrated items written by GPT from ../../paper/data/fresh_spec.md (20 narrated reversals in varied wording; 20 narrated
//     look-alikes: refinement, reaffirmation, doubt), under production, the fix line, the rewrite (no empty-list line) and generic A;
// (2) the rewrite on all 50 hand-written items and end to end on held-out histories t12-t23;
// (3) generic A plus the production exclusion list, on the 36 marked positives and 40 held-out decoys (does the list buy the precision?).
// Run-to-run variance (no new requests): production and rewrite marked requests re-run twice more.
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import { CONFLICTS_SYSTEM } from './shipped';
import { CONFLICTS_SYSTEM_FIXED } from './variant';

const DEF = 'Count a pair only when the person asserts both as their own view, on the same point, and they clash.';
const DEF_NEW = 'Count a pair only when each excerpt, at the time it was written, stated the person\'s own view, on the same point, and the two clash.';
const defNoEmpty = CONFLICTS_SYSTEM.replace(DEF, DEF_NEW).replace('Most themes have none, and an empty list is the right answer then. ', '');
const EXCL = CONFLICTS_SYSTEM.slice(CONFLICTS_SYSTEM.indexOf('Do not count:'), CONFLICTS_SYSTEM.indexOf('Most themes have none'));
const R = '../../paper/results/';
const lines = (f: string) => readFileSync(R + f, 'utf8').trim().split('\n').map((l) => JSON.parse(l));

test('mechanism5', () => {
  const out: string[] = [];
  const push = (r: object) => out.push(JSON.stringify(r));
  const genA = lines('requests_mech3.jsonl').find((r) => r.prompt_version === 'genA').system as string;
  const genX = genA.replace('Find pairs of excerpts that contradict each other.\n\n', `Find pairs of excerpts that contradict each other.\n\n${EXCL}`);
  if (genX === genA || !defNoEmpty.includes(DEF_NEW)) throw new Error('variant not built');
  const fresh = JSON.parse(readFileSync('../../paper/data/fresh_narrated.json', 'utf8'));
  for (const it of fresh) {
    const body = { theme: 'philosophy', excerpts: [{ id: `${it.id}_a`, when: '2018-03', text: it.a }, { id: `${it.id}_b`, when: '2023-03', text: it.b }] };
    for (const [pv, sys] of [['prod', CONFLICTS_SYSTEM], ['fixed', CONFLICTS_SYSTEM_FIXED], ['defNoEmpty', defNoEmpty], ['genA', genA]])
      push({ id: `${pv}:fresh:${it.id}`, prompt_version: pv, kind: 'fresh', item: it.id, label: it.label, system: sys, prompt: conflictsPrompt(body), body });
  }
  for (const r of lines('requests.jsonl').filter((r) => r.kind === 'direct'))
    push({ ...r, id: `defNoEmpty:hw:${r.item}`, kind: 'hw1', prompt_version: 'defNoEmpty', system: defNoEmpty });
  for (const r of lines('requests_rerun.jsonl').filter((r) => r.kind === 'adv2' && r.prompt_version === 'prod'))
    push({ ...r, id: r.id.replace(/^prod:/, 'defNoEmpty:'), prompt_version: 'defNoEmpty', system: defNoEmpty });
  for (const r of lines('requests_rerun.jsonl').filter((r) => r.kind === 'pipeline_heldout' && r.prompt_version === 'prod'))
    push({ ...r, id: r.id.replace(/^prod:/, 'defNoEmpty:'), prompt_version: 'defNoEmpty', system: defNoEmpty });
  for (const r of lines('requests_mech3.jsonl').filter((r) => r.prompt_version === 'genA' && r.kind === 'genmarked'))
    push({ ...r, id: r.id.replace(/^genA:/, 'genX:'), prompt_version: 'genX', system: genX });
  for (const r of lines('requests_mech4.jsonl').filter((r) => r.prompt_version === 'genA'))
    push({ ...r, id: r.id.replace(/^genA:/, 'genX:'), prompt_version: 'genX', system: genX });
  writeFileSync(R + 'requests_mech5.jsonl', out.join('\n') + '\n');
  console.log(out.length, 'requests');
});
