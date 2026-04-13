import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from recommender import load_songs, recommend_songs

# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

PROFILES = {
    "casey": {                          # DEFAULT — pop / happy
        "name":               "Casey",
        "preferred_genre":    "pop",
        "preferred_mood":     "euphoric",
        "preferred_mode":     "major",
        "target_energy":       0.78,
        "target_valence":      0.85,
        "target_tempo_bpm":    110,
        "target_danceability": 0.72,
        "target_acousticness": 0.05,
    },
    "riley": {
        "name":               "Riley",
        "preferred_genre":    "grunge",
        "preferred_mood":     "angry",
        "preferred_mode":     "minor",
        "target_energy":       0.88,
        "target_valence":      0.35,
        "target_tempo_bpm":    125,
        "target_danceability": 0.45,
        "target_acousticness": 0.02,
    },
    "morgan": {
        "name":               "Morgan",
        "preferred_genre":    "any",
        "preferred_mood":     "chill",
        "preferred_mode":     "minor",
        "target_energy":       0.25,
        "target_valence":      0.40,
        "target_tempo_bpm":    85,
        "target_danceability": 0.55,
        "target_acousticness": 0.35,
    },
    "drew": {
        "name":               "Drew",
        "preferred_genre":    "folk",
        "preferred_mood":     "peaceful",
        "preferred_mode":     "major",
        "target_energy":       0.28,
        "target_valence":      0.52,
        "target_tempo_bpm":    80,
        "target_danceability": 0.38,
        "target_acousticness": 0.82,
    },
}

WIDTH = 60


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def divider(char="-"):
    print("  " + char * WIDTH)


def score_bar(score, max_score=9.0, width=20):
    filled = int((score / max_score) * width)
    return "[" + "#" * filled + "." * (width - filled) + "]"


def print_profile_header(profile):
    divider("=")
    print(f"  Listener : {profile['name']}")
    print(f"  Genre    : {profile['preferred_genre']}   "
          f"Mood: {profile['preferred_mood']}   "
          f"Mode: {profile['preferred_mode']}")
    print(f"  Energy   : {profile['target_energy']}   "
          f"Valence: {profile['target_valence']}   "
          f"Tempo: {profile['target_tempo_bpm']} BPM")
    divider("=")


def print_recommendations(songs, profile, top_n=5):
    print_profile_header(profile)

    results = recommend_songs(profile, songs, k=top_n)

    for rank, (song, score, reasons) in enumerate(results, start=1):
        bar = score_bar(score)
        print(f"\n  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Score : {score:.2f} / 9.0  {bar}")
        print(f"       Genre : {song['genre']}  |  "
              f"Mood: {song['mood']}  |  "
              f"Energy: {song['energy']}  |  "
              f"BPM: {song['tempo_bpm']}")
        print(f"       Reasons:")
        for reason in reasons:
            prefix = "  +" if "match" in reason and "mismatch" not in reason else "  ~"
            print(f"         {prefix} {reason}")

    print()
    divider()
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    songs = load_songs()

    print()
    divider("=")
    print(f"  Music Recommender  |  Content-Based Filtering")
    print(f"  Catalog : {len(songs)} songs loaded")
    divider("=")

    for profile in PROFILES.values():
        print_recommendations(songs, profile, top_n=5)


if __name__ == "__main__":
    main()
