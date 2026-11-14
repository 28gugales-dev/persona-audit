// Stage 6 round-3b, built 2026-11-14 after seeing that the generic prompts lose nothing to the marker, before any run:
// what the production prompt's careful definition buys. The three generic prompts on the 40 held-out decoys (unmarked).
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';

const FORMAT = 'Respond with only this JSON and nothing else, using the excerpt labels (E1, E2, ...), with a short neutral question in "tension":\n{"conflicts":[{"a":"E1","b":"E4","tension":""}]}';
const GENERIC = [
  ['genA', `Here are excerpts one person wrote over time. Find pairs of excerpts that contradict each other.\n\n${FORMAT}`],
  ['genB', `You check a person's writing for inconsistencies. List pairs of their claims that are logically inconsistent with each other. Ignore pairs that are only on different topics.\n\n${FORMAT}`],
  ['genC', `Which of these excerpts by one person contradict each other?\n\n${FORMAT}`],
] as const;

test('mechanism4', () => {
  const key = JSON.parse(readFileSync('../../paper/data/answer_key.json', 'utf8')) as { set: string; item: string; label: string }[];
  const reqs = readFileSync('../../paper/results/requests.jsonl', 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  const oracle = new Map(reqs.filter((r) => r.kind === 'oracle').map((r) => [r.item, r]));
  const lines: string[] = [];
  for (const it of key.filter((k) => k.set === 'test' && k.label.startsWith('D'))) {
    const r = oracle.get(it.item);
    if (!r || Number(r.history.slice(1)) < 12) continue;
    for (const [pv, sys] of GENERIC)
      lines.push(JSON.stringify({ id: `${pv}:dpl:${it.item}`, prompt_version: pv, kind: 'gendecoy', item: it.item, history: r.history, label: it.label, set: 'test', system: sys, prompt: conflictsPrompt(r.body), body: r.body }));
  }
  writeFileSync('../../paper/results/requests_mech4.jsonl', lines.join('\n') + '\n');
  console.log(lines.length, 'requests');
});
