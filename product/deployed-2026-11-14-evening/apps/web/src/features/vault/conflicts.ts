import { PERSONA_CONFLICT_LIMITS as LIMITS, PERSONA_CONFLICT_OUT, type PersonaConflictsBody, type PersonaConflictsRes } from '@amphi/contract';
import { ApiError, call } from '../../lib/api';
import { isPersonaDemo } from '../../lib/personaDemo';
import type { ActivityItem } from '../activity/types';
import { excerptOf } from './enrich';
import { isWritten } from './profile';
import type { LocalConflict } from './localConflicts';
import { contentHash } from './sections';
import { siteDisplayName } from '../activity/copy';

/**
 * Where someone's writing disagrees with itself, found by a model for those who
 * said yes. A separate yes from better titles and tags, because this one also sends
 * what the extension collected. `conflictRequests` picks what leaves the browser,
 * and only the person's own words: never clips or saved posts, never quoted lines.
 */

export const CONFLICT_CONSENT_KEY = 'conflicts-consent';
export const CONFLICTS_KEY = 'conflicts';

const MIN_EXCERPT_CHARS = 60;
const REQUEST_TIMEOUT_MS = 55_000;
/** Per theme, once a history is too big to send whole. */
const THEME_EXCERPTS = 20;
/** The `asked` key for a whole-history request. */
export const WHOLE = '*';
const WHOLE_LABEL = 'Everything you wrote';

export type Verdict = 'first' | 'second' | 'both' | 'none';

export interface Conflict {
  /** The two entries, sorted, so finding a pair twice can't make two conflicts. */
  id: string;
  a: string;
  b: string;
  theme: string;
  tension: string;
  verdict?: Verdict;
  why?: string;
  /** Found on this device. Until answered it's replaced by each new look. */
  local?: true;
}

export interface ConflictStore {
  conflicts: Conflict[];
  /** What each theme last sent, so a theme that hasn't changed isn't sent again. */
  asked: Record<string, string>;
}

export const NO_CONFLICTS: ConflictStore = { conflicts: [], asked: {} };

const VERDICTS: readonly unknown[] = ['first', 'second', 'both', 'none'];

export function parseConflictStore(raw: unknown): ConflictStore {
  if (typeof raw !== 'object' || raw === null) return NO_CONFLICTS;
  const { conflicts, asked } = raw as Partial<ConflictStore>;
  return {
    conflicts: (Array.isArray(conflicts) ? conflicts : []).filter(
      (c): c is Conflict =>
        typeof c?.id === 'string' && typeof c.a === 'string' && typeof c.b === 'string' && typeof c.theme === 'string' && typeof c.tension === 'string' && (c.verdict === undefined || VERDICTS.includes(c.verdict)),
    ),
    asked: typeof asked === 'object' && asked !== null ? (asked as Record<string, string>) : {},
  };
}

export interface ThemeForConflicts {
  term: string;
  label: string;
  itemIds: string[];
}

export interface ConflictRequest {
  term: string;
  signature: string;
  body: PersonaConflictsBody;
}

/** Evenly across a theme's history: a conflict needs the old writing as well as the new. */
function spread<T>(list: readonly T[], count: number): T[] {
  if (list.length <= count) return [...list];
  return Array.from({ length: count }, (_, i) => list[Math.round((i * (list.length - 1)) / (count - 1))]!);
}

/** The person's own sendable writing among `ids`, oldest first. */
function sendable(ids: Iterable<string>, byId: ReadonlyMap<string, ActivityItem>) {
  return [...ids]
    .flatMap((id) => {
      const entry = byId.get(id);
      if (!entry || !isWritten(entry)) return [];
      const text = excerptOf(entry.body, LIMITS.excerptChars);
      return text.length < MIN_EXCERPT_CHARS || entry.id.length > LIMITS.excerptId ? [] : [{ entry, text }];
    })
    .sort((x, y) => x.entry.createdUtc - y.entry.createdUtc || (x.entry.id < y.entry.id ? -1 : 1));
}

const asExcerpts = (mine: ReturnType<typeof sendable>) =>
  mine.map(({ entry, text }) => ({ id: entry.id, when: new Date(entry.createdUtc * 1000).toISOString().slice(0, 7), text }));

/**
 * What to ask on the next look. A history that fits in one request goes whole: an old
 * view and the one that replaced it rarely share words, so themes split them apart
 * (the eval in paper/ found word themes joined 0 of 19 real reversals).
 */
export function lookRequests(themes: readonly ThemeForConflicts[], byId: ReadonlyMap<string, ActivityItem>, asked: ConflictStore['asked']): ConflictRequest[] {
  const mine = asExcerpts(sendable(byId.keys(), byId));
  if (mine.length > LIMITS.excerpts) return conflictRequests(themes, byId, asked);
  if (mine.length < 2) return [];
  // Each post gets an equal share of the request, so a full history still goes whole.
  const share = Math.floor((LIMITS.totalChars - WHOLE_LABEL.length) / mine.length);
  const excerpts = mine.map((e) => ({ ...e, text: e.text.slice(0, share) }));
  const signature = contentHash(excerpts.map((e) => e.id).join('|'));
  return asked[WHOLE] === signature ? [] : [{ term: WHOLE, signature, body: { theme: WHOLE_LABEL, excerpts } }];
}

export function conflictRequests(themes: readonly ThemeForConflicts[], byId: ReadonlyMap<string, ActivityItem>, asked: ConflictStore['asked']): ConflictRequest[] {
  const out: ConflictRequest[] = [];
  for (const theme of themes) {
    const excerpts = asExcerpts(spread(sendable(theme.itemIds, byId), THEME_EXCERPTS));
    if (excerpts.length < 2) continue;
    const signature = contentHash(excerpts.map((e) => e.id).join('|'));
    if (asked[theme.term] === signature) continue;
    out.push({ term: theme.term, signature, body: { theme: theme.label.slice(0, LIMITS.themeChars), excerpts } });
  }
  return out;
}

