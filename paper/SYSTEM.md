# System description (for the paper's Methods; every fact here traces to a file or commit)

**Persona** is part of Amphi (amphi-forum.org). A browser extension and uploads bring in a person's own writing: Reddit posts and comments, AI-chat exports, notes and documents (extension: 508d2c39, 2026-11-01; library: b6a64cf7, 11-01).

## Pipeline as shipped (code paths)

1. **Theme sort**, on device, deterministic.
   - TF-IDF terms per entry, with the place (subreddit/folder) weighted like three shared words.
   - Entries are grouped into at most 14 themes, plus up to 56 smaller groups that cut across themes.
   - Code: `apps/web/src/features/vault/sort.ts` (`sortLibrary`; JOIN_AT 0.16, MERGE_AT 0.45).
2. **On-device conflict finder**: no model, nothing sent.
   - Cuts entries into short claims (3-32 words, up to 12 per entry).
   - Drops questions, sarcasm, hypotheticals, and reported speech about another person. Hedged claims count less.
   - Pairs claims about the same subject (IDF-weighted overlap, compound-word check) with opposite verdicts (positive/negative word lexicons, negation within 3 words, "I used to think" flips).
   - Scores each pair, discounting pairs less than 30 days apart, and keeps up to 60.
   - Code: `apps/web/src/features/vault/localConflicts.ts` (c86449aa, 2026-11-07).
3. **Opt-in model step**: separate consent, weekly allowance of 300 excerpts with 2 resets (1c3aa3ba, 882ba4fc, 11-01).
   - Per theme, up to 20 of the person's own excerpts (400 chars each, 8,200 chars total) are sent, spread evenly over time, under aliases E1..En.
   - Production prompt `CONFLICTS_SYSTEM`: "Count a pair only when the person asserts both as their own view... Do not count: different points, questions/doubt, more careful wording, someone else's view, jokes... Return at most 3 pairs". Each pair comes with a one-line neutral question ("tension").
   - The model is Claude Haiku 5.5 (effort medium) when a key is set (9cba2eba, 11-01).
   - Ids are checked against what was sent, and a question with a label in it is replaced (f8ed24fd).
   - Code: `apps/api/src/features/persona/conflicts.ts` (e2378d80, 11-01); request builder `conflictRequests` in `apps/web/src/features/vault/conflicts.ts`.
4. **Card**, built during the sprint.
   - Each pair is labelled "change of mind" if the entries are at least 365 days apart or the newer one uses revision words ("used to", "no longer", "I now think"...). Otherwise it is a "live" conflict.
   - The person settles each card: holds the first, holds the second, holds both, or not a conflict. Only cards settled as "second" count as "views changed".
   - When both entries are the person's messages to AI chats and the assistant's replies agreed both times, the card says so.
   - Code: `conflictKind`, `changedViews` (5609693d, 2026-11-13); replies and agreement (`agreement.ts`, `replies.ts`, 5609693d).

## Built before vs during the sprint (Nov 13-15, 2026)

| Before | During |
|---|---|
| Import, library, theme sort, on-device finder, opt-in model step + prompt, allowance, Conflicts screen with verdicts (Nov 1-7) | Change-of-mind vs live split; "your AI agreed both times" flag and on-device stance reader (5609693d); sycophancy harness + pilot (2b7caaf2, 2daaff2f); this whole evaluation (`evals/conflicts`, `paper/`); UI theming (not part of the paper) |
