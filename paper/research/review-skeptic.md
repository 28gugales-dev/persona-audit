# Skeptic review of PLAN.md v1 (judge's view)

1. **Q1 substitutes an easier question.** Track 3 asks whether the tool helps *people notice* things *they later endorse*. Philosophers endorsed their *change*, not a *flag*; nobody endorses Persona's output. As written, Q1 is "can a detector recover published reversals". **Fix:** say so in the title and abstract ("recovers self-endorsed revisions", a proxy). Add one real endorsement datapoint: the author's own consented history, with a list of known changes written down *before* running, then rate each flag "would I want this shown" and report it as n=1. The protocol for the real user study goes in Limitations.

2. **The change-of-mind label is decided by date, so Q1 "kind" is trivial.** `conflictKind` returns `shift` when the two entries are ≥365 days apart or match the `REVISED` regex. Philosopher reversals are years apart, and P3 positives contain "I used to think" by construction. **Fix:** report kind only on pairs <365 days apart that lack REVISED cues, or run an arm with dates compressed. Otherwise call it a property of the code, not a result.

3. **The decoys are the detector's own spec (tuned on the test set).** `localConflicts.ts` hard-codes REPORTED/OTHER_SUBJECT ("my professor"), HEDGE ("less sure"), skips "?", and `compoundsDiffer`'s comment uses "moral realism" vs "moral luck", which is exactly D5. The "Do not count" list in `CONFLICTS_SYSTEM` is D1-D4. Template decoys only test whether the code follows its own regex. **Fix:** treat the template set as a dev set. Build a blind test set: decoys and P2 paraphrases written by another model family given only the label definitions, never the code. Add ~30 hand-written adversarial items: a reported view the person then adopts, a hedge that is still a reversal, sarcasm, a negated refinement, and the same claim with the "not" moved. Report dev and test results side by side; the gap is itself a finding.

4. **The LLM writes the paraphrase and an LLM detects it.** P2 recall partly measures one model reading its own style. **Fix:** paraphrase with the other family (DeepSeek) and detect with Haiku, and the reverse. Stratify recall by lexical overlap (Jaccard bins). That gives the honest "where Local stops" curve.

5. **The reversal set is small, picked by hand, and in the training data.** Famous reversals (Putnam, Wittgenstein, Ayer) are things Haiku already knows. 10-14 hand-picked cases favour the dramatic ones. Controls that "conflict with neither" are straw men. **Fix:** freeze an inclusion rule before running (for example, every SEP entry stating that the philosopher changed their view; take all hits). Strip names and era vocabulary. Include an arm with explicit change markers removed. Add a contamination probe ("who wrote this?"). Use **hard controls**: same-era, same-topic pairs that scholars argue are compatible.

6. **Pooled precision depends on our own mix.** We choose 2-4 positives against 3-6 decoys, so precision is whatever that ratio makes it. **Fix:** lead with per-type recall and per-decoy false-flag rates. Report precision at two stated prevalences. Define S3 as a precision difference at a matched flag count whose CI excludes 0 ("similar recall" is undefined).

7. **The thresholds are arbitrary.** Nothing justifies 0.6, 0.15, 70%, 90%. **Fix:** anchor them: P2 recall must beat the word-overlap baseline by a preregistered margin; the decoy false-flag rate must be below the naive chatbot's. S4 needs a stated minimum n for its CI to be informative.

8. **Running Haiku through a subagent is not the production call.** A Claude Code subagent adds an agent system prompt and tools, and its temperature and output cap are unknown. `deps.complete` in production differs. **Fix:** label it "Haiku (agent harness)". Pass `CONFLICTS_SYSTEM` verbatim with tools disabled, feed raw output through the real `readConflicts`, and run 20 requests twice to report run-to-run agreement. One fidelity paragraph.

9. **Theme misses are confounded with model misses.** A planted pair reaches the model only if `sortLibrary` puts both entries in one theme and `spread` keeps both. **Fix:** split end-to-end recall into P(theme together) × P(in the 20-excerpt window) × P(model flags | seen). Also run the model with an oracle theme assignment.

10. **Q4 misses the biggest nudge: the product's own card.** Labelling a pair "change of mind" frames the newer view as growth, so it leans toward the later view by design. The local tension line is a fixed template, neutral by construction. **Fix:** score the model's questions *and* the kind label against the user's later verdict where known (the reversal set). This is the Innovation hook: a reflection tool's framing as an epistemic intervention.

**Weakest point a judge will name:** "No human endorsement, and the decoys were written to fit the detector" (1 + 3).

**The single change that raises Execution and Innovation most:** a blind test set (fix 3+4) with dev-vs-test results reported. It turns a self-graded demo into validation. Add fix 10 for novelty.

AGREED WITH PLANNER:
- `conflictKind` is decided by date and regex, so Q1 kind and P3 are close to unit tests (my 2).
- Template and LLM labels leak and decoys need blind labelling, since D4/D6 are arguable (my 3, 4); planner adds second-model label agreement plus a hand check, and I agree.
- "Endorsed later" is guaranteed by selection, and the model sees only our paraphrases (my 1, 5).
- Theme formation confounds Q3, and a generator artifact can drive recall vs length (my 9).
