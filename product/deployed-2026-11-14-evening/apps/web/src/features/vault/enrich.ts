import { PERSONA_ENRICH_LIMITS as LIMITS, type PersonaEnrichBody, type PersonaEnrichRes } from '@amphi/contract';
import { extractKeywords } from '../activity/buildGraph';
import type { ActivityItem } from '../activity/types';
import { env } from '../../lib/env';
import { UPLOAD_SITE } from './migrate';
import { contentHash } from './sections';
import type { ThemeCluster } from './sort';
import type { VaultNote } from './types';

/**
 * The optional step: better labels from a model, for those who said yes. This file
 * is the gate on what leaves the browser. `enrichCandidates` is the only thing that
 * picks text to send: excerpts of uploaded documents and of notes, never an item the
 * extension collected, and never a note's title, which can repeat a collected title.
 * Every answer is cached here by the hash of what was sent, so nothing goes twice.
 */

export const CONSENT_KEY = 'enrich-consent';
export const CACHE_KEY = 'enriched';

export const EXCERPT_CHARS = 500;
const MIN_EXCERPT_CHARS = 40;
/** The server allows 10 requests a minute. */
export const PACE_MS = 6_500;
/** One visit's worth, so a huge library works through over a few sittings rather than all at once. */
export const SESSION_ITEMS = 1_000;
const MIN_NAMED_MEMBERS = 2;
/** A note still being written would be sent again with every change. */
export const SETTLED_MS = 2 * 60_000;
const REQUEST_TIMEOUT_MS = 30_000;

export interface Enrichment {
  title?: string;
  summary?: string;
  tags?: string[];
}

export interface EnrichCache {
  /** By hash of the excerpt. An empty record means the model had nothing to say, so it isn't asked again. */
  items: Record<string, Enrichment>;
  /** By the local label of the theme. */
  names: Record<string, string>;
}

export const EMPTY_CACHE: EnrichCache = { items: {}, names: {} };

export function parseCache(raw: unknown): EnrichCache {
  if (typeof raw !== 'object' || raw === null) return EMPTY_CACHE;
  const { items, names } = raw as Partial<EnrichCache>;
  return {
    items: typeof items === 'object' && items !== null ? (items as EnrichCache['items']) : {},
    names: typeof names === 'object' && names !== null ? (names as EnrichCache['names']) : {},
  };
}

/** What may be sent of a body. Quotes and [[links]] go first: "Write about this" pastes a collected post into a note that way. */
export function excerptOf(body: string, chars = EXCERPT_CHARS): string {
  return body
    .split('\n')
    .filter((line) => !line.trimStart().startsWith('>'))
    .join('\n')
    .replace(/\[\[[^\]\n]*\]\]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, chars);
}

const hashes = new WeakMap<ActivityItem, string>();

/** The cache key for an entry, stable for as long as its opening doesn't change. */
export function excerptHash(entry: ActivityItem): string {
  let hash = hashes.get(entry);
  if (!hash) {
    hash = contentHash(excerptOf(entry.body));
    hashes.set(entry, hash);
  }
  return hash;
}

export interface Candidate {
  /** The entry it came from, on this side only: the hash is what goes out as its id. */
  entryId: string;
  hash: string;
  text: string;
}

/**
 * Everything allowed to be sent. Documents are picked out of `imported` and not the
 * merged library, and anything sharing an id with what the extension sent is out,
 * so a collected item can't get in by any route. First sections go first, as they
 * say the most per excerpt.
 */
export function enrichCandidates(notes: readonly VaultNote[], imported: readonly ActivityItem[], collectedIds: ReadonlySet<string>, now = Date.now()): Candidate[] {
  const of = (entryId: string, body: string): Candidate | null => {
    const text = excerptOf(body);
    return text.length < MIN_EXCERPT_CHARS ? null : { entryId, hash: contentHash(text), text };
  };
  const docs = imported.filter((item) => item.site === UPLOAD_SITE && item.id.startsWith('doc_') && !collectedIds.has(item.id));
  const firsts = docs.filter((item) => item.id.endsWith('_0'));
  const rest = docs.filter((item) => !item.id.endsWith('_0'));
  const settled = notes.filter((note) => now - note.updatedAt >= SETTLED_MS);
  return [
    ...firsts.map((item) => of(item.id, item.body)),
    ...settled.map((note) => of(note.id, note.body)),
    ...rest.map((item) => of(item.id, item.body)),
  ].filter((c): c is Candidate => c !== null);
}

