// Runs the shipped Persona pipeline, unmodified, on every history in paper/data/histories.json:
// theme sort -> on-device detector -> the requests the opt-in model step would send.
// Writes paper/results/{local,themes}.json and paper/results/requests.jsonl (one model request per line,
// with the exact system prompt and user prompt), plus oracle requests (one per planted item).
import { test } from 'vitest';
import { readFileSync, writeFileSync } from 'node:fs';
import { sortLibrary } from '../../../apps/web/src/features/vault/sort';
import { findLocalConflicts } from '../../../apps/web/src/features/vault/localConflicts';
import { conflictRequests, conflictKind } from '../../../apps/web/src/features/vault/conflicts';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import { CONFLICTS_SYSTEM } from './shipped';
import type { ActivityItem } from '../../../apps/web/src/features/activity/types';

const DATA = '../../paper/data';
const OUT = '../../paper/results';
interface Post { id: string; body: string; createdUtc: number; role: string; item: string | null }
interface History { set: string; history: string; posts: Post[] }

const asItem = (p: Post): ActivityItem => ({ id: p.id, kind: 'comment', site: 'reddit', subreddit: 'philosophy', title: '', body: p.body, permalink: '', createdUtc: p.createdUtc, score: 1, parentId: null, linkId: null, source: 'backlog', philosophy: true });

test('pipeline', () => {
  const histories: History[] = JSON.parse(readFileSync(`${DATA}/histories.json`, 'utf8'));
  const local: Record<string, unknown[]> = {};
  const themes: Record<string, { term: string; itemIds: string[] }[]> = {};
  const kinds: Record<string, string> = {};
  const lines: string[] = [];
  for (const h of histories) {
    const entries = h.posts.map(asItem);
    const byId = new Map(entries.map((e) => [e.id, e]));
    const sorted = sortLibrary(entries);
    const groups = [...sorted.smaller, ...sorted.clusters].map((c) => ({ term: c.term, label: c.term, itemIds: c.itemIds }));
    themes[h.history] = groups.map((g) => ({ term: g.term, itemIds: g.itemIds }));
    local[h.history] = findLocalConflicts(entries, groups);
    for (const req of conflictRequests(groups, byId, {})) {
      lines.push(JSON.stringify({ id: `${h.history}:${req.term}`, kind: 'pipeline', set: h.set, history: h.history, system: CONFLICTS_SYSTEM, prompt: conflictsPrompt(req.body), body: req.body }));
    }
    // Oracle: the planted item's own posts as one theme, so model recall is measured with grouping out of the way.
    const items = [...new Set(h.posts.filter((p) => p.item).map((p) => p.item!))];
    for (const item of items) {
      const mine = h.posts.filter((p) => p.item === item).map(asItem);
      const a = byId.get(`${item}_a`)!;
      const b = byId.get(`${item}_b`)!;
      kinds[item] = conflictKind(a, b);
      const [req] = conflictRequests([{ term: item, label: 'philosophy', itemIds: mine.map((m) => m.id) }], byId, {});
      // Bypass of the 60-character excerpt filter, so the model itself is measured on every hand-written item.
      if (h.set === 'adversarial') {
        const body = { theme: 'philosophy', excerpts: [a, b].map((e) => ({ id: e.id, when: new Date(e.createdUtc * 1000).toISOString().slice(0, 7), text: e.body.slice(0, 400) })) };
        lines.push(JSON.stringify({ id: `${h.history}:direct:${item}`, kind: 'direct', set: h.set, history: h.history, item, system: CONFLICTS_SYSTEM, prompt: conflictsPrompt(body), body }));
      }
      if (req) lines.push(JSON.stringify({ id: `${h.history}:oracle:${item}`, kind: 'oracle', set: h.set, history: h.history, item, system: CONFLICTS_SYSTEM, prompt: conflictsPrompt(req.body), body: req.body }));
    }
  }
  writeFileSync(`${OUT}/local.json`, JSON.stringify(local, null, 0));
  writeFileSync(`${OUT}/themes.json`, JSON.stringify(themes, null, 0));
  writeFileSync(`${OUT}/kinds.json`, JSON.stringify(kinds, null, 0));
  writeFileSync(`${OUT}/requests.jsonl`, lines.join('\n') + '\n');
  console.log(histories.length, 'histories,', lines.length, 'requests');
});
