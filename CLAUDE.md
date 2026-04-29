# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
python -m src.main

# Run all tests
pytest

# Run a single test
pytest tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score

# Test the RAG retriever
python -m src.rag.retriever
```

**Python:** The active interpreter is the Anaconda install at `C:\Users\neba_\anaconda3\python.exe`. `requirements.txt` is a full conda environment export, not a pip file — activate the base conda env rather than pip-installing from it. Core runtime dependencies are `pandas`, `scikit-learn`, `pytest`, and `streamlit`.

## Architecture

VibeFinder is a content-based music recommender. Recommendation logic lives in `src/recommender.py`; knowledge retrieval for future LLM integration lives in `src/rag/`.

### [src/recommender.py](src/recommender.py)

Two parallel APIs coexist intentionally:

| API | Consumer |
|---|---|
| Dict-based: `load_songs`, `score_song`, `recommend_songs` | `src/main.py` — already works |
| OOP: `Song`, `UserProfile`, `Recommender` | `tests/test_recommender.py` — stubs need implementation |

**Scoring** (in `score_song`): genre match (+2.0), mood match (+1.0), energy proximity (up to +1.0), acousticness proximity (up to +1.0). Max 5.0, sorted descending.

**Field mismatch** — when implementing `Recommender.recommend()`, bridge `UserProfile` fields to the dict `score_song` expects:

| `UserProfile` field | `score_song` dict key | Conversion |
|---|---|---|
| `favorite_genre` | `genre` | — |
| `favorite_mood` | `mood` | — |
| `target_energy` | `energy` | — |
| `likes_acoustic` | `acousticness` | `True` → `1.0`, `False` → `0.0` |

`Recommender.recommend()` and `Recommender.explain_recommendation()` are stubs — both OOP tests fail until implemented.

### [src/rag/retriever.py](src/rag/retriever.py)

TF-IDF retriever over the `knowledge_base/` markdown files. `Retriever.__init__` loads all `knowledge_base/genres/*.md` and `knowledge_base/moods/*.md` into `Chunk` objects (`source_file`, `category`, `name`, `text`), fits a `TfidfVectorizer` with `token_pattern=r"(?u)\b\w+\b"` (single-char tokens required so "R&B" → ["R","B"] isn't silently dropped), and stores the TF-IDF matrix. `retrieve(song, k=3)` builds a `"<genre> <mood>"` query string, vectorizes it, and returns top-k chunks by cosine similarity.

Knowledge base: 12 genre files (`knowledge_base/genres/`) and 12 mood files (`knowledge_base/moods/`). Chunk `name` is the filename stem lowercased (e.g. `r&b`, `sad`).

### Data

`data/songs.csv` — 18 songs. Column names match `Song` dataclass fields exactly. `energy`, `valence`, `danceability`, `acousticness` ∈ [0.0, 1.0]; `tempo_bpm` in BPM. `valence`, `danceability`, and `tempo_bpm` are stored but unused in scoring.

## Environment

`.env` defines `GEMINI_API_KEY` — not yet wired into any source file, reserved for a planned LLM/RAG integration step.

## Assignment Context

AI 110, Module 3. Remaining deliverables:
- Implement `Recommender.recommend()` and `Recommender.explain_recommendation()` in `src/recommender.py`
- Fill in `README.md` and `model_card.md`

`streamlit` is in requirements for a potential future UI; no Streamlit app exists yet.
