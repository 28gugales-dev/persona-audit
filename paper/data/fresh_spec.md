# Fresh narrated items (written 2026-11-14 for round-4 confirmation; the writer sees only this file)

Write 40 items. Each item is two short first-person posts by the same person on one philosophy question: post A (written in 2018) and post B (written in 2023). Each post is 1-3 sentences, plain conversational English, like a Reddit comment. No names of philosophers, no jargon labels.

Use these questions (one item per question, in order; reuse from the top after 35):
nominalism vs Platonism about abstract objects; objective vs subjective aesthetic value; externalism vs internalism about justification; empiricism vs rationalism; subjective vs objective meaning of life; internalism vs externalism about moral motivation; two boxes vs one box in Newcomb's problem; virtue ethics vs deontology; Millian vs Fregean names; death vs survival in the teletransporter; B-theory vs A-theory of time; credence vs belief; non-anthropocentric vs anthropocentric environmental ethics; extended mind yes vs no; reliabilism vs foundationalism; legal non-positivism vs positivism; restricted vs universal composition; naturalist realism vs non-naturalism in ethics; Aristotelian vs Humean practical reason; principle of sufficient reason true vs false.

Labels (exactly this many of each):
- NR (20): narrated reversal. Post A clearly holds one side. Post B clearly holds the incompatible side AND says, in the person's own words, that their view changed. Vary the narration a lot: at most 5 of the 20 may use the words "changed my mind"; others say things like "these days I'd say", "I've come round to", "I no longer think", "back then I was sure ... now", "I was wrong", "after a few years of thinking about it", or narrate it in the middle or end of the post rather than the start.
- NF (7): narrated refinement. Post A holds a view. Post B holds the SAME side, says it used to put it badly or too loosely, and states it more carefully. Not a change of side.
- NA (7): narrated reaffirmation. Post B says the person reconsidered or was tempted by the other side, but still holds the same side as post A.
- ND (6): narrated doubt. Post B says they are less sure than they used to be, but does not take the other side.

Output only a JSON array, no commentary, saved to fresh_narrated.json in this directory:
[{"id":"f01","question":"...","label":"NR","a":"...","b":"..."}, ...]
Ids f01..f40. Mix the labels in a shuffled order, not grouped.
