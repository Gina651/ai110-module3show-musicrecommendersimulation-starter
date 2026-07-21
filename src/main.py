"""
CLI entry point for the Music Recommender Simulation.

Run (from the project root):
    python -m src.main
"""

from .recommender import load_songs, recommend_songs, MAX_POSSIBLE_SCORE

DATA_PATH = "data/songs.csv"

# Default taste profile used for CLI verification: a "pop/happy" listener.
DEFAULT_USER_PREFS = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.80,
    "target_valence": 0.80,
    "target_tempo_bpm": 118,
    "target_danceability": 0.80,
    "target_acousticness": 0.20,
}


def print_recommendations(title, recs):
    """Print a ranked list of recommendation dicts with score and reasons in a readable CLI layout."""
    print(f"\n=== {title} ===")
    for rank, entry in enumerate(recs, start=1):
        song, score, reasons = entry["song"], entry["score"], entry["reasons"]
        print(f"\n{rank}. {song['title']} — {song['artist']} "
              f"[{song['genre']}/{song['mood']}]  "
              f"score={score:.2f} / {MAX_POSSIBLE_SCORE:.2f}")
        for reason in reasons:
            print(f"     - {reason}")


def main():
    """Load the song catalog, run the default pop/happy recommendation, and print the results."""
    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    recs = recommend_songs(DEFAULT_USER_PREFS, songs, k=5)
    print_recommendations("Recommendations for pop/happy listener", recs)

    recs_diverse = recommend_songs(DEFAULT_USER_PREFS, songs, k=5, max_per_artist=1)
    print_recommendations("Same listener, max 1 song per artist", recs_diverse)


if __name__ == "__main__":
    main()
