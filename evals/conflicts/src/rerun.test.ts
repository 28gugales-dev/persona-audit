// Stage 4 reruns, built 2026-11-14 after the critics and before any run:
// (1) the change marker added to every unsignalled test positive (P1, P2, P4: 36 items, oracle requests), prod and fixed;
// (2) three more marker phrasings on the reversals, prod and fixed;
// (3) the second hand-written set (adversarial2.json) as direct requests, prod and fixed;
// (4) end-to-end pipeline requests for held-out histories t12-t23, prod and fixed.
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import { CONFLICTS_SYSTEM } from './shipped';
import { CONFLICTS_SYSTEM_FIXED } from './variant';

const MARKER = "I used to see this differently, but I've changed my mind. ";
const PHRASINGS = ["I've come around on this since I last wrote about it. ", 'My view on this has changed. ', 'I was wrong about this before. '];
const PROMPTS = [['prod', CONFLICTS_SYSTEM], ['fixed', CONFLICTS_SYSTEM_FIXED]] as const;
const strip = (t: string) => t.replace(/^PARAPHRASE:\s*/, '').trim();

test('rerun', () => {
  const lines: string[] = [];
  const push = (id: string, extra: object, body: { theme: string; excerpts: { id: string; when: string; text: string }[] }) => {
    for (const [p, sys] of PROMPTS) lines.push(JSON.stringify({ id: `${p}:${id}`, prompt_version: p, ...extra, system: sys, prompt: conflictsPrompt(body), body }));
  };
  const key = JSON.parse(readFileSync('../../paper/data/answer_key.json', 'utf8')) as { set: string; item: string; label: string; b: string }[];
  const reqs = readFileSync('../../paper/results/requests.jsonl', 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  const oracle = new Map(reqs.filter((r) => r.kind === 'oracle').map((r) => [r.item, r]));
  for (const it of key.filter((k) => k.set === 'test' && ['P1', 'P2', 'P4'].includes(k.label))) {
    const r = oracle.get(it.item);
    if (!r) continue;
    const excerpts = r.body.excerpts.map((e: { id: string; when: string; text: string }) => (e.id === it.b ? { ...e, text: (MARKER + e.text).slice(0, 400) } : e));
    push(`mk:${it.item}`, { kind: 'markerpos', item: it.item, history: r.history, set: 'test' }, { ...r.body, excerpts });
  }
  const cases = JSON.parse(readFileSync('../../paper/data/reversals.json', 'utf8'));
  cases.forEach((c: any) => PHRASINGS.forEach((m, i) => {
    const excerpts = [
      { id: `${c.id}_earlier`, when: '2016-03', text: strip(c.earlier.claim.text) },
      ...(c.same_era_control ? [{ id: `${c.id}_ctl`, when: '2016-09', text: strip(c.same_era_control.claim) }] : []),
      ...(c.hard_control ? [{ id: `${c.id}_hard`, when: '2017-02', text: strip(c.hard_control.claim) }] : []),
      { id: `${c.id}_later`, when: '2023-03', text: m + strip(c.later.claim.text) },
    ].map((e) => ({ ...e, text: e.text.slice(0, 400) }));
    push(`ph${i + 1}:${c.id}`, { kind: 'phrasing', case: c.id, phrasing: i + 1 }, { theme: 'philosophy', excerpts });
  }));
  const adv2 = JSON.parse(readFileSync('../../paper/data/adversarial2.json', 'utf8')).items;
  for (const it of adv2)
    push(`adv2:${it.id}`, { kind: 'adv2', item: it.id, type: it.type, conflict: it.conflict }, { theme: 'philosophy', excerpts: [{ id: `${it.id}_a`, when: it.a_month, text: it.a }, { id: `${it.id}_b`, when: it.b_month, text: it.b }] });
  for (const r of reqs.filter((r) => r.kind === 'pipeline' && r.set === 'test' && Number(r.history.slice(1)) >= 12))
    push(`pipe:${r.id}`, { kind: 'pipeline_heldout', base: r.id, history: r.history, set: 'test' }, r.body);
  writeFileSync('../../paper/results/requests_rerun.jsonl', lines.join('\n') + '\n');
  console.log(lines.length, 'requests');
});
