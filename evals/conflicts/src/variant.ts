import { CONFLICTS_SYSTEM } from './shipped';

/** The one-line prompt fix, written 2026-11-14 after seeing signalled changes of mind missed in histories t00-t11,
 * before any run on t12-t23, the reversals or the hand-written decoys (the held-out evaluation). */
export const FIX_LINE =
  'A change of mind still counts: if a later excerpt asserts, as their current view, something that cannot stand with what an earlier excerpt asserted, include the pair even when they say they have changed their mind.';

export const CONFLICTS_SYSTEM_FIXED = CONFLICTS_SYSTEM.replace(
  'Count a pair only when the person asserts both as their own view, on the same point, and they clash.',
  `Count a pair only when the person asserts both as their own view, on the same point, and they clash. ${FIX_LINE}`,
);
if (CONFLICTS_SYSTEM_FIXED === CONFLICTS_SYSTEM) throw new Error('fix line not inserted');
