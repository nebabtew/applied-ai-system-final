"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profiles = [
        ("Late Night R&B", {"genre": "R&B", "mood": "sad", "energy": 0.30, "acousticness": 0.60}),
        ("Pop Energy", {"genre": "pop", "mood": "happy", "energy": 0.90, "acousticness": 0.10}),
        ("Lo-Fi Chill", {"genre": "lofi", "mood": "chill", "energy": 0.40, "acousticness": 0.75}),
        ("Adversarial Rock", {"genre": "rock", "mood": "chill", "energy": 0.95, "acousticness": 0.90}),
        ("Adversarial Neutral", {"genre": "classical", "mood": "happy", "energy": 0.50, "acousticness": 0.50}),
    ]

    for name, prefs in profiles:
        print(f"\n=== {name} ===\n")
        recommendations = recommend_songs(prefs, songs, k=5)
        for rec in recommendations:
            song, score, explanation = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