/** What's left to ask about, in batches the server will take. Nothing already answered, nothing twice. */
export function nextBatches(candidates: readonly Candidate[], cache: EnrichCache, limit = SESSION_ITEMS): PersonaEnrichBody[] {
  const seen = new Set<string>();
  const fresh = candidates.filter((c) => {
    if (c.hash in cache.items || seen.has(c.hash)) return false;
    seen.add(c.hash);
    return true;
  });
  const batches: PersonaEnrichBody[] = [];
  const kept = fresh.slice(0, limit);
  for (let i = 0; i < kept.length; i += LIMITS.items) {
    batches.push({ items: kept.slice(i, i + LIMITS.items).map((c) => ({ id: c.hash, text: c.text })), clusters: [] });
  }
  return batches;
}

const asEntry = (candidate: Candidate): ActivityItem => ({
  id: candidate.entryId,
  kind: 'note',
  site: UPLOAD_SITE,
  subreddit: '',
  title: '',
  body: candidate.text,
  permalink: '',
  createdUtc: 1,
  score: 0,
  parentId: null,
  linkId: null,
  source: 'live',
  philosophy: false,
});

export interface NameRequest {
  /** Sent as the id. */
  id: string;
  /** The theme's label, where the answer is remembered. */
  term: string;
  terms: string[];
}

/**
 * Themes worth naming. Terms come from the same excerpts that may be sent, never
 * from the theme's own word list, which also counts what the extension collected. A
 * theme that's mostly collected items keeps the label it has.
 */
export function nameRequests(clusters: readonly ThemeCluster[], candidates: readonly Candidate[], cache: EnrichCache): NameRequest[] {
  const byId = new Map(candidates.map((c) => [c.entryId, c]));
  const out: NameRequest[] = [];
  for (const cluster of clusters) {
    if (cluster.term in cache.names) continue;
    const mine = cluster.itemIds.flatMap((id) => byId.get(id) ?? []);
    if (mine.length < MIN_NAMED_MEMBERS || mine.length * 2 < cluster.itemIds.length) continue;
    // Words at least two of them share, since a phrase from just one says nothing about the group.
    const terms = extractKeywords(mine.map(asEntry), LIMITS.clusterTerms, 2)
      .map((k) => k.term)
      .filter((term) => term.length <= LIMITS.termChars);
    if (terms.length > 0) out.push({ id: `c${out.length}`, term: cluster.term, terms });
    if (out.length === LIMITS.clusters) break;
  }
  return out;
}

export function mergeAnswer(cache: EnrichCache, sent: PersonaEnrichBody, res: PersonaEnrichRes, named: readonly NameRequest[] = []): EnrichCache {
  const items = { ...cache.items };
  for (const item of sent.items) items[item.id] = {};
  for (const answer of res.items) {
    if (!(answer.id in items)) continue;
    items[answer.id] = { title: answer.title || undefined, summary: answer.summary || undefined, tags: answer.tags };
  }
  const names = { ...cache.names };
  for (const answer of res.clusters) {
    const request = named.find((n) => n.id === answer.id);
    if (request) names[request.term] = answer.name;
  }
  return { items, names };
}

/**
 * Null on anything but a clean answer, and the caller just stops: the person keeps
 * the local result and sees no error. Goes around `call()`, which demands a sign-in
 * for every POST, and sends no token or cookie, so the server sees only an address.
 */
export async function postEnrich(body: PersonaEnrichBody, signal: AbortSignal): Promise<PersonaEnrichRes | null> {
  const stop = new AbortController();
  const abort = () => stop.abort();
  const timer = setTimeout(abort, REQUEST_TIMEOUT_MS);
  signal.addEventListener('abort', abort, { once: true });
  try {
    const res = await fetch(`${env.apiUrl}/persona/enrich`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      credentials: 'omit',
      body: JSON.stringify(body),
      signal: stop.signal,
    });
    if (!res.ok) return null;
    const data = (await res.json()) as PersonaEnrichRes;
    return Array.isArray(data.items) && Array.isArray(data.clusters) ? data : null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
    signal.removeEventListener('abort', abort);
  }
}
