// PLAN v41: the path records over 124 posts take today. Each round-40 long history (realtext_histories*L.json) run through the
// shipped word-theme sort, conflictRequests (20 excerpts a theme) and affordable() with a full week's 300 chats, as a first look;
// system prompt = Persona's current one (depNoCap, identical to main's CONFLICTS_SYSTEM).
// Writes paper/results/requests_v41_themes.jsonl and haiku_in/<id>.txt. Run: npx vitest run src/longthemes.test.ts
import { test } from 'vitest';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { sortLibrary } from '../../../apps/web/src/features/vault/sort';
import { conflictRequests, affordable } from '../../../apps/web/src/features/vault/conflicts';
import { conflictsPrompt } from '../../../apps/api/src/features/persona/conflicts';
import type { ActivityItem } from '../../../apps/web/src/features/activity/types';

const R = '../../paper/results/';
interface Post { id: string; body: string; createdUtc: number; role: string }
const asItem = (p: Post): ActivityItem => ({ id: p.id, kind: 'comment', site: 'reddit', subreddit: 'philosophy', title: '', body: p.body, permalink: '', createdUtc: p.createdUtc, score: 1, parentId: null, linkId: null, source: 'backlog', philosophy: true });

test('longthemes', () => {
  const sys = JSON.parse(readFileSync('gen/real_prompts.json', 'utf8')).depNoCap as string;
  const out: string[] = []; const stats: string[] = [];
  for (const suf of ['', '2', '3', '4', '5', '6']) {
    const f = `../../paper/data/realtext_histories${suf}L.json`;
    if (!existsSync(f)) continue;
    for (const h of JSON.parse(readFileSync(f, 'utf8')) as { case: string; posts: Post[] }[]) {
      const entries = h.posts.map(asItem);
      const byId = new Map(entries.map((e) => [e.id, e]));
      const sorted = sortLibrary(entries);
      const groups = [...sorted.smaller, ...sorted.clusters].map((g) => ({ term: g.term, label: g.term, itemIds: g.itemIds }));
      const all = conflictRequests(groups, byId, {});
      const reqs = affordable(all, 300);
      const seen = new Set<string>();
      for (const req of reqs) {
        let id = `v41t:realB:${h.case}:${req.term.replace(/[^\w-]+/g, '-')}`;
        while (seen.has(id)) id += '_'; seen.add(id);
        const prompt = conflictsPrompt(req.body);
        out.push(JSON.stringify({ id, prompt_version: 'depNoCap', kind: 'realB', case: h.case, term: req.term, system: sys, prompt, body: req.body }));
        writeFileSync(`${R}haiku_in/${id.replaceAll(':', '__')}.txt`, `=== SYSTEM PROMPT ===\n${sys}\n\n=== USER MESSAGE ===\n${prompt}\n`);
      }
      stats.push(`${h.case} ${h.posts.length} posts, ${all.length} themes, ${reqs.length} sent`);
    }
  }
  writeFileSync(`${R}requests_v41_themes.jsonl`, out.join('\n') + '\n');
  console.log(stats.join('\n'), '\n', out.length, 'requests');
});
