# Candidate directions (written before PLAN.md, not anchored on the sycophancy pilot)

Main question: does Persona's belief mapping help people notice where their views conflict or change, in ways they later agree with?

Scored 1-5 against the published rubric (track3.md): Impact+Novelty (I), Execution feasible this weekend (E), Clarity of the story (C). "Data" says what real data it needs and whether we have it.

| # | Direction | What it measures | Data (have it?) | I | E | C | Notes |
|---|---|---|---|---|---|---|---|
| 1 | **Endorsed reversals**: philosophers who later said in print they changed their minds (Wittgenstein, Putnam, Jackson, Ayer, ...) | Does the tool find the change, and call it a change of mind rather than a live conflict? The person's own later statement is the "later endorsed" answer key | Short excerpts + citations, public domain where possible (yes, buildable) | 4 | 4 | 5 | Unique framing of "later endorse": an external, citable endorsement. Small n; needs controls (same-era consistent pairs) |
| 2 | **Planted-conflict benchmark with hard decoys** | Precision/recall of the on-device detector vs the production LLM step vs naive baselines; decoys = reported speech, hedges, questions, refinements, shared word different subject | Synthetic histories from PhilPapers-contested positions (yes) | 3 | 5 | 4 | Solid execution; benchmark alone is "well-trodden" unless tied to endorsement |
| 3 | **Window / scale audit**: the LLM step sees 20 excerpts per theme | Recall of planted conflicts as history grows (20 → 500 entries) using the real `conflictRequests` sampler | Synthetic (yes) | 3 | 5 | 4 | A real product finding (what a deployed design misses), cheap |
| 4 | **Nudge audit of the tension question** | Does the model's neutral question lean toward one side, toward the PhilPapers majority, or toward the newer view? | Model outputs from 1-3 + PhilPapers % (yes) | 4 | 4 | 4 | Epistemic-autonomy angle: a reflection tool that nudges toward consensus is not "endorsed later" but steered. Doubles as the "steelman fairness" check |
| 5 | **Privacy/recall trade-off** | What the on-device detector finds with zero data leaving vs the opt-in model | From 2-3 (yes) | 3 | 5 | 4 | Product-relevant; folds into 2 |
| 6 | Cross-chat sycophancy ("your AI agreed both times") | How often an assistant agrees with both sides in separate chats; does the on-device stance heuristic work | Pilot exists (Claude only, n=60 pairs) | 2 | 4 | 3 | ELEPHANT already reports both-sides affirmation; our pilot rate is low and the heuristic failed (kappa 0.02). Keep small, as a negative result |
| 7 | Endorsement by real users (friends' Reddit, rated) | Do people agree the conflicts are real | Needs written consent; none in hand this weekend | 5 | 1 | 5 | Cannot run without consent; protocol only, stated as future work |
| 8 | Classroom pilot (LMU, Moorpark) | Usage aggregates | Discuss app, not belief mapping; consent for paper use not documented | 2 | 1 | 2 | Cut unless professors' OK is on file |
| 9 | Prompt injection through imported history | Does planted text steer the conflict model | Synthetic (yes) | 2 | 4 | 3 | Dual-use appendix material |

## Leaning (to be checked by Stage 2 reviewers)

Lead with 1 + 2 (does it find real, later-endorsed changes and planted conflicts, without flagging look-alikes), support with 3 and 4 (what the deployed design misses, and whether its question nudges), and keep 6 as a short negative result. 7 is the honest gap.
