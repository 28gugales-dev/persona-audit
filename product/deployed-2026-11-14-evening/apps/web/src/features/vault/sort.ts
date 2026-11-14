import { itemTermCounts } from '../activity/buildGraph';
import type { ActivityItem } from '../activity/types';
import { UPLOAD_SITE } from './migrate';

/**
 * The library sorting itself, with nothing but what's here: a few words that say
 * what each entry is about (TF-IDF over the whole library) and themes that group
 * entries by those words. No network and no randomness, so the same library always
 * sorts the same way. The related list on an open entry stays in links.ts.
 */

export interface ThemeCluster {
  /** The phrase that best stands for the group. Also how a name for it is remembered. */
  term: string;
  terms: string[];
  itemIds: string[];
}

export interface LibrarySort {
  tags: Map<string, string[]>;
  clusters: ThemeCluster[];
  /** Groups too small to show as themes. Two entries on one exact subject can still disagree, so Conflicts reads these too. */
  smaller: ThemeCluster[];
}

const VECTOR_TERMS = 14;
const TAGS = 4;
const THEME_LIMIT = 14;
const SMALLER_LIMIT = THEME_LIMIT * 4;
const NAME_CANDIDATES = 24;
// How close an entry must be to a theme's centre to join it. Tuned on short posts and long sections together.
const JOIN_AT = 0.16;
const MERGE_AT = 0.45;
/** A term in more entries than this says nothing about any one of them, as in links.ts. */
const COMMON_SHARE = 0.25;
const MIN_COMMON = 8;
/** A word in fewer entries than this share can't hold a theme together. */
const THEME_WORD_SHARE = 0.002;
/** Where an entry was put says what it's about, so sharing a place counts for about as much as three shared words. */
const PLACE_WEIGHT = 3;
const PLACE_PREFIX = 'place:';
/** Everything lands in these whatever it's about. */
const NOT_A_TOPIC = /^(documents?|downloads?|desktop|files?|misc|notes?|other|stuff|uploads?|untitled)$/i;
/** These sites file everything under their own name. */
const NO_PLACES = new Set(['chatgpt', 'claude', 'persona']);
const STEP_EVERY = 64;

type Vector = Map<string, number>;

/** The subreddit, course or forum it came from, or else the folder it sits in. */
function placeOf(entry: ActivityItem, folderOf: ReadonlyMap<string, string>): string | null {
  if (!NO_PLACES.has(entry.site) && entry.site !== UPLOAD_SITE && entry.subreddit) return `${PLACE_PREFIX}${entry.site}/${entry.subreddit.toLowerCase()}`;
  const folder = folderOf.get(entry.id);
  return folder && !NOT_A_TOPIC.test(folder) ? `${PLACE_PREFIX}${folder.toLowerCase()}` : null;
}

interface Cluster {
  center: Vector;
  normSq: number;
  /** How many members each term came from. */
  seen: Map<string, number>;
  itemIds: string[];
}

function addInto(cluster: Cluster, vector: Vector, seen?: Map<string, number>) {
  for (const [term, weight] of vector) {
    const was = cluster.center.get(term) ?? 0;
    const now = was + weight;
    cluster.center.set(term, now);
    cluster.normSq += now * now - was * was;
    cluster.seen.set(term, (cluster.seen.get(term) ?? 0) + (seen?.get(term) ?? 1));
  }
}

function similarity(a: Cluster, b: Cluster): number {
  const [small, large] = a.center.size < b.center.size ? [a, b] : [b, a];
  let dot = 0;
  for (const [term, weight] of small.center) dot += weight * (large.center.get(term) ?? 0);
  return dot / Math.sqrt(a.normSq * b.normSq || 1);
}

/** Average closeness of a group's members, from 0 to 1. Entries that say nearly the same words are about one exact subject. */
const tightness = (cluster: Cluster) => cluster.normSq / cluster.itemIds.length ** 2;

/** A theme's name should be said by most of its members and not by much else, with most of its members counting for more. */
function nameScore(term: string, members: number, size: number, df: ReadonlyMap<string, number>): number {
  const reach = members / size;
  const focus = members / (df.get(term) ?? 1);
  return ((5 * focus * reach) / (4 * focus + reach)) * (term.includes(' ') ? 1.3 : 1);
}

