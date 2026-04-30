# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the CLI pipeline (interactive menu: 3 presets, custom profile, quit)
python -m src.main

# Run the Streamlit UI (exposes scoring, retrieval, Gemini, guardrail per card)
streamlit run app.py

# Run all tests
pytest

# Run a single test
pytest tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score

# Smoke-test individual RAG stages directly (each module has a __main__ block)
python -m src.rag.retriever
python -m src.rag.explainer
python -m src.rag.guardrail
```

**Python:** active interpreter is the Anaconda install at `C:\Users\neba_\anaconda3\python.exe`. `requirements.txt` is a full conda environment export, not a pip file — activate the base conda env rather than pip-installing from it. Core runtime deps: `pandas`, `scikit-learn`, `pytest`, `streamlit`, `google-genai`, `python-dotenv`.

**Working directory:** all entry points (`src.main`, `app.py`, the `__main__` blocks) read `data/songs.csv` and `knowledge_base/` with relative paths. Run them from the project root, not from `src/`.

## Architecture

VibeFinder 2.0 is a content-based music recommender wrapped in a 4-stage pipeline: **score → retrieve → explain → guard**. Each stage is a separate module so it can be swapped or tested in isolation.

### Pipeline stages

| Stage | Module | Output |
|---|---|---|
| 1. Score | [src/recommender.py](src/recommender.py) — `recommend_songs` | top-k `(song, score, reasons_str)` |
| 2. Retrieve | [src/rag/retriever.py](src/rag/retriever.py) — `Retriever.retrieve` | top-3 `Chunk`s by TF-IDF cosine |
| 3. Explain | [src/rag/explainer.py](src/rag/explainer.py) — `explain` | 2–3 sentence string from Gemini |
| 4. Guard | [src/rag/guardrail.py](src/rag/guardrail.py) — `validate` | `GuardrailResult(confidence, passed, warnings)` |

[src/main.py](src/main.py) (CLI) and [app.py](app.py) (Streamlit) both compose these four stages identically — they are presentation layers, not logic.

### [src/recommender.py](src/recommender.py): two parallel APIs

| API | Consumer |
|---|---|
| Dict-based: `load_songs`, `score_song`, `recommend_songs` | `src.main`, `app.py` — runtime path |
| OOP: `Song`, `UserProfile`, `Recommender` | [tests/test_recommender.py](tests/test_recommender.py) — stubs |

`Recommender.recommend()` and `Recommender.explain_recommendation()` are unimplemented stubs that return placeholders; both OOP tests fail until they are filled in. When implementing, bridge `UserProfile` → `score_song` dict keys: `favorite_genre`→`genre`, `favorite_mood`→`mood`, `target_energy`→`energy`, `likes_acoustic` (bool) → `acousticness` (`True`→`1.0`, `False`→`0.0`).

**Scoring** in `score_song`: genre match (+2.0), mood match (+1.0), energy proximity (up to +1.0), acousticness proximity (up to +1.0). Max 5.0, sorted descending. `valence`, `danceability`, `tempo_bpm` are loaded from CSV but unused in scoring.

### [src/rag/retriever.py](src/rag/retriever.py): TF-IDF over markdown KB

Indexes `knowledge_base/genres/*.md` (12 files) + `knowledge_base/moods/*.md` (12 files) into `Chunk(source_file, category, name, text)` where `name` is the lowercased filename stem. `retrieve(song, k=3)` builds a `"<genre> <mood>"` query string and ranks chunks by cosine similarity.

**Critical:** vectorizer uses `token_pattern=r"(?u)\b\w+\b"` rather than the sklearn default. This is required so `"R&B"` tokenizes to `["R", "B"]` instead of being silently dropped (default pattern requires 2+ chars). Do not "simplify" this back to the default.

`Retriever.__init__` does the TF-IDF fit, which is non-trivial. Both [src/main.py](src/main.py) and [app.py](app.py) instantiate it once and pass it through; `app.py` wraps it in `@st.cache_resource`. Don't construct one per request.

### [src/rag/explainer.py](src/rag/explainer.py): Gemini, grounded

Reads `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) from `.env` via `python-dotenv`. Default model is `gemini-2.5-flash`. The prompt forbids inventing facts about artist/release year/chart performance and constrains output to 2–3 sentences — these constraints are what the guardrail later checks against.

**Failure mode:** if the API key is missing or the call raises, `explain` returns the literal string `"[LLM unavailable] Recommended based on genre and mood match."` instead of raising. Downstream code (and the guardrail) must handle this fallback gracefully. Don't change this contract without auditing callers.

### [src/rag/guardrail.py](src/rag/guardrail.py): three weighted checks

Starts at `confidence = 1.0` and subtracts:
- **Length** (−0.2): not 1–5 sentences (split on `.!?`).
- **Lexical grounding** (−0.5): `<30%` of explanation tokens (≥4 chars, non-stopword) appear in the retrieved chunks.
- **Hallucination patterns** (−0.3): regexes for years (`19xx`/`20xx`), `Billboard`, `Grammy`, `released in`, `peaked at`, `chart`, `album of the year`, `debut album`, `record label`.

`passed = confidence >= 0.7`. The thresholds, weights, and pattern list are the contract the README's "Reliability & Guardrails" section advertises — changing them changes the demo's behavior, not just internals.

The sentence splitter is naive (any `.!?` is a boundary), so decimals in numeric values can inflate the sentence count and trip the length check on borderline outputs. This is a known artifact of the demo, not a bug to silently fix.

### Data

[data/songs.csv](data/songs.csv) — 18 songs. Column names match the `Song` dataclass exactly. `energy`, `valence`, `danceability`, `acousticness` ∈ [0.0, 1.0]; `tempo_bpm` in BPM.

`knowledge_base/` markdown files are the *only* grounding source for the explainer — there is no other corpus. If a genre or mood appears in the CSV but lacks a corresponding `.md` file, retrieval will still return the closest 3 chunks by cosine, which may be poor. Keep CSV vocabulary aligned with KB filenames.

## Environment

`.env` at the project root must define `GEMINI_API_KEY` (or `GOOGLE_API_KEY`). Without it the explainer returns the `[LLM unavailable]` fallback string and the rest of the pipeline still runs.
