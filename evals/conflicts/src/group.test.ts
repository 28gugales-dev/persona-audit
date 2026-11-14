// PLAN v12: conflict requests from the model-based grouping (make_group.py), built by the shipped request builder
// (20-excerpt window, 400-character cut, 60-character filter), under the arms in ARMS (default prod,genX; realX = PLAN v13).
// Run: GROUP=<version>_<set> [ARMS=genX,realX] [HIST=<histories file>] npx vitest run src/group.test.ts
//   -> paper/results/requests_group_<version>_<set>.jsonl
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { conflictRequests } from '../../../apps/web/src/features/vault/conflicts';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import { CONFLICTS_SYSTEM } from './shipped';
import type { ActivityItem } from '../../../apps/web/src/features/activity/types';

const R = '../../paper/results/';
interface Post { id: string; body: string; createdUtc: number }
const asItem = (p: Post): ActivityItem => ({ id: p.id, kind: 'comment', site: 'reddit', subreddit: 'philosophy', title: '', body: p.body, permalink: '', createdUtc: p.createdUtc, score: 1, parentId: null, linkId: null, source: 'backlog', philosophy: true });

test('group', () => {
  const tag = process.env.GROUP;
  if (!tag) return;
  const set = tag.split('_').pop();
  const genX = readFileSync(R + 'requests_mech7.jsonl', 'utf8').trim().split('\n').map((l) => JSON.parse(l)).find((r) => r.prompt_version === 'genX').system as string;
  const themes: Record<string, { term: string; itemIds: string[] }[]> = JSON.parse(readFileSync(`${R}group_themes_${tag}.json`, 'utf8'));
  const realX = JSON.parse(readFileSync('gen/real_prompts.json', 'utf8')).realX_v1 as string;
  const all = { prod: CONFLICTS_SYSTEM, genX, realX } as Record<string, string>;
  const arms = (process.env.ARMS ?? 'prod,genX').split(',').map((a) => [a, all[a]] as const);
  if (arms.some(([, sys]) => !sys)) throw new Error('unknown arm');
  const histories: { id: string; posts: Post[] }[] = set?.startsWith('real')
    ? JSON.parse(readFileSync(`../../paper/data/${process.env.HIST ?? 'realtext_histories.json'}`, 'utf8')).map((h: { case: string; posts: Post[] }) => ({ id: h.case, posts: h.posts }))
    : JSON.parse(readFileSync('../../paper/data/histories.json', 'utf8')).map((h: { history: string; posts: Post[] }) => ({ id: h.history, posts: h.posts }));
  const out: string[] = [];
  for (const h of histories) {
    if (!themes[h.id]) continue;
    const byId = new Map(h.posts.map((p) => [p.id, asItem(p)]));
    const groups = themes[h.id].map((t, i) => ({ term: `g${i}`, label: t.term, itemIds: t.itemIds }));
    for (const req of conflictRequests(groups, byId, {}))
      for (const [pv, sys] of arms)
        out.push(JSON.stringify({ id: `${pv}:grp${tag}:${h.id}:${req.term}`, prompt_version: pv, kind: 'group', history: h.id, term: req.term, system: sys, prompt: conflictsPrompt(req.body), body: req.body }));
  }
  writeFileSync(`${R}requests_group_${tag}.jsonl`, out.join('\n') + '\n');
});
