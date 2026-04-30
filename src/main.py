from src.recommender import load_songs, recommend_songs
from src.rag.retriever import Retriever
from src.rag.explainer import explain
from src.rag.guardrail import validate


PROFILES = [
    ("Late Night R&B", {"genre": "R&B", "mood": "sad", "energy": 0.30, "acousticness": 0.60}),
    ("Pop Energy",     {"genre": "pop", "mood": "happy", "energy": 0.85, "acousticness": 0.15}),
    ("Chill Lofi",     {"genre": "lofi", "mood": "chill", "energy": 0.40, "acousticness": 0.75}),
]


def run_pipeline(profile_name: str, user_prefs: dict, songs: list, retriever: Retriever) -> None:
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

    print()


def prompt_float(label: str) -> float:
    while True:
        raw = input(f"  {label} (0.0-1.0): ").strip()
        try:
            val = float(raw)
            if 0.0 <= val <= 1.0:
                return val
            print("  Must be between 0.0 and 1.0. Try again.")
        except ValueError:
            print("  Invalid number. Try again.")


def build_custom_profile() -> tuple[str, dict]:
    print("\nBuild your own profile:")
    genre = input("  genre: ").strip()
    mood = input("  mood: ").strip()
    energy = prompt_float("energy")
    acousticness = prompt_float("acousticness")
    name = f"Custom ({genre} / {mood})"
    return name, {"genre": genre, "mood": mood, "energy": energy, "acousticness": acousticness}


def show_menu() -> str:
    print("\n" + "=" * 60)
    for i, (name, _) in enumerate(PROFILES, 1):
        print(f"  {i}) {name}")
    print(f"  {len(PROFILES) + 1}) Build your own profile")
    print(f"  {len(PROFILES) + 2}) Quit")
    return input("Select an option: ").strip()


def main() -> None:
    songs = load_songs("data/songs.csv")
    retriever = Retriever()

    print("VibeFinder — Music Recommendation System")

    while True:
        try:
            choice = show_menu()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return

        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(PROFILES):
                try:
                    name, prefs = PROFILES[n - 1]
                    run_pipeline(name, prefs, songs, retriever)
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    return
            elif n == len(PROFILES) + 1:
                try:
                    name, prefs = build_custom_profile()
                    run_pipeline(name, prefs, songs, retriever)
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    return
            elif n == len(PROFILES) + 2:
                print("Goodbye!")
                return
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
