import type { UserRef } from './domain';

/**
 * Persona, the notebook the browser extension fills. The notebook lives in the
 * browser; these are the only shapes that reach the server, and only when the
 * member publishes them for their friends.
 */

export interface PersonaSharedNote {
  id: string;
  title: string;
  /** Markdown, with [[links]] and #tags. */
  body: string;
  /** ISO. */
  updatedAt: string;
}

export interface PersonaTopic {
  term: string;
  /** How many of the member's notes and items mention it. */
  count: number;
}

export interface PersonaSnapshot {
  notes: PersonaSharedNote[];
  topics: PersonaTopic[];
  /** Totals only: how big the notebook is, never what is in it. */
  counts: { notes: number; items: number };
}

export const PERSONA_LIMITS = {
  notes: 100,
  noteId: 64,
  noteTitle: 200,
  noteBody: 10_000,
  topics: 24,
  topicTerm: 60,
} as const;

export interface PersonaShare {
  snapshot: PersonaSnapshot | null;
  updatedAt: string | null;
}

export interface FriendPersona extends PersonaShare {
  user: UserRef;
}

export interface FriendInvite {
  code: string;
  /** ISO. */
  expiresAt: string;
}

export interface FriendInvitePreview {
  inviter: UserRef;
}

/**
 * Optional tidying for what someone uploaded, sent only after they opt in. Excerpts
 * of their documents and notes, never anything the extension collected. The server
 * keeps none of it; the browser caches the answers by content hash.
 */
export const PERSONA_ENRICH_LIMITS = {
  items: 20,
  itemId: 40,
  itemChars: 600,
  clusters: 8,
  clusterTerms: 8,
  termChars: 40,
  /** All text in one request, which with the output cap bounds what one call can cost. */
  totalChars: 14_000,
  title: 80,
  summary: 160,
  tags: 4,
  tag: 30,
  clusterName: 40,
} as const;

export const PERSONA_CONFLICT_LIMITS = {
  /** A whole history goes in one request up to this many posts; past that, themes go in 20 at a time. paper/ round 41: on 30 records of 166-244 posts, whole at 1,000 characters found 28 changes of mind, word themes 2, with fewer false cards (0.67 vs 0.87 per record). */
  excerpts: 244,
  excerptId: 80,
  /** At 400 the words that changed often fell past the cut (paper/ v18b: Godwin, James); a full history is trimmed to share totalChars. */
  excerptChars: 1_000,
  themeChars: 60,
  /** All text in one request, which with the output cap bounds what one call can cost. 244 posts x 1,000: shorter cuts on long records cost recall (paper/ round 40). */
  totalChars: 244_000,
  found: 8,
  tension: 180,
} as const;

/** One theme's excerpts. Only ever sent after the member turned conflicts on. */
export interface PersonaConflictsBody {
  theme: string;
  excerpts: { id: string; when: string; text: string }[];
}

/** What one account can send to the model each window. A chat counts every time it is sent. */
export const PERSONA_CONFLICT_ALLOWANCE = { chats: 300, days: 7, resets: 2 } as const;

/** The 429 for a request the pool can't cover: nothing is wrong, it has just run out. */
export const PERSONA_CONFLICT_OUT = 'conflict_allowance_out';

export interface PersonaConflictAllowance {
  left: number;
  total: number;
  /** When the pool fills again. Null while it hasn't been touched this window. */
  refillsAt: string | null;
  /** Free resets this account still has. */
  resets: number;
}

export interface PersonaConflictsRes {
  conflicts: { a: string; b: string; tension: string }[];
  allowance: PersonaConflictAllowance;
}

export interface PersonaEnrichBody {
  items: { id: string; text: string }[];
  /** A group of documents, described only by words from those documents' excerpts. */
  clusters: { id: string; terms: string[] }[];
}

export interface PersonaEnrichRes {
  items: { id: string; title: string; summary: string; tags: string[] }[];
  clusters: { id: string; name: string }[];
}
