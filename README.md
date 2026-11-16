# Persona audit: silent misses

Code, data and every model reply behind the Apart AI x Epistemics sprint paper (Track 3, Nov 13-15, 2026):
**"Silent misses: auditing a belief-mapping tool on philosophers' documented changes of mind"** — [`paper/paper.pdf`](paper/paper.pdf).

Persona (part of [Amphi](https://amphi-forum.org)) reads what a person has written and shows where their views conflict or have changed. We audited the shipped version against 30 changes of mind that authors documented in their own public-domain writing, plus planted conflicts with known answers.

**Headline:** given each whole history, the shipped prompt found 3 of the 30 changes and flagged no control passage, so the failure was silent. Four causes: grouping posts by shared words, a definition that counts only views held at the same time, cutting each post to 400 characters, and retractions that never restate the old view. A rewritten prompt, frozen before two new test sets were sourced, found 10 of their 12 changes against 2 for the shipped prompt (p = 0.008). With longer excerpts and one output line removed it is the prompt Persona now runs; on a fourth set, sourced after that version shipped and run once, it found 6 of 7 against 1. A one-line naive prompt also finds many changes (20 of 30), but only 50% of its cards were judged genuine, against 88% for the prompt Persona now runs. All 77 pre-written predictions are reported, including the 37 that failed. Whether these cards help people decide is not measured.

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
| `evals/conflicts/gen/` | Python scorers and builders. Run from the repo root, e.g. `python3 evals/conflicts/gen/score_v16.py .` (`score_v17.py` needs `uv run --with scikit-learn`; the case-level scores come from `score_v18b.py`, card costs from `score_cost.py`, the hand check from `score_human_check.py`). |
| `evals/conflicts/src/` | TypeScript request builders. They import Persona's own request builder and prompt, so they ran inside the Amphi monorepo; `src/shipped.ts` pins the Nov 1 prompt. |
| `product/shipped-2026-11-01/` | The audited product code (request builder, theme sort, prompt, limits) as shipped. |
| `product/deployed-2026-11-14/` | After the first fix (afternoon): whole history in one request when it fits, realX prompt. |
| `product/deployed-2026-11-14-evening/` | A second "changes" prompt added beside the rewrite, posts up to 1,000 characters (Amphi main 34bfd61e). |
| `product/deployed-2026-11-15/` | The second prompt removed again: one prompt (main c9a32b4c). |
| `product/deployed-2026-11-15b/` | The "at most 8 pairs" line removed (main 2a5e359e). This is the prompt Persona runs now. |
| `product/deployed-2026-11-15c/`, `15d/` | The whole-history limit raised to 124 posts (main cea9afd9), then to 244 (main b9e4feef). |
| `paper/human_check/` | The author's blind labels of 20 cards, the page used to label them, the key and the agreement scores. |

## Reproducing numbers

All scorers read only files in this repo, so every reported number can be recomputed from the saved replies without model access. Model calls were made with Claude Haiku 5.5 (the system under test), with Sonnet 5.5 and Opus 5.5 as blind labellers, through Claude Code subagents, one fresh agent per request; GPT (via Codex) wrote the planted posts and served as the question-neutrality judge.

## Data and licences

Real-text passages are public domain (pre-1930 publications and translations from Project Gutenberg, Wikisource and archive.org). PhilPapers 2020 figures are used as aggregates under CC BY-NC. Planted and hand-written items are synthetic. No personal data is included.
