// Q3, no model: of all planted pairs (i, j) in one theme of n written entries, what share
// reach the model together, given the real conflictRequests sampler (20 excerpts, spread over time)?
import { test } from 'vitest';
import { writeFileSync } from 'node:fs';
import { conflictRequests } from '../../../apps/web/src/features/vault/conflicts';

const item = (i: number) => ({ id: `e${i}`, kind: 'comment', site: 'reddit', subreddit: 'philosophy', title: '', body: `Entry ${i}: ${'a long enough sentence about one theme so the excerpt clears the minimum length. '.repeat(1)}`, permalink: '', createdUtc: 1.5e9 + i * 86_400 * 7, score: 1, parentId: null, linkId: null, source: 'backlog', philosophy: true }) as any;

test('window coverage by theme size', () => {
  const rows: { n: number; sent: number; pairCoverage: number }[] = [];
  for (const n of [5, 10, 20, 21, 30, 40, 60, 80, 120, 200]) {
    const entries = Array.from({ length: n }, (_, i) => item(i));
    const byId = new Map(entries.map((e) => [e.id, e]));
    const [req] = conflictRequests([{ term: 't', label: 't', itemIds: entries.map((e) => e.id) }], byId, {});
    const sent = new Set(req!.body.excerpts.map((e) => e.id));
    let both = 0, all = 0;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) { all++; if (sent.has(`e${i}`) && sent.has(`e${j}`)) both++; }
    rows.push({ n, sent: sent.size, pairCoverage: both / all });
  }
  writeFileSync('../../paper/results/q3_window_coverage.json', JSON.stringify(rows, null, 1));
  console.table(rows);
});
