// Stage 6 round-2 reruns, built 2026-11-14 after mock judging round 2 and before any run:
// (1) rewrite only the conflict definition so it no longer implies both views are held now ("defOnly"), and the same with the
//     empty-list default removed too ("defNoEmpty"); neither mentions a change of mind. Same items as mechanism.test.ts:
//     36 marked planted positives, 10 marked reversals, 10 natural narrations (P3), 40 held-out decoys.
// (2) harness check (no new requests): the 36 marked and 36 unmarked production requests rerun with a different wrapper
//     and effort "medium" (production's setting), written as run 3.
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { CONFLICTS_SYSTEM } from './shipped';

const DEF = 'Count a pair only when the person asserts both as their own view, on the same point, and they clash.';
const DEF_NEW = 'Count a pair only when each excerpt, at the time it was written, stated the person\'s own view, on the same point, and the two clash.';
const EMPTY = 'Most themes have none, and an empty list is the right answer then. ';
const defOnly = CONFLICTS_SYSTEM.replace(DEF, DEF_NEW);
const defNoEmpty = defOnly.replace(EMPTY, '');
if (defOnly === CONFLICTS_SYSTEM || defNoEmpty === defOnly) throw new Error('rewrite not applied');
export const VARIANTS = [['defOnly', defOnly], ['defNoEmpty', defNoEmpty]] as const;

test('mechanism2', () => {
  const src = readFileSync('../../paper/results/requests_mech.jsonl', 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  const lines: string[] = [];
  for (const r of src.filter((r) => r.prompt_version === 'noDNC'))
    for (const [pv, sys] of VARIANTS)
      lines.push(JSON.stringify({ ...r, id: r.id.replace(/^noDNC:/, `${pv}:`), prompt_version: pv, system: sys }));
  writeFileSync('../../paper/results/requests_mech2.jsonl', lines.join('\n') + '\n');
  console.log(lines.length, 'requests');
});
