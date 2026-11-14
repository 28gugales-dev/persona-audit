# Persona audit: zero false alarms, missing the point

Code, data and every model reply behind the Apart AI x Epistemics sprint paper (Track 3, Nov 13-16, 2026):
**"Zero false alarms, missing the point: auditing a belief-mapping tool on philosophers' documented changes of mind"** — [`paper/paper.pdf`](paper/paper.pdf).

Persona (part of [Amphi](https://amphi-forum.org)) reads what a person has written and shows where their views conflict or have changed. We audited the shipped version against answer keys it cannot grade itself on: planted conflicts with known truth, and 24 documented changes of mind in public-domain writing (12 development cases by ten authors, then two sets of six sourced later by agents that never saw our prompts).

**Headline:** the shipped prompt raised no false alarms, yet given each whole history it found the change in 2 of 24 cases, and its word-overlap grouping never put a change's two ends together. Four causes: grouping by shared words, a definition that counts only views asserted at once, a 400-character excerpt cut, and retractions that never restate the old view. The repaired configuration (whole history in one call, the realX and changes prompts merged, longer excerpts) found 17 of 18 cases on the sets it was tuned on and 6 of 6, in all three repeated runs, on a third set sourced after it was frozen and deployed to Persona (Nov 14, 2026; shipped prompt 1 of 6). Our first scorer credited only the keyed passage and understated recall; case-level scores use blind Haiku and Sonnet labels calibrated on known pairs (102/110) and decoys (6/102).

## Layout

| Path | What |
|---|---|
| `paper/paper.md`, `paper.pdf` | The paper. `build_pdf.py` renders it (`uv run --with markdown python paper/build_pdf.py`). |
| `paper/RESULTS.md` | Ledger: every number in the paper with the file it comes from. |
| `paper/PLAN.md` | Each round's design and numeric predictions, committed before its runs. Failed predictions are kept. |
| `paper/REFLECTION.md` | What each round changed in our beliefs and plan. |
| `paper/data/` | Planted histories and answer keys, hand-written sets, the real-text cases (passages, source URLs, line spans, secondary sources) and histories. |
| `paper/results/` | Requests sent (`requests_*.jsonl`, with the exact system prompt), every raw model reply (`haiku_raw/`, `raw/`), and scores (`*_scores.json`). |
| `paper/research/` | Reviews and critiques of the plan written during the sprint. |
| `evals/conflicts/gen/` | Python scorers and builders. Run from the repo root, e.g. `python3 evals/conflicts/gen/score_v16.py .` (`score_v17.py` needs `uv run --with scikit-learn`; the case-level round-18 scores come from `score_v18b.py`). |
| `evals/conflicts/src/` | TypeScript request builders. They import Persona's own request builder and prompt, so they ran inside the Amphi monorepo; `src/shipped.ts` pins the Nov 1 prompt. |
| `product/shipped-2026-11-01/` | The audited product code (request builder, theme sort, prompt, limits) as shipped. |
| `product/deployed-2026-11-14/` | After the first fix (afternoon): whole history in one request when it fits, realX prompt. |
| `product/deployed-2026-11-14-evening/` | The final configuration: realX and changes prompts merged, posts up to 1,000 characters (Amphi main 34bfd61e). |

## Reproducing numbers

All scorers read only files in this repo, so every reported number can be recomputed from the saved replies without model access. Model calls were made with Claude Haiku 5.5 (and Sonnet 5.5 for checks) through Claude Code subagents, one fresh agent per request; GPT (via Codex) wrote the planted posts and served as the question-neutrality judge.

## Data and licences

Real-text passages are public domain (pre-1930 publications and translations from Project Gutenberg, Wikisource and archive.org). PhilPapers 2020 figures are used as aggregates under CC BY-NC. Planted and hand-written items are synthetic. No personal data is included.
