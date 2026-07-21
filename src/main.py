"""
CLI entry point for the Music Recommender Simulation.

Run from the project root:
    python3 -m src.main
"""

from .recommender import (
    MAX_POSSIBLE_SCORE,
    load_songs,
    recommend_songs,
)

DATA_PATH = "data/songs.csv"


# ----------------------------------------------------------------------
# Regular user profiles
# ----------------------------------------------------------------------

HIGH_ENERGY_POP = {
    "favorite_genre": "pop",
    "favorite_mood": "intense",
    "target_energy": 0.95,
    "target_valence": 0.85,
    "target_tempo_bpm": 135,
    "target_danceability": 0.85,
    "target_acousticness": 0.05,
}

CHILL_LOFI = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.35,
    "target_valence": 0.60,
    "target_tempo_bpm": 75,
    "target_danceability": 0.55,
    "target_acousticness": 0.85,
}

DEEP_INTENSE_ROCK = {
    "favorite_genre": "rock",
    "favorite_mood": "intense",
    "target_energy": 0.90,
    "target_valence": 0.40,
    "target_tempo_bpm": 155,
    "target_danceability": 0.55,
    "target_acousticness": 0.05,
}


# ----------------------------------------------------------------------
# Adversarial and edge-case profiles
# ----------------------------------------------------------------------

# This profile contains conflicting preferences.
# It asks for metal music with a sad mood, but the metal song in the
# catalog may use a different mood such as aggressive.
CONTRADICTORY_METAL_SAD = {
    "favorite_genre": "metal",
    "favorite_mood": "sad",
    "target_energy": 0.95,
    "target_valence": 0.10,
    "target_tempo_bpm": 170,
    "target_danceability": 0.50,
    "target_acousticness": 0.05,
}

# This profile requests a genre that does not exist in the dataset.
# It tests whether the recommender can still rank songs using mood
# and numerical features.
NONEXISTENT_GENRE_KPOP = {
    "favorite_genre": "k-pop",
    "favorite_mood": "happy",
    "target_energy": 0.80,
    "target_valence": 0.85,
    "target_tempo_bpm": 120,
    "target_danceability": 0.85,
    "target_acousticness": 0.20,
}


PROFILES = [
    ("High-Energy Pop", HIGH_ENERGY_POP),
    ("Chill Lofi", CHILL_LOFI),
    ("Deep Intense Rock", DEEP_INTENSE_ROCK),
    (
        "ADVERSARIAL: Metal genre + Sad mood",
        CONTRADICTORY_METAL_SAD,
    ),
    (
        "ADVERSARIAL: K-pop genre not in catalog",
        NONEXISTENT_GENRE_KPOP,
    ),
]


def print_recommendations(title, recommendations):
    """
    Print a ranked list of recommendations with scores and explanations.
    """

    print(f"\n=== {title} ===")

    for rank, entry in enumerate(recommendations, start=1):
        song = entry["song"]
        score = entry["score"]
        reasons = entry["reasons"]

        print(
            f"\n{rank}. {song['title']} — {song['artist']} "
            f"[{song['genre']}/{song['mood']}] "
            f"score={score:.2f} / {MAX_POSSIBLE_SCORE:.2f}"
        )

        for reason in reasons:
            print(f"     - {reason}")


def main():
    """
    Load the song catalog and run the recommender for every profile.
    """

    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    for profile_name, preferences in PROFILES:
        recommendations = recommend_songs(
            preferences,
            songs,
            k=5,
        )

        print_recommendations(
            profile_name,
            recommendations,
        )


if __name__ == "__main__":
    main()