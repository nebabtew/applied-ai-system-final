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
```

The virtual environment is in `.venv/`. Activate with `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac/Linux) before running commands if packages aren't found. Dependencies: `pandas`, `pytest`, `streamlit`.

## Architecture

This is a content-based music recommender simulation. All logic lives in two source files:

**[src/recommender.py](src/recommender.py)** — the core module. Contains:
- `Song` dataclass — attributes: `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`
- `UserProfile` dataclass — preference fields: `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`
- `Recommender` class (OOP API) — `recommend(user, k)` and `explain_recommendation(user, song)` — **stubs; CLI works but OOP tests will fail until these are implemented**
- `load_songs(csv_path)` — reads `data/songs.csv` into a list of dicts — already implemented
- `score_song(user_prefs, song)` — scores a single dict-based song against dict-based preferences, returns `(float, List[str])` — already implemented
- `recommend_songs(user_prefs, songs, k)` — ranks all songs and returns top-k as `List[Tuple[dict, float, str]]` — already implemented

**[src/main.py](src/main.py)** — thin CLI runner. Calls `load_songs` then `recommend_songs` with five hardcoded user profiles and prints results. Uses dict-based API only.

**Two parallel APIs exist intentionally:**
- Dict-based functions (`load_songs`, `score_song`, `recommend_songs`) are used by `src/main.py`
- OOP classes (`Song`, `UserProfile`, `Recommender`) are used by `tests/test_recommender.py`

**Key implementation detail — field mismatch between `UserProfile` and `score_song`:**

| `UserProfile` field | `score_song` dict key | Type change |
|---|---|---|
| `favorite_genre` | `genre` | none |
| `favorite_mood` | `mood` | none |
| `target_energy` | `energy` | none |
| `likes_acoustic` | `acousticness` | **bool → float** (`True` → `1.0`, `False` → `0.0`) |

When implementing `Recommender.recommend()`, build the dict that `score_song` expects from `UserProfile` fields, converting `likes_acoustic` to a float.

**Scoring logic** (in `score_song`): genre match (+2.0), mood match (+1.0), energy proximity (up to 1.0), acousticness proximity (up to 1.0). Max score is 5.0. Sorted descending.

**Data:** `data/songs.csv` — 18 songs, columns match `Song` fields exactly. Numeric attributes (`energy`, `valence`, `danceability`, `acousticness`) are in range [0.0, 1.0]; `tempo_bpm` is in BPM. `valence`, `danceability`, and `tempo_bpm` are stored but not used in scoring.

**Tests:** `tests/test_recommender.py` uses only the OOP API. `test_recommend_returns_songs_sorted_by_score` asserts the pop/happy/high-energy song ranks first for a matching user profile. `test_explain_recommendation_returns_non_empty_string` asserts a non-empty string is returned.

## Assignment Context

This is a classroom project (AI 110, Module 3). Three deliverables:
- **`src/recommender.py`** — implement `Recommender.recommend()` and `Recommender.explain_recommendation()`
- **`README.md`** — system design explanation, experiments, limitations
- **`model_card.md`** — structured reflection on bias, strengths, evaluation, and future work

`streamlit` is listed in requirements for a potential future UI but no Streamlit app exists yet.
