// Stage 6 round-3 reruns, built 2026-11-14 after mock judging round 3 and before any run:
// (1) generality: three generic contradiction prompts nobody tuned for Persona, each on the 36 planted positives unmarked and marked
//     (paired), so the marker effect can be checked beyond the production prompt;
// (2) cost of the repairs: the change marker pasted onto post B of the 40 held-out decoys, under production, the fix line and the
//     cue-free definition rewrite (no empty-list line), to see whether a change sentence alone now produces flags.
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import { CONFLICTS_SYSTEM } from './shipped';
import { CONFLICTS_SYSTEM_FIXED } from './variant';

const MARKER = "I used to see this differently, but I've changed my mind. ";
const FORMAT = 'Respond with only this JSON and nothing else, using the excerpt labels (E1, E2, ...), with a short neutral question in "tension":\n{"conflicts":[{"a":"E1","b":"E4","tension":""}]}';
export const GENERIC = [
  ['genA', `Here are excerpts one person wrote over time. Find pairs of excerpts that contradict each other.\n\n${FORMAT}`],
  ['genB', `You check a person's writing for inconsistencies. List pairs of their claims that are logically inconsistent with each other. Ignore pairs that are only on different topics.\n\n${FORMAT}`],
  ['genC', `Which of these excerpts by one person contradict each other?\n\n${FORMAT}`],
] as const;
const DEF = 'Count a pair only when the person asserts both as their own view, on the same point, and they clash.';
const DEF_NEW = 'Count a pair only when each excerpt, at the time it was written, stated the person\'s own view, on the same point, and the two clash.';
const defNoEmpty = CONFLICTS_SYSTEM.replace(DEF, DEF_NEW).replace('Most themes have none, and an empty list is the right answer then. ', '');
if (defNoEmpty === CONFLICTS_SYSTEM) throw new Error('rewrite not applied');

test('mechanism3', () => {
  const lines: string[] = [];
  const key = JSON.parse(readFileSync('../../paper/data/answer_key.json', 'utf8')) as { set: string; item: string; label: string; b: string }[];
  const reqs = readFileSync('../../paper/results/requests.jsonl', 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  const oracle = new Map(reqs.filter((r) => r.kind === 'oracle').map((r) => [r.item, r]));
  const marked = (r: any, b: string) => ({ ...r.body, excerpts: r.body.excerpts.map((e: any) => (e.id === b ? { ...e, text: (MARKER + e.text).slice(0, 400) } : e)) });
  const push = (pv: string, sys: string, id: string, extra: object, body: any) =>
    lines.push(JSON.stringify({ id: `${pv}:${id}`, prompt_version: pv, ...extra, system: sys, prompt: conflictsPrompt(body), body }));
  for (const it of key.filter((k) => k.set === 'test')) {
    const r = oracle.get(it.item);
    if (!r) continue;
    const meta = { item: it.item, history: r.history, label: it.label, set: 'test' };
    if (['P1', 'P2', 'P4'].includes(it.label))
      for (const [pv, sys] of GENERIC) {
        push(pv, sys, `pl:${it.item}`, { kind: 'genplain', ...meta }, r.body);
        push(pv, sys, `mk:${it.item}`, { kind: 'genmarked', ...meta }, marked(r, it.b));
      }
    if (it.label.startsWith('D') && Number(r.history.slice(1)) >= 12)
      for (const [pv, sys] of [['prod', CONFLICTS_SYSTEM], ['fixed', CONFLICTS_SYSTEM_FIXED], ['defNoEmpty', defNoEmpty]] as const)
        push(pv, sys, `dmk:${it.item}`, { kind: 'markeddecoy', ...meta }, marked(r, it.b));
  }
  writeFileSync('../../paper/results/requests_mech3.jsonl', lines.join('\n') + '\n');
  console.log(lines.length, 'requests');
});
