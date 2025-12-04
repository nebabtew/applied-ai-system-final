# src/cli.py
"""
Command line interface for the Music Recommender Simulation.

This is intentionally lightweight:
- Ask the user a few questions about their taste
- Build a UserProfile
- Print a ranked list of recommendations plus short explanations

Students can:
- Add more questions
- Support multiple users
- Save and reload simple profiles
"""

from recommender import UserProfile, default_recommender


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} [y/n]: ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer with y or n.")


def ask_float(prompt: str, min_value: float = 0.0, max_value: float = 1.0) -> float:
    while True:
        raw = input(f"{prompt} ({min_value} to {max_value}): ").strip()
        try:
            value = float(raw)
        except ValueError:
            print("Please enter a number.")
            continue
        if min_value <= value <= max_value:
            return value
        print(f"Value must be between {min_value} and {max_value}.")


def build_user_profile() -> UserProfile:
    print("Welcome to the Music Recommender Simulation!")
    print("Answer a few quick questions to set up your vibe profile.\n")

    genre = input("What is your favorite genre (for example, pop, lofi, rock): ").strip()
    mood = input("What is your usual listening mood (for example, chill, happy, intense): ").strip()
    energy = ask_float("On average, how much energy do you like in your music", 0.0, 1.0)
    likes_acoustic = ask_yes_no("Do you usually prefer more acoustic, less produced tracks")

    return UserProfile(
        favorite_genre=genre or "pop",
        favorite_mood=mood or "happy",
        target_energy=energy,
        likes_acoustic=likes_acoustic,
    )


def main() -> None:
    user = build_user_profile()
    recommender = default_recommender()

    print("\nCalculating your top recommendations...\n")
    top_songs = recommender.recommend(user, k=5)

    if not top_songs:
        print("No songs available. Check that data/songs.csv exists.")
        return

    for idx, song in enumerate(top_songs, start=1):
        explanation = recommender.explain_recommendation(user, song)
        print(f"{idx}. {song.title} - {song.artist}")
        print(f"   Why this track: {explanation}")
        print()

    print("Experiment idea: run again with different answers and compare the ranked list.")


if __name__ == "__main__":
    main()
