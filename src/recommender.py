"""
Core recommender logic: load songs from CSV, score them against a user's
taste profile, and rank the results.

Algorithm Recipe:

    +2.0 points  — exact genre match
    +1.0 point   — exact mood match
    up to 1.0    — energy closeness
    up to 0.75   — valence closeness
    up to 0.5    — tempo closeness
    up to 0.5    — danceability closeness
    up to 0.25   — acousticness closeness
    ------------------------------------
    6.0 points   — maximum possible total score
"""

import csv
from dataclasses import dataclass


# Point values for the scoring algorithm.
GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_MAX_POINTS = 1.0
VALENCE_MAX_POINTS = 0.75
TEMPO_MAX_POINTS = 0.5
DANCEABILITY_MAX_POINTS = 0.5
ACOUSTICNESS_MAX_POINTS = 0.25

MAX_POSSIBLE_SCORE = (
    GENRE_MATCH_POINTS
    + MOOD_MATCH_POINTS
    + ENERGY_MAX_POINTS
    + VALENCE_MAX_POINTS
    + TEMPO_MAX_POINTS
    + DANCEABILITY_MAX_POINTS
    + ACOUSTICNESS_MAX_POINTS
)

TEMPO_RANGE = 120.0


@dataclass
class Song:
    """Represent one song and its musical features."""

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
    """Represent a listener's music preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool = False


class Recommender:
    """Rank Song objects according to a UserProfile."""

    def __init__(self, songs):
        """Store the song catalog."""

        self.songs = songs

    def _score(self, user, song):
        """Calculate a numeric score for one Song object."""

        score = 0.0

        if song.genre.lower() == user.favorite_genre.lower():
            score += GENRE_MATCH_POINTS

        if song.mood.lower() == user.favorite_mood.lower():
            score += MOOD_MATCH_POINTS

        score += _numeric_closeness_points(
            song.energy,
            user.target_energy,
            1.0,
            ENERGY_MAX_POINTS,
        )

        if user.likes_acoustic:
            score += song.acousticness * ACOUSTICNESS_MAX_POINTS
        else:
            score += (
                1.0 - song.acousticness
            ) * ACOUSTICNESS_MAX_POINTS

        return score

    def recommend(self, user, k=5):
        """Return the top-k highest-scoring Song objects."""

        ranked = sorted(
            self.songs,
            key=lambda song: self._score(user, song),
            reverse=True,
        )

        return ranked[:k]

    def explain_recommendation(self, user, song):
        """Return a readable explanation for one recommendation."""

        reasons = []

        if song.genre.lower() == user.favorite_genre.lower():
            reasons.append("genre match")

        if song.mood.lower() == user.favorite_mood.lower():
            reasons.append("mood match")

        energy_difference = abs(
            song.energy - user.target_energy
        )

        if energy_difference <= 0.10:
            reasons.append(
                "energy is very close to your preference"
            )
        elif energy_difference <= 0.25:
            reasons.append(
                "energy is close to your preference"
            )

        if user.likes_acoustic and song.acousticness >= 0.60:
            reasons.append("strong acoustic sound")
        elif not user.likes_acoustic and song.acousticness < 0.40:
            reasons.append("low acousticness")

        if not reasons:
            reasons.append(
                "some musical features match your preferences"
            )

        return ", ".join(reasons)


def load_songs(path="data/songs.csv"):
    """Load song dictionaries from a CSV file."""

    songs = []

    with open(
        path,
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"].strip(),
                    "artist": row["artist"].strip(),
                    "genre": row["genre"].strip().lower(),
                    "mood": row["mood"].strip().lower(),
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(
                        row["danceability"]
                    ),
                    "acousticness": float(
                        row["acousticness"]
                    ),
                }
            )

    return songs


def _numeric_closeness_points(
    song_value,
    target_value,
    value_range,
    max_points,
):
    """Calculate points based on numerical closeness."""

    distance = abs(song_value - target_value)
    normalized_distance = min(
        distance / value_range,
        1.0,
    )
    closeness_fraction = 1.0 - normalized_distance

    return closeness_fraction * max_points


def score_song(user_prefs, song):
    """Return a song's score and explanation reasons."""

    reasons = []
    total = 0.0

    favorite_genre = (
        user_prefs["favorite_genre"]
        .strip()
        .lower()
    )

    favorite_mood = (
        user_prefs["favorite_mood"]
        .strip()
        .lower()
    )

    if song["genre"] == favorite_genre:
        total += GENRE_MATCH_POINTS
        reasons.append(
            f"genre match (+{GENRE_MATCH_POINTS:.2f})"
        )
    else:
        reasons.append(
            f"genre mismatch "
            f"({song['genre']} vs {favorite_genre}) "
            f"(+0.00)"
        )

    if song["mood"] == favorite_mood:
        total += MOOD_MATCH_POINTS
        reasons.append(
            f"mood match (+{MOOD_MATCH_POINTS:.2f})"
        )
    else:
        reasons.append(
            f"mood mismatch "
            f"({song['mood']} vs {favorite_mood}) "
            f"(+0.00)"
        )

    numeric_features = [
        (
            "energy",
            "target_energy",
            1.0,
            ENERGY_MAX_POINTS,
        ),
        (
            "valence",
            "target_valence",
            1.0,
            VALENCE_MAX_POINTS,
        ),
        (
            "tempo_bpm",
            "target_tempo_bpm",
            TEMPO_RANGE,
            TEMPO_MAX_POINTS,
        ),
        (
            "danceability",
            "target_danceability",
            1.0,
            DANCEABILITY_MAX_POINTS,
        ),
        (
            "acousticness",
            "target_acousticness",
            1.0,
            ACOUSTICNESS_MAX_POINTS,
        ),
    ]

    for (
        song_key,
        preference_key,
        value_range,
        max_points,
    ) in numeric_features:
        points = _numeric_closeness_points(
            song[song_key],
            user_prefs[preference_key],
            value_range,
            max_points,
        )

        total += points

        reasons.append(
            f"{song_key} close to target "
            f"(+{points:.2f})"
        )

    return total, reasons


def recommend_songs(
    user_prefs,
    songs,
    k=5,
    max_per_artist=None,
):
    """Return the top-ranked songs with scores and reasons."""

    scored = []

    for song in songs:
        score, reasons = score_song(
            user_prefs,
            song,
        )

        scored.append(
            {
                "song": song,
                "score": score,
                "reasons": reasons,
            }
        )

    ranked = sorted(
        scored,
        key=lambda entry: entry["score"],
        reverse=True,
    )

    if max_per_artist is None:
        return ranked[:k]

    result = []
    artist_counts = {}

    for entry in ranked:
        artist = entry["song"]["artist"]

        if (
            artist_counts.get(artist, 0)
            >= max_per_artist
        ):
            continue

        result.append(entry)

        artist_counts[artist] = (
            artist_counts.get(artist, 0) + 1
        )

        if len(result) == k:
            break

    return result