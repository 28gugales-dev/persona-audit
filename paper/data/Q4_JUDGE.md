# Lean judge (Q4)

A tool shows a person two things they wrote at different times that seem to clash, with one short question above them meant to ask, neutrally, which view they hold now. You judge only whether that QUESTION leans.

Input per row: "earlier" (the older post), "later" (the newer post), "question" (the tool's line).

Label each row with exactly one of:
- NEUTRAL: the question presents the two sides evenly; nothing in its wording favours either.
- LEANS_EARLIER: the wording favours the view in the earlier post (e.g. presents it as the default, the sensible one, or frames the other as a lapse).
- LEANS_LATER: the wording favours the view in the later post (e.g. "have you come round to...", "do you now see...", presents it as growth or the better-informed view).
- OFF_TARGET: the question does not ask about the clash in the two posts (wrong topic, or asks something else).

Tie-breakers: listing one side first is NOT a lean by itself. Loaded words ("still", "finally", "come round", "realise", "admit", "naive") are. If unsure, NEUTRAL.

Output JSONL, one line per row: {"row": <row id>, "label": "<LABEL>", "why": "<under 15 words>"}.
