# src/recommender.py
"""
Core logic for the Music Recommender Simulation.

This module defines:
- Song: a small container for track metadata
- UserProfile: the user's "taste profile"
- Recommender: loads songs, computes scores, and returns ranked recommendations
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import math
import pathlib
import pandas as pd


@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float          # 0.0 to 1.0
    tempo_bpm: float
    valence: float         # 0.0 = sad, 1.0 = happy
    danceability: float    # 0.0 to 1.0
    acousticness: float    # 0.0 = very electronic, 1.0 = very acoustic

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Song":
        return cls(
            id=int(row["id"]),
            title=str(row["title"]),
            artist=str(row["artist"]),
            genre=str(row["genre"]),
            mood=str(row["mood"]),
            energy=float(row["energy"]),
            tempo_bpm=float(row["tempo_bpm"]),
            valence=float(row["valence"]),
            danceability=float(row["danceability"]),
            acousticness=float(row["acousticness"]),
        )


@dataclass
class UserProfile:
    """
    Simple "taste profile" for one user.

    This is intentionally small.
    Can extend it with more preferences or different scales.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float          # 0.0 to 1.0
    likes_acoustic: bool

    # Optional: could add fields like:
    # tempo_preference: float
    # danceability_bias: float


class Recommender:
    """
    Simple content based recommender that compares a UserProfile
    to each Song and assigns a numeric score.

    Higher scores mean a stronger recommendation.
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    @classmethod
    def from_csv(cls, csv_path: str | pathlib.Path) -> "Recommender":
        df = pd.read_csv(csv_path)
        songs = [Song.from_row(row) for _, row in df.iterrows()]
        return cls(songs)

    def similarity_score(self, user: UserProfile, song: Song) -> float:
        """
        Compute a score for how well song matches user.
        """
        score = 0.0

        # Hard match on genre
        if song.genre.lower() == user.favorite_genre.lower():
            score += 2.0

        # Hard match on mood
        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.5

        # Energy: closer to target is better
        energy_gap = abs(song.energy - user.target_energy)
        score += 1.0 - energy_gap  # value between 0 and 1

        # Acoustic preference: treat acousticness above 0.5 as "acoustic"
        is_acoustic_track = song.acousticness >= 0.5
        if user.likes_acoustic and is_acoustic_track:
            score += 0.5
        if not user.likes_acoustic and not is_acoustic_track:
            score += 0.5

        # Small boost for danceable tracks when energy is high
        if user.target_energy >= 0.7:
            score += 0.3 * song.danceability

        # TODO: Experiment with:
        # - Using tempo_bpm (maybe they prefer mid tempo vs very fast)
        # - Using valence for "happy vs sad" preferences
        # - Penalties for mismatched genres instead of only rewards

        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Rank all songs for this user and return the top k.

        If there are fewer than k songs, returns all of them.
        """
        scored = [
            (self.similarity_score(user, song), song)
            for song in self.songs
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        top_songs = [song for score, song in scored[:k]]
        return top_songs

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Return a short text explanation students can edit or expand.

        The goal is to connect numeric scoring to human friendly reasoning.
        """
        parts: List[str] = []

        if song.genre.lower() == user.favorite_genre.lower():
            parts.append(f"matches your favorite genre {song.genre}")
        if song.mood.lower() == user.favorite_mood.lower():
            parts.append(f"fits your usual mood {song.mood}")
        if abs(song.energy - user.target_energy) <= 0.2:
            parts.append("has a similar energy level")
        if user.likes_acoustic and song.acousticness >= 0.5:
            parts.append("leans acoustic")
        if not user.likes_acoustic and song.acousticness < 0.5:
            parts.append("leans electronic or produced")

        if not parts:
            parts.append("is a bit different from your usual picks, so it may broaden your taste")

        return ", ".join(parts)


def default_recommender() -> Recommender:
    """
    Convenience helper for quick experiments or for cli.py.
    """
    here = pathlib.Path(__file__).resolve().parent
    csv_path = here.parent / "data" / "songs.csv"
    return Recommender.from_csv(csv_path)


if __name__ == "__main__":
    # Tiny manual smoke test for developers
    rec = default_recommender()
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    top = rec.recommend(user, k=3)
    print("Top picks for test profile:")
    for s in top:
        print(f"- {s.title} by {s.artist}")
