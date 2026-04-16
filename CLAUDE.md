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
- `Recommender` class (OOP API) — `recommend(user, k)` and `explain_recommendation(user, song)` — **stubs that still need implementing**
- `load_songs(csv_path)` — reads `data/songs.csv` into a list of dicts — already implemented
- `score_song(user_prefs, song)` — scores a single dict-based song against dict-based preferences, returns `(float, List[str])` — already implemented
- `recommend_songs(user_prefs, songs, k)` — ranks all songs and returns top-k as `List[Tuple[dict, float, str]]` — already implemented

**[src/main.py](src/main.py)** — thin CLI runner. Calls `load_songs` then `recommend_songs` with five hardcoded user profiles and prints results. Uses dict-based API only.

**Two parallel APIs exist intentionally:**
- Dict-based functions (`load_songs`, `score_song`, `recommend_songs`) are used by `src/main.py`
- OOP classes (`Song`, `UserProfile`, `Recommender`) are used by `tests/test_recommender.py`

**Key implementation detail — key name mismatch:** `score_song` expects dict keys `genre`, `mood`, `energy`, `acousticness`, but `UserProfile` uses `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`. When implementing `Recommender.recommend()`, you must convert the `UserProfile` fields into the dict shape that `score_song` expects.

**Scoring logic** (in `score_song`): genre match (+2.0), mood match (+1.0), energy proximity (up to 1.0), acousticness proximity (up to 1.0). Max score is 5.0. Sorted descending.

**Data:** `data/songs.csv` — columns match `Song` fields exactly. Numeric attributes (`energy`, `valence`, `danceability`, `acousticness`) are in range [0.0, 1.0]; `tempo_bpm` is in BPM.

**Tests:** `tests/test_recommender.py` uses only the OOP API. `test_recommend_returns_songs_sorted_by_score` asserts the pop/happy/high-energy song ranks first for a matching user profile. `test_explain_recommendation_returns_non_empty_string` asserts a non-empty string is returned.

## Assignment Context

This is a classroom project (AI 110, Module 3). After implementing the recommender logic, the student also fills in `README.md` (system design explanation, experiments, limitations) and `model_card.md` (structured reflection on bias, strengths, evaluation, and future work).
