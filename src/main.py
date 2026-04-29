from src.recommender import load_songs, recommend_songs
from src.rag.retriever import Retriever
from src.rag.explainer import explain
from src.rag.guardrail import validate

PROFILES = [
    ("Late Night R&B", {"genre": "R&B", "mood": "sad", "energy": 0.30, "acousticness": 0.60}),
    ("Pop Energy",     {"genre": "pop", "mood": "happy", "energy": 0.85, "acousticness": 0.15}),
    ("Chill Lofi",     {"genre": "lofi", "mood": "chill", "energy": 0.40, "acousticness": 0.75}),
]


def main() -> None:
    songs = load_songs("data/songs.csv")
    retriever = Retriever()

    total_recs = 0

    for profile_name, user_prefs in PROFILES:
        print("=" * 60)
        print(f"PROFILE: {profile_name}")
        print(
            f"  genre={user_prefs['genre']}  mood={user_prefs['mood']}"
            f"  energy={user_prefs['energy']}  acousticness={user_prefs['acousticness']}"
        )
        print("=" * 60)

        recommendations = recommend_songs(user_prefs, songs, k=3)

        for i, (song, score, _) in enumerate(recommendations):
            if i > 0:
                print("-" * 40)

            print(f"{song['title']} — {song['artist']}")
            print(f"  genre={song['genre']}  mood={song['mood']}  score={score:.2f}")

            chunks = retriever.retrieve(song, k=3)
            chunk_labels = ", ".join(f"{c.category}:{c.name}" for c in chunks)
            print(f"  context: [{chunk_labels}]")

            explanation = explain(song, user_prefs, chunks)
            result = validate(explanation, chunks)

            print(f"  explanation: {explanation.strip()}")
            print(f"  confidence={result.confidence:.2f} | passed={result.passed}")

            for warning in result.warnings:
                print(f"    ! {warning}")

            total_recs += 1

        print()

    print("=" * 60)
    print(f"Pipeline run complete. Reviewed {total_recs} recommendations across {len(PROFILES)} profiles.")


if __name__ == "__main__":
    main()