function named(clusters: readonly Cluster[], df: ReadonlyMap<string, number>, byId: ReadonlyMap<string, ActivityItem>, biggestFirst = true): ThemeCluster[] {
  const byLabel = new Map<string, ThemeCluster>();
  for (const cluster of clusters) {
    const members = cluster.itemIds.flatMap((id) => {
      const entry = byId.get(id);
      return entry ? [itemTermCounts(entry)] : [];
    });
    const ranked = [...cluster.center]
      .filter(([term]) => (cluster.seen.get(term) ?? 0) >= 2 && !term.startsWith(PLACE_PREFIX))
      .sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))
      .slice(0, NAME_CANDIDATES)
      .map(([term]) => [term, nameScore(term, members.filter((counts) => counts.has(term)).length, members.length, df)] as const)
      .sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))
      .map(([term]) => term);
    const term = ranked[0];
    if (!term) continue;
    const same = byLabel.get(term);
    if (same) same.itemIds.push(...cluster.itemIds);
    else byLabel.set(term, { term, terms: ranked.slice(0, 6), itemIds: [...cluster.itemIds] });
  }
  const groups = [...byLabel.values()];
  return biggestFirst ? groups.sort((a, b) => b.itemIds.length - a.itemIds.length || (a.term < b.term ? -1 : 1)) : groups;
}

/** One pass, oldest first, joining each entry to the closest group or starting its own. Biggest groups first; lone entries are left out. */
function* gather(ordered: readonly ActivityItem[], vectors: ReadonlyMap<string, Vector>): Generator<void, Cluster[]> {
  const clusters: Cluster[] = [];
  // Only themes sharing a word get compared, which is what keeps this near linear.
  const holders = new Map<string, Set<number>>();
  for (let i = 0; i < ordered.length; i++) {
    const entry = ordered[i]!;
    const vector = vectors.get(entry.id);
    if (!vector || vector.size === 0) continue;
    const dots = new Map<number, number>();
    for (const [term, weight] of vector) {
      for (const at of holders.get(term) ?? []) dots.set(at, (dots.get(at) ?? 0) + weight * (clusters[at]!.center.get(term) ?? 0));
    }
    let best = -1;
    let bestScore = JOIN_AT;
    for (const [at, dot] of dots) {
      const score = dot / Math.sqrt(clusters[at]!.normSq || 1);
      if (score > bestScore || (score === bestScore && at < best)) {
        best = at;
        bestScore = score;
      }
    }
    if (best < 0) {
      best = clusters.length;
      clusters.push({ center: new Map(), normSq: 0, seen: new Map(), itemIds: [] });
    }
    const cluster = clusters[best]!;
    addInto(cluster, vector);
    cluster.itemIds.push(entry.id);
    for (const term of vector.keys()) {
      let set = holders.get(term);
      if (!set) holders.set(term, (set = new Set()));
      set.add(best);
    }
    if (i % STEP_EVERY === 0) yield;
  }
  return clusters.filter((c) => c.itemIds.length >= 2).sort((a, b) => b.itemIds.length - a.itemIds.length || (a.itemIds[0]! < b.itemIds[0]! ? -1 : 1));
}

