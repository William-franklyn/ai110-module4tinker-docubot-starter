"""evaluate.py — stress-test the recommender with targeted experiments.

Five experiments, each designed to expose a specific behaviour or weakness:

  1. Perfect Match     — profile engineered to match one song exactly
  2. Orphan Genre      — preferred genre not in the catalog at all
  3. Contradictory     — high energy target paired with a peaceful mood label
  4. Genre vs No-Genre — compare specific genre vs "any" for the same listener
  5. Score Spread      — how discriminating is the system across all 18 songs?

Run with:  python -m src.evaluate
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from recommender import load_songs, score_song, recommend_songs, MAX_SCORE

WIDTH = 62


def divider(char="-"):
    print("  " + char * WIDTH)


def header(title):
    print()
    divider("=")
    print(f"  EXPERIMENT: {title}")
    divider("=")


def show_result(rank, song, score, reasons, show_reasons=True):
    bar = "[" + "#" * int((score / MAX_SCORE) * 20) + "." * (20 - int((score / MAX_SCORE) * 20)) + "]"
    print(f"\n  #{rank}  {song['title']} by {song['artist']}")
    print(f"       Score : {score:.2f} / {MAX_SCORE:.1f}  {bar}")
    if show_reasons:
        for r in reasons:
            tag = "  +" if ("match" in r and "mismatch" not in r) else "  ~"
            print(f"       {tag} {r}")


# ---------------------------------------------------------------------------
# Experiment 1 — Perfect Match
# ---------------------------------------------------------------------------
# Profile is hand-crafted to mirror Smells Like Teen Spirit exactly.
# If the scorer is working correctly this song should dominate with a score
# very close to (but not quite) 9.0 because floating-point proximity is
# never a perfect 1.0 unless the values are identical.

def experiment_perfect_match(songs):
    header("1 — Perfect Match")
    print("  Profile engineered to match 'Smells Like Teen Spirit' exactly.")
    print("  Expected: that song scores ~8.9+ and leads by a large margin.\n")

    profile = {
        "name":               "Perfect Rock",
        "preferred_genre":    "grunge",
        "preferred_mood":     "angry",
        "preferred_mode":     "minor",
        "target_energy":       0.92,
        "target_valence":      0.41,
        "target_tempo_bpm":    117,
        "target_danceability": 0.48,
        "target_acousticness": 0.00,
    }

    results = recommend_songs(profile, songs, k=3)
    for rank, (song, score, reasons) in enumerate(results, 1):
        show_result(rank, song, score, reasons)

    top_score = results[0][1]
    gap = top_score - results[1][1]
    print(f"\n  Result: #{1} scored {top_score:.2f}. Gap to #2: {gap:.2f} pts.")
    if gap >= 2.5:
        print("  Verdict: STRONG separation — perfect profile isolates the target song.")
    else:
        print("  Verdict: WEAK separation — scoring is not discriminating enough.")


# ---------------------------------------------------------------------------
# Experiment 2 — Orphan Genre
# ---------------------------------------------------------------------------
# preferred_genre is "jazz" — a genre that does not appear anywhere in the
# catalog.  Nobody gets genre points.  The system should fall back entirely
# on mood + numerical proximity.  Scores will compress into a narrow band
# and the top result will be whoever wins on mood + energy, not genre.

def experiment_orphan_genre(songs):
    header("2 — Orphan Genre")
    print("  preferred_genre = 'jazz'  (not in catalog).")
    print("  Nobody earns genre points. Expect scores clustered in 4–6 range.\n")

    profile = {
        "name":               "Jazz Hunter",
        "preferred_genre":    "jazz",
        "preferred_mood":     "chill",
        "preferred_mode":     "minor",
        "target_energy":       0.30,
        "target_valence":      0.45,
        "target_tempo_bpm":    90,
        "target_danceability": 0.60,
        "target_acousticness": 0.30,
    }

    results = recommend_songs(profile, songs, k=5)
    scores = [s for _, s, _ in results]
    for rank, (song, score, reasons) in enumerate(results, 1):
        show_result(rank, song, score, reasons, show_reasons=False)
        print(f"       Genre in catalog: {song['genre']}")

    print(f"\n  Score range (top 5): {min(scores):.2f} – {max(scores):.2f}")
    print(f"  Spread: {max(scores) - min(scores):.2f} pts  "
          f"(vs ~3+ pts when genre matches)")
    print("  Verdict: genre mismatch collapses scores and weakens discrimination.")


# ---------------------------------------------------------------------------
# Experiment 3 — Contradictory Profile
# ---------------------------------------------------------------------------
# High energy (0.90) + peaceful mood.  No song in the catalog is both
# high-energy AND peaceful — the two features pull in opposite directions.
# This exposes a real weakness: the system cannot synthesise a song that
# doesn't exist.  It will promote whichever imperfect compromise scores best.

def experiment_contradictory(songs):
    header("3 — Contradictory Profile (high energy + peaceful mood)")
    print("  target_energy=0.90  preferred_mood='peaceful'.")
    print("  No song in the catalog satisfies both. Watch for compromise picks.\n")

    profile = {
        "name":               "Walking Contradiction",
        "preferred_genre":    "any",
        "preferred_mood":     "peaceful",
        "preferred_mode":     "any",
        "target_energy":       0.90,
        "target_valence":      0.55,
        "target_tempo_bpm":    120,
        "target_danceability": 0.55,
        "target_acousticness": 0.10,
    }

    results = recommend_songs(profile, songs, k=5)
    print("  Top 5 (showing score + genre/mood for each):")
    for rank, (song, score, _) in enumerate(results, 1):
        print(f"  #{rank}  [{score:.2f}]  {song['title']}")
        print(f"        mood={song['mood']}  energy={song['energy']}  genre={song['genre']}")

    top = results[0][0]
    print(f"\n  Winner: {top['title']} (mood={top['mood']}, energy={top['energy']})")
    print("  Verdict: system picks the least-wrong song, not a right one.")
    print("  This is a known limitation of static profiles with no feedback loop.")


# ---------------------------------------------------------------------------
# Experiment 4 — Specific Genre vs 'any'
# ---------------------------------------------------------------------------
# Same listener (euphoric, happy, high energy) with genre='pop' vs genre='any'.
# Measures exactly how much the 2.0 genre points shift the rankings.

def experiment_genre_weight(songs):
    header("4 — Genre Weight Impact  (pop vs any)")
    print("  Same listener preferences, genre='pop' vs genre='any'.")
    print("  Shows how much 2.0 genre points shift the final ranking.\n")

    base = {
        "name":               "Casey",
        "preferred_mood":     "euphoric",
        "preferred_mode":     "major",
        "target_energy":       0.78,
        "target_valence":      0.85,
        "target_tempo_bpm":    110,
        "target_danceability": 0.72,
        "target_acousticness": 0.05,
    }

    with_genre    = {**base, "preferred_genre": "pop",  "name": "Casey (genre=pop)"}
    without_genre = {**base, "preferred_genre": "any",  "name": "Casey (genre=any)"}

    results_with    = recommend_songs(with_genre,    songs, k=5)
    results_without = recommend_songs(without_genre, songs, k=5)

    print(f"  {'Rank':<6} {'genre=pop':<32} {'genre=any'}")
    print(f"  {'-'*6} {'-'*32} {'-'*28}")
    for i in range(5):
        s_w = results_with[i][0]["title"][:28]
        sc_w = results_with[i][1]
        s_wo = results_without[i][0]["title"][:28]
        sc_wo = results_without[i][1]
        print(f"  #{i+1:<5} {s_w:<28} {sc_w:.2f}   {s_wo:<28} {sc_wo:.2f}")

    print()
    # Find Blinding Lights score in both
    for song, score, _ in results_with:
        if song["title"] == "Blinding Lights":
            bl_with = score
    for song, score, _ in results_without:
        if song["title"] == "Blinding Lights":
            bl_without = score
    print(f"  'Blinding Lights' score:  {bl_with:.2f} (with genre)  vs  {bl_without:.2f} (any)")
    print(f"  Genre bonus: +{bl_with - bl_without:.2f} pts — that is "
          f"{((bl_with - bl_without) / MAX_SCORE * 100):.0f}% of the max score.")
    print("  Verdict: genre lock-in is powerful — it can suppress great songs")
    print("  that don't carry the right label.")


# ---------------------------------------------------------------------------
# Experiment 5 — Score Spread
# ---------------------------------------------------------------------------
# For each of the four main profiles, score ALL 18 songs and show the
# distribution.  A healthy recommender should separate good matches from bad
# ones clearly.  If the spread is too narrow, the ranking is nearly random.

def experiment_score_spread(songs):
    header("5 — Score Spread Across Full Catalog")
    print("  Scores all 18 songs per profile and reports min/max/mean/spread.")
    print("  A wide spread means the system is discriminating well.\n")

    profiles = [
        {"name": "Casey",  "preferred_genre": "pop",    "preferred_mood": "euphoric",
         "preferred_mode": "major",  "target_energy": 0.78, "target_valence": 0.85,
         "target_tempo_bpm": 110,    "target_danceability": 0.72, "target_acousticness": 0.05},
        {"name": "Riley",  "preferred_genre": "grunge", "preferred_mood": "angry",
         "preferred_mode": "minor",  "target_energy": 0.88, "target_valence": 0.35,
         "target_tempo_bpm": 125,    "target_danceability": 0.45, "target_acousticness": 0.02},
        {"name": "Morgan", "preferred_genre": "any",    "preferred_mood": "chill",
         "preferred_mode": "minor",  "target_energy": 0.25, "target_valence": 0.40,
         "target_tempo_bpm": 85,     "target_danceability": 0.55, "target_acousticness": 0.35},
        {"name": "Drew",   "preferred_genre": "folk",   "preferred_mood": "peaceful",
         "preferred_mode": "major",  "target_energy": 0.28, "target_valence": 0.52,
         "target_tempo_bpm": 80,     "target_danceability": 0.38, "target_acousticness": 0.82},
    ]

    print(f"  {'Profile':<10} {'Min':>5} {'Max':>5} {'Mean':>5} {'Spread':>7} {'Top song'}")
    print(f"  {'-'*10} {'-'*5} {'-'*5} {'-'*5} {'-'*7} {'-'*28}")

    for profile in profiles:
        all_scored = recommend_songs(profile, songs, k=len(songs))
        all_scores = [s for _, s, _ in all_scored]
        lo, hi = min(all_scores), max(all_scores)
        mean = sum(all_scores) / len(all_scores)
        spread = hi - lo
        top = all_scored[0][0]["title"][:26]
        print(f"  {profile['name']:<10} {lo:>5.2f} {hi:>5.2f} {mean:>5.2f} {spread:>7.2f}   {top}")

    print()
    print("  Spread interpretation:")
    print("  < 2.0 pts  — weak discrimination, rankings nearly random")
    print("  2.0–4.0    — moderate, system finds a preference but noisily")
    print("  > 4.0 pts  — strong discrimination, top picks are clearly right")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    songs = load_songs()
    print(f"\n  Loaded {len(songs)} songs. Running 5 evaluation experiments...")

    experiment_perfect_match(songs)
    experiment_orphan_genre(songs)
    experiment_contradictory(songs)
    experiment_genre_weight(songs)
    experiment_score_spread(songs)

    print()
    divider("=")
    print("  Evaluation complete.")
    divider("=")
    print()


if __name__ == "__main__":
    main()
