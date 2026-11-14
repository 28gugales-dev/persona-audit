// Reads raw model outputs (paper/results/raw/<model>.jsonl: {id, text}) through the production readConflicts.
import { test } from 'vitest';
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { readConflicts } from '../../../apps/api/src/features/persona/conflicts';

const OUT = '../../paper/results';
test('parse', () => {
  const requests = new Map(readFileSync(`${OUT}/requests.jsonl`, 'utf8').trim().split('\n').map((l) => { const r = JSON.parse(l); return [r.id, r]; }));
  for (const file of readdirSync(`${OUT}/raw`).filter((f) => f.endsWith('.jsonl'))) {
    const parsed: unknown[] = [];
    for (const line of readFileSync(`${OUT}/raw/${file}`, 'utf8').trim().split('\n').filter(Boolean)) {
      const { id, text, run } = JSON.parse(line);
      const req = requests.get(id);
      if (!req) continue;
      const res = readConflicts(text ?? '', req.body);
      parsed.push({ id, run: run ?? 1, ok: res !== null, conflicts: res?.conflicts ?? [] });
    }
    writeFileSync(`${OUT}/parsed/${file.replace('.jsonl', '.json')}`, JSON.stringify(parsed));
    console.log(file, parsed.length);
  }
});
