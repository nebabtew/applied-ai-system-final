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
- `Recommender` class (OOP API) — `recommend(user, k)` and `explain_recommendation(user, song)` — both are stubs to implement
- `load_songs(csv_path)` — reads `data/songs.csv` into a list of dicts — stub to implement
- `score_song(user_prefs, song)` — scores a single dict-based song against dict-based preferences, returns `(float, List[str])` — stub to implement
- `recommend_songs(user_prefs, songs, k)` — ranks all songs and returns top-k as `List[Tuple[dict, float, str]]` — stub to implement

**[src/main.py](src/main.py)** — thin CLI runner. Calls `load_songs` then `recommend_songs` and prints results. Uses dict-based API (not the OOP classes).

**Two parallel APIs exist intentionally:**
- Dict-based functions (`load_songs`, `score_song`, `recommend_songs`) are used by `src/main.py`
- OOP classes (`Song`, `UserProfile`, `Recommender`) are used by `tests/test_recommender.py`

Both must be implemented to satisfy tests and run the app.

**Data:** `data/songs.csv` — columns match `Song` fields exactly. Songs have numeric attributes (`energy`, `valence`, `danceability`, `acousticness`) in the range [0.0, 1.0]; `tempo_bpm` is in beats per minute.

**Tests:** `tests/test_recommender.py` imports from `src.recommender`. Tests assert that `recommend()` returns results sorted so that the best-matching song (by genre + mood + energy) ranks first, and that `explain_recommendation()` returns a non-empty string.

## Assignment Context

This is a classroom project (AI 110, Module 3). After implementing the recommender logic, the student also fills in `README.md` (system design explanation, experiments, limitations) and `model_card.md` (structured reflection on bias, strengths, evaluation, and future work).
