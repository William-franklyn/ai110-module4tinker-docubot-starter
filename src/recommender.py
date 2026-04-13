import csv
from pathlib import Path

# Path to the song catalog relative to this file
DATA_PATH = Path(__file__).parent.parent / "data" / "songs.csv"

# Fields that must be numbers so we can do math with them later
FLOAT_FIELDS = {"energy", "valence", "danceability", "acousticness", "instrumentalness"}
INT_FIELDS   = {"id", "tempo_bpm", "popularity"}


def load_songs(filepath=DATA_PATH):
    """Read songs.csv and return a list of dictionaries.

    Every row comes back as a dict whose keys match the CSV headers.
    Numerical columns are converted to int or float so arithmetic
    (like subtraction for proximity scoring) works without extra casting.

    Example row returned:
        {
            "id": 1,
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "genre": "pop",
            "mood": "euphoric",
            "energy": 0.8,
            "valence": 0.33,
            "tempo_bpm": 171,
            "danceability": 0.51,
            "acousticness": 0.0,
            "instrumentalness": 0.0,
            "mode": "major",
            "popularity": 97,
        }
    """
    songs = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            song = {}
            for key, value in row.items():
                if key in FLOAT_FIELDS:
                    song[key] = float(value)
                elif key in INT_FIELDS:
                    song[key] = int(value)
                else:
                    song[key] = value   # keep as string (title, artist, genre, mood, mode)
            songs.append(song)

    return songs


def score_song(song, user_profile):
    """Score one song against a user profile.

    Returns a tuple of (score, reasons):
        score   — total points earned, float in range 0.0 to 9.0
        reasons — list of strings explaining every point contribution

    Categorical rules (binary — full points or zero):
        genre match  ->  +2.0
        mood  match  ->  +1.5
        mode  match  ->  +0.5

    Continuous rules (proximity — fraction of max points):
        Each earns  max_pts x (1.0 - |user_target - song_value|)
        energy       ->  up to +2.0
        valence      ->  up to +1.0
        tempo_bpm    ->  up to +1.0  (normalised over 200 BPM ceiling)
        danceability ->  up to +0.5
        acousticness ->  up to +0.5

    Maximum possible score: 9.0
    """
    score = 0.0
    reasons = []

    # --- categorical: genre ---
    if user_profile["preferred_genre"] in ("any", song["genre"]):
        pts = 2.0
        score += pts
        reasons.append(f"genre match '{song['genre']}' (+{pts})")
    else:
        reasons.append(
            f"genre mismatch: wanted '{user_profile['preferred_genre']}', "
            f"got '{song['genre']}' (+0.0)"
        )

    # --- categorical: mood ---
    if user_profile["preferred_mood"] in ("any", song["mood"]):
        pts = 1.5
        score += pts
        reasons.append(f"mood match '{song['mood']}' (+{pts})")
    else:
        reasons.append(
            f"mood mismatch: wanted '{user_profile['preferred_mood']}', "
            f"got '{song['mood']}' (+0.0)"
        )

    # --- categorical: mode ---
    if user_profile["preferred_mode"] in ("any", song["mode"]):
        pts = 0.5
        score += pts
        reasons.append(f"mode match '{song['mode']}' (+{pts})")
    else:
        reasons.append(
            f"mode mismatch: wanted '{user_profile['preferred_mode']}', "
            f"got '{song['mode']}' (+0.0)"
        )

    # --- continuous: energy ---
    pts = round(2.0 * (1.0 - abs(user_profile["target_energy"] - song["energy"])), 2)
    score += pts
    reasons.append(
        f"energy {song['energy']} vs target {user_profile['target_energy']} (+{pts})"
    )

    # --- continuous: valence ---
    pts = round(1.0 * (1.0 - abs(user_profile["target_valence"] - song["valence"])), 2)
    score += pts
    reasons.append(
        f"valence {song['valence']} vs target {user_profile['target_valence']} (+{pts})"
    )

    # --- continuous: tempo ---
    pts = round(1.0 * (1.0 - abs(user_profile["target_tempo_bpm"] - song["tempo_bpm"]) / 200), 2)
    score += pts
    reasons.append(
        f"tempo {song['tempo_bpm']} BPM vs target {user_profile['target_tempo_bpm']} BPM (+{pts})"
    )

    # --- continuous: danceability ---
    pts = round(0.5 * (1.0 - abs(user_profile["target_danceability"] - song["danceability"])), 2)
    score += pts
    reasons.append(
        f"danceability {song['danceability']} vs target {user_profile['target_danceability']} (+{pts})"
    )

    # --- continuous: acousticness ---
    pts = round(0.5 * (1.0 - abs(user_profile["target_acousticness"] - song["acousticness"])), 2)
    score += pts
    reasons.append(
        f"acousticness {song['acousticness']} vs target {user_profile['target_acousticness']} (+{pts})"
    )

    return round(score, 3), reasons


def recommend_songs(user_prefs, songs, k=5):
    """Score every song against user_prefs and return the top k matches.

    Returns a list of (song, score, reasons) tuples, best match first.
    Ties are broken by popularity (higher popularity wins).

    --- sorted() vs .sort() ---

    There are two ways to sort in Python, and they behave very differently:

    .sort()   — sorts the list IN PLACE and returns None.
                The original list is permanently reordered.
                If you called  songs.sort(...)  here, the caller's catalog
                would come back shuffled every time they asked for recs.
                That's a sneaky bug — hard to notice, hard to trace.

    sorted()  — takes any iterable, returns a BRAND NEW sorted list,
                and leaves the original completely untouched.
                This is the right choice here because:
                  1. We don't own the catalog — we should never mutate it.
                  2. The caller can ask for recs multiple times without
                     the list getting silently reshuffled between calls.
                  3. sorted() works on any iterable (lists, tuples,
                     generators) not just lists.

    The Pythonic idiom for "score everything, sort by score, take top k":

        scored = sorted(iterable, key=fn, reverse=True)[:k]

    The key= argument tells sorted() what value to sort by.
    reverse=True means highest score first (descending order).
    Slicing [:k] gives us only the top k results.
    """
    # Build (song, score, reasons) for every song in one pass
    scored = [
        (song, *score_song(song, user_prefs))   # * unpacks the (score, reasons) tuple
        for song in songs
    ]

    # sorted() returns a new list — the original `songs` catalog is untouched.
    # Primary key: score (higher is better).
    # Tiebreaker: popularity (also higher is better).
    ranked = sorted(scored, key=lambda t: (t[1], t[0]["popularity"]), reverse=True)

    return ranked[:k]
