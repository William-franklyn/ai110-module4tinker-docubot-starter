import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from recommender import load_songs, recommend_songs, MAX_SCORE

# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Standard profiles — realistic listener archetypes
# ---------------------------------------------------------------------------

STANDARD_PROFILES = {
    "high_energy_pop": {
        "name":               "High-Energy Pop",
        "preferred_genre":    "pop",
        "preferred_mood":     "euphoric",
        "preferred_mode":     "major",
        "target_energy":       0.85,
        "target_valence":      0.90,   # very happy
        "target_tempo_bpm":    125,
        "target_danceability": 0.85,   # wants to dance
        "target_acousticness": 0.02,
    },
    "chill_lofi": {
        "name":               "Chill Lofi",
        "preferred_genre":    "any",   # lofi spans r&b, hip-hop, soul
        "preferred_mood":     "chill",
        "preferred_mode":     "minor",
        "target_energy":       0.18,   # barely audible, background
        "target_valence":      0.35,
        "target_tempo_bpm":    72,     # slow enough to think over
        "target_danceability": 0.48,
        "target_acousticness": 0.45,   # warm, textured
    },
    "deep_intense_rock": {
        "name":               "Deep Intense Rock",
        "preferred_genre":    "rock",
        "preferred_mood":     "angry",
        "preferred_mode":     "minor",
        "target_energy":       0.92,   # maximum loudness
        "target_valence":      0.22,   # dark
        "target_tempo_bpm":    130,
        "target_danceability": 0.38,   # not a dance track
        "target_acousticness": 0.01,   # fully electric
    },
}

# ---------------------------------------------------------------------------
# Adversarial profiles — designed to expose edge cases and scoring quirks
# ---------------------------------------------------------------------------

ADVERSARIAL_PROFILES = {
    "sad_bangers": {
        # Conflict: very high energy (0.90) but wants melancholy mood.
        # No song in the catalog is both loud and melancholy.
        # Watch whether energy or mood wins the tiebreak.
        "name":               "Sad Bangers (adversarial)",
        "preferred_genre":    "any",
        "preferred_mood":     "melancholy",
        "preferred_mode":     "minor",
        "target_energy":       0.90,
        "target_valence":      0.20,
        "target_tempo_bpm":    140,
        "target_danceability": 0.60,
        "target_acousticness": 0.05,
    },
    "the_completist": {
        # Every preference is dead-centre (0.5 / "any").
        # All songs should score very similarly — no real discrimination.
        # Reveals how much the system relies on categorical matches.
        "name":               "The Completist (adversarial)",
        "preferred_genre":    "any",
        "preferred_mood":     "any",
        "preferred_mode":     "any",
        "target_energy":       0.50,
        "target_valence":      0.50,
        "target_tempo_bpm":    100,
        "target_danceability": 0.50,
        "target_acousticness": 0.50,
    },
    "classical_purist": {
        # Wants classical music at near-zero energy.
        # Only 2 classical songs exist. Tests catalog thinness.
        # Also: very slow tempo (68 BPM) and high acousticness.
        "name":               "Classical Purist (adversarial)",
        "preferred_genre":    "classical",
        "preferred_mood":     "peaceful",
        "preferred_mode":     "minor",
        "target_energy":       0.01,
        "target_valence":      0.20,
        "target_tempo_bpm":    68,
        "target_danceability": 0.18,
        "target_acousticness": 0.99,
    },
}

# Run all profiles in this order
PROFILES = {**STANDARD_PROFILES, **ADVERSARIAL_PROFILES}

WIDTH = 60


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def divider(char="-"):
    print("  " + char * WIDTH)


def score_bar(score, max_score=MAX_SCORE, width=20):
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
        print(f"       Score : {score:.2f} / {MAX_SCORE:.1f}  {bar}")
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

    print("\n  -- STANDARD PROFILES --\n")
    for profile in STANDARD_PROFILES.values():
        print_recommendations(songs, profile, top_n=5)

    print("\n  -- ADVERSARIAL PROFILES --\n")
    for profile in ADVERSARIAL_PROFILES.values():
        print_recommendations(songs, profile, top_n=5)


if __name__ == "__main__":
    main()
