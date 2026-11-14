// Stage 6 mechanism reruns, built 2026-11-14 after mock judging round 1 and before any run:
// is the drop caused by the change cue or by any prefix, and which line of the prompt causes it?
// (1) neutral, non-revision prefix on post B of the 36 unsignalled positives and the 10 reversals, production prompt;
// (2) the change marker on the same items under three ablated prompts (no "Do not count" list; only its doubt line removed;
//     no "empty list is the right answer" line), plus GPT's natural narrated changes (P3, 10) and held-out decoys (t12-t23, 40)
//     under each ablation, so any recall gained is priced in false flags.
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import { CONFLICTS_SYSTEM } from './shipped';

const MARKER = "I used to see this differently, but I've changed my mind. ";
const NEUTRAL = 'I was reading about this again today. ';
const cut = (from: string) => {
  const out = CONFLICTS_SYSTEM.replace(from, '');
  if (out === CONFLICTS_SYSTEM) throw new Error(`not found: ${from}`);
  return out;
};
export const ABLATIONS = [
  ['noDNC', cut(CONFLICTS_SYSTEM.slice(CONFLICTS_SYSTEM.indexOf('Do not count:'), CONFLICTS_SYSTEM.indexOf('Most themes have none')))],
  ['noDoubt', cut('- questions, doubt, or being less sure than before\n')],
  ['noEmpty', cut('Most themes have none, and an empty list is the right answer then. ')],
] as const;
const strip = (t: string) => t.replace(/^PARAPHRASE:\s*/, '').trim();
type Excerpt = { id: string; when: string; text: string };

test('mechanism', () => {
  const lines: string[] = [];
  const push = (pv: string, sys: string, id: string, extra: object, body: { theme: string; excerpts: Excerpt[] }) =>
    lines.push(JSON.stringify({ id: `${pv}:${id}`, prompt_version: pv, ...extra, system: sys, prompt: conflictsPrompt(body), body }));
  const key = JSON.parse(readFileSync('../../paper/data/answer_key.json', 'utf8')) as { set: string; item: string; label: string; b: string; history: string }[];
  const reqs = readFileSync('../../paper/results/requests.jsonl', 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  const oracle = new Map(reqs.filter((r) => r.kind === 'oracle').map((r) => [r.item, r]));
  const prefixed = (r: { body: { theme: string; excerpts: Excerpt[] } }, b: string, prefix: string) =>
    ({ ...r.body, excerpts: r.body.excerpts.map((e) => (e.id === b ? { ...e, text: (prefix + e.text).slice(0, 400) } : e)) });

  for (const it of key.filter((k) => k.set === 'test')) {
    const r = oracle.get(it.item);
    if (!r) continue;
    const meta = { item: it.item, history: r.history, label: it.label, set: 'test' };
    if (['P1', 'P2', 'P4'].includes(it.label)) {
      push('prod', CONFLICTS_SYSTEM, `neu:${it.item}`, { kind: 'neutralpos', ...meta }, prefixed(r, it.b, NEUTRAL));
      for (const [pv, sys] of ABLATIONS) push(pv, sys, `mk:${it.item}`, { kind: 'markerpos', ...meta }, prefixed(r, it.b, MARKER));
    } else if (it.label === 'P3' || (it.label.startsWith('D') && Number(r.history.slice(1)) >= 12)) {
      for (const [pv, sys] of ABLATIONS) push(pv, sys, `or:${it.item}`, { kind: 'oracle', ...meta }, r.body);
    }
  }
  const cases = JSON.parse(readFileSync('../../paper/data/reversals.json', 'utf8'));
  for (const c of cases) {
    const body = (prefix: string) => ({
      theme: 'philosophy',
      excerpts: [
        { id: `${c.id}_earlier`, when: '2016-03', text: strip(c.earlier.claim.text) },
        ...(c.same_era_control ? [{ id: `${c.id}_ctl`, when: '2016-09', text: strip(c.same_era_control.claim) }] : []),
        ...(c.hard_control ? [{ id: `${c.id}_hard`, when: '2017-02', text: strip(c.hard_control.claim) }] : []),
        { id: `${c.id}_later`, when: '2023-03', text: prefix + strip(c.later.claim.text) },
      ].map((e) => ({ ...e, text: e.text.slice(0, 400) })),
    });
    push('prod', CONFLICTS_SYSTEM, `rneu:${c.id}`, { kind: 'rev', arm: 'neutral', case: c.id }, body(NEUTRAL));
    for (const [pv, sys] of ABLATIONS) push(pv, sys, `rmk:${c.id}`, { kind: 'rev', arm: 'marker', case: c.id }, body(MARKER));
  }
  writeFileSync('../../paper/results/requests_mech.jsonl', lines.join('\n') + '\n');
  console.log(lines.length, 'requests');
});