/** Yields whenever it's had a turn, so one caller can run it straight through and another can take breaths. */
function* sortSteps(entries: readonly ActivityItem[], folderOf: ReadonlyMap<string, string>): Generator<void, LibrarySort> {
  const total = entries.length;
  const df = new Map<string, number>();
  for (let i = 0; i < total; i++) {
    for (const term of itemTermCounts(entries[i]!).keys()) df.set(term, (df.get(term) ?? 0) + 1);
    const place = placeOf(entries[i]!, folderOf);
    if (place) df.set(place, (df.get(place) ?? 0) + 1);
    if (i % STEP_EVERY === 0) yield;
  }

  const ceiling = Math.max(MIN_COMMON, total * COMMON_SHARE);
  const shareFloor = Math.max(2, Math.ceil(total * THEME_WORD_SHARE));
  const tags = new Map<string, string[]>();
  const vectors = new Map<string, Vector>();
  const wordVectors = new Map<string, Vector>();
  for (let i = 0; i < total; i++) {
    const entry = entries[i]!;
    const scored: [string, number][] = [];
    for (const [term, tf] of itemTermCounts(entry)) {
      const shared = df.get(term)!;
      if (shared > ceiling) continue;
      // Said once and nowhere else is a stray word, not a topic.
      if (tf < 2 && shared < 2) continue;
      scored.push([term, (1 + Math.log(tf)) * Math.log(1 + total / shared) * (term.includes(' ') ? 1.5 : 1)]);
    }
    scored.sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1));
    const top = scored.slice(0, VECTOR_TERMS);

    const picked: string[] = [];
    const title = entry.title.toLowerCase();
    for (const [term] of top) {
      // Printed right beside the title, so repeating it says nothing.
      if (title.includes(term)) continue;
      // "moral" says nothing "moral luck" doesn't, and the reverse order is just as redundant.
      if (picked.some((p) => (p.includes(' ') && p.split(' ').includes(term)) || (term.includes(' ') && term.split(' ').includes(p)))) continue;
      picked.push(term);
      if (picked.length === TAGS) break;
    }
    if (picked.length > 0) tags.set(entry.id, picked);

    // Tags want what's rare, themes want what's shared. In a big library the rarest phrases fill the
    // top of the list and match almost nothing, which split every subject into crumbs, so themes
    // only look at words common enough to gather a group. The phrase bonus stays with tags and labels.
    const shareable = scored
      .filter(([term]) => df.get(term)! >= shareFloor)
      .map(([term, score]) => [term, term.includes(' ') ? score / 1.5 : score] as const)
      .sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))
      .slice(0, VECTOR_TERMS);
    const wordNorm = Math.sqrt(shareable.reduce((sum, [, w]) => sum + w * w, 0)) || 1;
    wordVectors.set(entry.id, new Map(shareable.map(([term, w]) => [term, w / wordNorm])));
    const place = placeOf(entry, folderOf);
    const shared = place ? df.get(place)! : 0;
    // A place nearly everything is in says as little as a word nearly everything uses.
    if (place && shared >= 2 && shared <= ceiling) shareable.push([place, PLACE_WEIGHT * Math.log(1 + total / shared)]);
    const norm = Math.sqrt(shareable.reduce((sum, [, w]) => sum + w * w, 0)) || 1;
    vectors.set(entry.id, new Map(shareable.map(([term, w]) => [term, w / norm])));
    if (i % STEP_EVERY === 0) yield;
  }

  // Oldest first, with id breaking ties, so the outcome depends on the library and not on how it was listed.
  const ordered = [...entries].sort((a, b) => a.createdUtc - b.createdUtc || (a.id < b.id ? -1 : 1));
  const clusters = yield* gather(ordered, vectors);

  // One pass splits what a better order would have kept together, so close themes get a second look.
  const kept: Cluster[] = [];
  for (const cluster of clusters.slice(0, THEME_LIMIT * 4)) {
    const home = kept.find((other) => similarity(other, cluster) >= MERGE_AT);
    if (!home) {
      kept.push(cluster);
      continue;
    }
    addInto(home, cluster.center, cluster.seen);
    home.itemIds.push(...cluster.itemIds);
    yield;
  }

  // Entries left in a crumb that didn't make the cut still belong somewhere. The centres hold still here, so order can't matter.
  const shown = kept.slice(0, THEME_LIMIT);
  const placed = new Set(shown.flatMap((cluster) => cluster.itemIds));
  for (let i = 0; i < ordered.length; i++) {
    const entry = ordered[i]!;
    if (placed.has(entry.id)) continue;
    const vector = vectors.get(entry.id);
    if (!vector || vector.size === 0) continue;
    let best: Cluster | null = null;
    let bestScore = JOIN_AT;
    for (const cluster of shown) {
      let dot = 0;
      for (const [term, weight] of vector) dot += weight * (cluster.center.get(term) ?? 0);
      const score = dot / Math.sqrt(cluster.normSq || 1);
      if (score > bestScore) {
        best = cluster;
        bestScore = score;
      }
    }
    best?.itemIds.push(entry.id);
    if (i % STEP_EVERY === 0) yield;
  }

  // Going by words alone finds entries on one exact subject that their places pulled into different themes.
  const themeOf = new Map(shown.flatMap((cluster) => cluster.itemIds.map((id) => [id, cluster] as const)));
  const close = yield* gather(ordered, wordVectors);
  const smaller = close
    .filter((group) => new Set(group.itemIds.map((id) => themeOf.get(id))).size > 1 || !themeOf.has(group.itemIds[0]!))
    .sort((a, b) => tightness(b) - tightness(a) || (a.itemIds[0]! < b.itemIds[0]! ? -1 : 1))
    .slice(0, SMALLER_LIMIT);

  const byId = new Map(entries.map((entry) => [entry.id, entry]));
  return { tags, clusters: named(shown, df, byId).slice(0, THEME_LIMIT), smaller: named(smaller, df, byId, false) };
}

const NO_FOLDERS: ReadonlyMap<string, string> = new Map();

export function sortLibrary(entries: readonly ActivityItem[], folderOf = NO_FOLDERS): LibrarySort {
  const steps = sortSteps(entries, folderOf);
  for (;;) {
    const step = steps.next();
    if (step.done) return step.value;
  }
}

const BREATH_MS = 8;
let lastBreath = 0;

/** Hands the page back for a frame once a slice of work has run long. Cheap to call often. */
export async function breathe(): Promise<void> {
  const now = performance.now();
  if (now - lastBreath < BREATH_MS) return;
  await new Promise((resolve) => setTimeout(resolve));
  lastBreath = performance.now();
}

/** The same result in small slices, so a big library never stalls the page. Null if told to stop. */
export async function sortLibraryGently(entries: readonly ActivityItem[], signal: AbortSignal, folderOf = NO_FOLDERS): Promise<LibrarySort | null> {
  const steps = sortSteps(entries, folderOf);
  for (;;) {
    if (signal.aborted) return null;
    const step = steps.next();
    if (step.done) return step.value;
    await breathe();
  }
}