/** What the pool can cover, in order. A group too big for what's left is passed over, not the smaller ones after it. */
export function affordable(requests: readonly ConflictRequest[], chats: number): ConflictRequest[] {
  let left = chats;
  return requests.filter(({ body }) => {
    if (body.excerpts.length > left) return false;
    left -= body.excerpts.length;
    return true;
  });
}

/** New pairs join; anything already found keeps its verdict. A whole-history pair files under a theme that holds it. */
export function mergeFound(store: ConflictStore, request: ConflictRequest, res: Pick<PersonaConflictsRes, 'conflicts'>, themes: readonly ThemeForConflicts[] = []): ConflictStore {
  const known = new Set(store.conflicts.map((c) => c.id));
  const added: Conflict[] = [];
  for (const { a, b, tension } of res.conflicts) {
    const id = [a, b].sort().join('|');
    if (known.has(id)) continue;
    known.add(id);
    const theme = request.term === WHOLE ? (themes.find((t) => t.itemIds.includes(b) || t.itemIds.includes(a))?.label ?? request.body.theme) : request.body.theme;
    added.push({ id, a, b, theme, tension });
  }
  return { conflicts: [...store.conflicts, ...added], asked: { ...store.asked, [request.term]: request.signature } };
}

/**
 * What the browser found on its own, under the theme that holds the newer entry.
 * Its unanswered finds from before go unless found again; answered ones stay.
 * Same store back when nothing changed.
 */
export function mergeLocal(store: ConflictStore, found: readonly LocalConflict[], themes: readonly ThemeForConflicts[]): ConflictStore {
  const ids = new Set(found.map(({ a, b }) => [a, b].sort().join('|')));
  const kept = store.conflicts.filter((c) => !c.local || c.verdict || ids.has(c.id));
  const known = new Set(kept.map((c) => c.id));
  const added: Conflict[] = [];
  for (const { a, b, subject } of found) {
    const id = [a, b].sort().join('|');
    if (known.has(id)) continue;
    known.add(id);
    const theme = themes.find((t) => t.itemIds.includes(b))?.label ?? subject;
    added.push({ id, a, b, theme, tension: `Where do you stand on ${subject}?`, local: true });
  }
  return added.length > 0 || kept.length < store.conflicts.length ? { ...store, conflicts: [...kept, ...added] } : store;
}

/** Older first, so "the first" and "the second" always mean then and now. */
export function inOrder(conflict: Conflict, byId: ReadonlyMap<string, ActivityItem>): [ActivityItem, ActivityItem] | null {
  const a = byId.get(conflict.a);
  const b = byId.get(conflict.b);
  if (!a || !b) return null;
  return a.createdUtc <= b.createdUtc ? [a, b] : [b, a];
}

export type ConflictKind = 'shift' | 'live';

/** A year apart is long enough to call it a change of mind even with nothing in the words saying so. */
const SHIFT_DAYS = 365;
const REVISED = /\b(?:used to|no longer|any ?more|changed my mind|came to (?:think|believe|see)|(?:'ve|have) come to|i was wrong|was (?:a|my) mistake|for (?:far |much )?too long|once (?:thought|believed)|back then|stopped believing|now i (?:think|believe|see)|i now (?:think|believe|see))\b/i;

/**
 * Decided by code, never by a model: a change of mind is growth and a live tension
 * is a question, so the card must not drift between the two. `first` is the older.
 */
export function conflictKind(first: ActivityItem, second: ActivityItem): ConflictKind {
  const days = Math.abs(second.createdUtc - first.createdUtc) / 86_400;
  return days >= SHIFT_DAYS || REVISED.test(second.body.replace(/[‘’]/g, "'")) ? 'shift' : 'live';
}

/** `out` when the pool can't cover this, null on any other failure. The demo's guard is here too: sample text never reaches the model. */
export async function postConflicts(body: PersonaConflictsBody, signal: AbortSignal): Promise<PersonaConflictsRes | 'out' | null> {
  if (isPersonaDemo()) return null;
  try {
    return await call('POST /persona/conflicts', { body, signal, timeoutMs: REQUEST_TIMEOUT_MS });
  } catch (err) {
    return err instanceof ApiError && err.message === PERSONA_CONFLICT_OUT ? 'out' : null;
  }
}

export type ConflictStatus = 'open' | 'settled';

/** Changes of mind are only the ones the person settled as such: a pair found by the app is a question until they answer it. */
export const changedViews = (settled: readonly ShownConflict[]) => settled.filter(({ conflict }) => conflict.verdict === 'second');

export interface ConflictFilter {
  query: string;
  status: ConflictStatus | null;
  theme: string | null;
}

/** A conflict with the two entries it joins, as the screen holds it. */
export interface ShownConflict {
  conflict: Conflict;
  first: ActivityItem;
  second: ActivityItem;
}

/** Searches what's on the card: the question, its theme, and both excerpts with where they came from. */
export function filterConflicts(list: readonly ShownConflict[], { query, status, theme }: ConflictFilter): ShownConflict[] {
  const q = query.trim().toLowerCase();
  return list.filter(({ conflict, first, second }) => {
    if (theme !== null && conflict.theme !== theme) return false;
    if (status !== null && (status === 'settled') !== Boolean(conflict.verdict)) return false;
    return !q || [conflict.tension, conflict.theme, first.body, second.body, siteDisplayName(first.site), siteDisplayName(second.site)].some((text) => text.toLowerCase().includes(q));
  });
}
