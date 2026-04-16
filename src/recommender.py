import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV and return a list of normalized song dictionaries."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Compute a song score and return reasons explaining the match."""
    total_score = 0.0
    reasons: List[str] = []

    if song.get("genre") == user_prefs.get("genre"):
        total_score += 2.0
        reasons.append("genre match (+2.0)")

    if song.get("mood") == user_prefs.get("mood"):
        total_score += 1.0
        reasons.append("mood match (+1.0)")

    energy_target = float(user_prefs.get("energy", 0.0))
    energy_score = 1.0 - abs(song.get("energy", 0.0) - energy_target)
    total_score += energy_score
    reasons.append(f"energy proximity ({energy_score:.2f})")

    acoustic_target = float(user_prefs.get("acousticness", 0.0))
    acoustic_score = 1.0 - abs(song.get("acousticness", 0.0) - acoustic_target)
    total_score += acoustic_score
    reasons.append(f"acousticness proximity ({acoustic_score:.2f})")

    return total_score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score each song and return the top k recommendations ordered by score."""
    scored_songs = [
        (song, score, "; ".join(reasons))
        for song, (score, reasons) in ((song, score_song(user_prefs, song)) for song in songs)
    ]

    ranked_songs = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    return ranked_songs[:k]
