// PLAN v11 (real text). Builds requests from philosophers' own public-domain words:
// (A) oracle pairs early+announced, early+unannounced, early+control, 400-character cut lifted;
// (B) one history per case (sampled paragraphs of the early and later works plus the case's passages),
//     run unmodified through the shipped theme sort and request builder.
// Arms: production, the rewrite (defNoEmpty) and genX, built as in mechanism5.test.ts.
// Writes paper/results/requests_real.jsonl and paper/results/real_themes.json.
// PLAN v13 held-out: REAL=2 ARMS=prod,genX,realX reads realtext_cases2.json / realtext_histories2.json and writes *_real2.* files.
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { sortLibrary } from '../../../apps/web/src/features/vault/sort';
import { conflictRequests } from '../../../apps/web/src/features/vault/conflicts';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import { CONFLICTS_SYSTEM } from './shipped';
import type { ActivityItem } from '../../../apps/web/src/features/activity/types';

const DEF = 'Count a pair only when the person asserts both as their own view, on the same point, and they clash.';
const DEF_NEW = 'Count a pair only when each excerpt, at the time it was written, stated the person\'s own view, on the same point, and the two clash.';
const defNoEmpty = CONFLICTS_SYSTEM.replace(DEF, DEF_NEW).replace('Most themes have none, and an empty list is the right answer then. ', '');
const R = '../../paper/results/';
const lines = (f: string) => readFileSync(R + f, 'utf8').trim().split('\n').map((l) => JSON.parse(l));
interface Passage { text: string; written: number }
interface Case { id: string; early: Passage; announced: Passage | null; unannounced: Passage | null; control: Passage | null }
interface Post { id: string; body: string; createdUtc: number; role: string }

const ts = (year: number, month: number) => Date.UTC(year, month - 1, 15) / 1000;
const asItem = (p: Post): ActivityItem => ({ id: p.id, kind: 'comment', site: 'reddit', subreddit: 'philosophy', title: '', body: p.body, permalink: '', createdUtc: p.createdUtc, score: 1, parentId: null, linkId: null, source: 'backlog', philosophy: true });

test('realtext', () => {
  const genX = lines('requests_mech7.jsonl').find((r) => r.prompt_version === 'genX').system as string;
  if (defNoEmpty === CONFLICTS_SYSTEM || !genX.includes('Do not count:')) throw new Error('variant not built');
  const realX = JSON.parse(readFileSync('gen/real_prompts.json', 'utf8')).realX_v1 as string;
  const all = { prod: CONFLICTS_SYSTEM, defNoEmpty, genX, realX } as Record<string, string>;
  const ARMS = (process.env.ARMS ?? 'prod,defNoEmpty,genX').split(',').map((a) => [a, all[a]] as const);
  const SUF = process.env.REAL ?? '';
  const out: string[] = [];
  const push = (r: object) => out.push(JSON.stringify(r));

  const cases: Case[] = JSON.parse(readFileSync(`../../paper/data/realtext_cases${SUF}.json`, 'utf8')).filter((c: Case) => c.announced || c.unannounced);
  for (const c of cases) {
    const ex = (tag: string, p: Passage, month: number) => ({ id: `${c.id}_${tag}`, when: new Date(ts(p.written, month) * 1000).toISOString().slice(0, 7), text: p.text });
    const pairs = [
      ['ann', c.announced && [ex('early', c.early, 3), ex('ann', c.announced, 3)]],
      ['unann', c.unannounced && [ex('early', c.early, 3), ex('unann', c.unannounced, 3)]],
      ['ctl', c.control && [ex('early', c.early, 3), ex('ctl', c.control, 6)]],
    ] as const;
    for (const [pair, excerpts] of pairs) {
      if (!excerpts) continue;
      const body = { theme: 'philosophy', excerpts };
      for (const [pv, sys] of ARMS) push({ id: `${pv}:realA${SUF}:${c.id}:${pair}`, prompt_version: pv, kind: 'realA', case: c.id, pair, system: sys, prompt: conflictsPrompt(body), body });
    }
  }

  const histories: { case: string; posts: Post[] }[] = JSON.parse(readFileSync(`../../paper/data/realtext_histories${SUF}.json`, 'utf8'));
  const themes: Record<string, { term: string; itemIds: string[] }[]> = {};
  for (const h of histories) {
    const entries = h.posts.map(asItem);
    const byId = new Map(entries.map((e) => [e.id, e]));
    const sorted = sortLibrary(entries);
    const groups = [...sorted.smaller, ...sorted.clusters].map((g) => ({ term: g.term, label: g.term, itemIds: g.itemIds }));
    themes[h.case] = groups.map((g) => ({ term: g.term, itemIds: g.itemIds }));
    for (const req of conflictRequests(groups, byId, {}))
      for (const [pv, sys] of ARMS)
        push({ id: `${pv}:realB${SUF}:${h.case}:${req.term.replace(/[^\w-]+/g, '-')}`, prompt_version: pv, kind: 'realB', case: h.case, term: req.term, system: sys, prompt: conflictsPrompt(req.body), body: req.body });
  }
  writeFileSync(`${R}real${SUF}_themes.json`, JSON.stringify(themes));
  writeFileSync(`${R}requests_real${SUF}.jsonl`, out.join('\n') + '\n');
  console.log(cases.length, 'cases,', histories.length, 'histories,', out.length, 'requests');
});
