"""scorer.py — point-based scoring for content-based music recommendation.

Algorithm Recipe
================
Every song is scored against a user profile.  Points are awarded per
feature and summed into a total.  The maximum possible score is 9.0.

  Categorical features  (binary: full points or zero)
  ───────────────────────────────────────────────────
  +2.0   genre match      Biggest single signal — a wrong genre is a
                          dealbreaker for most listeners.
  +1.5   mood  match      Second-strongest vibe signal.  "angry" and
                          "chill" are worlds apart even at the same energy.
  +0.5   mode  match      Minor sounds darker than major — subtle but
                          consistent across listeners.

  Continuous features  (similarity: fraction of max points)
  ──────────────────────────────────────────────────────────
  Each continuous feature earns  max_pts × (1.0 − |user_pref − song_value|).
  This rewards *closeness* to the user's target rather than high or low
  absolute values.  Example: a user who wants energy 0.4 scores a 0.4-energy
  song at the full 2.0 pts and a 0.9-energy song at only 1.0 pt.

  +2.0   energy           Loudness + intensity — immediately perceptible.
                          Mismatches break immersion faster than any other
                          feature, so it shares the top slot with genre.
  +1.0   valence          Musical positivity (0 = sad/dark, 1 = happy/bright).
                          Refines the emotional tone within the energy envelope.
  +1.0   tempo_bpm        Beats per minute, normalised to 0–1 over a 200-BPM
                          ceiling before the proximity formula is applied.
  +0.5   danceability     Groove quality — useful for separating head-bob
                          rock from dance-floor pop at similar energies.
  +0.5   acousticness     Electric vs. acoustic texture — the cleanest axis
                          for separating rock (≈0.0) from folk/lofi (≈0.8).

  Maximum total: 2.0 + 1.5 + 0.5 + 2.0 + 1.0 + 1.0 + 0.5 + 0.5 = 9.0

Why genre outranks mood
───────────────────────
  A sad hip-hop track and a sad classical piece share a mood label but
  feel nothing alike.  Genre is the outer envelope; mood refines within it.

Why energy ties with genre
──────────────────────────
  Genre is categorical — you either match or you don't.  Energy is
  continuous and perceptible at every step.  Giving it the same ceiling
  (2.0) ensures that a near-perfect energy match on a slightly different
  genre still scores competitively, which produces more nuanced rankings.

Why acousticness weight was raised (vs. earlier draft)
───────────────────────────────────────────────────────
  Acousticness is the clearest axis between "intense rock" (≈0.0) and
  "chill lofi" (≈0.3–0.6).  An earlier version weighted it at 0.03 × 1.0,
  producing a max contribution of 0.03 — almost invisible.  At 0.5 pts it
  now meaningfully pushes acoustic-heavy songs up for acoustic listeners
  without dominating the ranking.
"""

from .song import Song
from .user_profile import UserProfile

# ---------------------------------------------------------------------------
# Point ceilings per feature  (must stay in sync with the docstring table)
# ---------------------------------------------------------------------------

MAX_POINTS: dict[str, float] = {
    # categorical
    "genre":        2.0,
    "mood":         1.5,
    "mode":         0.5,
    # continuous
    "energy":       2.0,
    "valence":      1.0,
    "tempo_bpm":    1.0,
    "danceability": 0.5,
    "acousticness": 0.5,
}

MAX_SCORE: float = sum(MAX_POINTS.values())   # 9.0

_MAX_BPM = 200   # normalisation ceiling for tempo proximity


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _category_pts(max_pts: float, user_pref: str, song_value: str) -> float:
    """Full points if they match (or user said 'any'), else 0."""
    if user_pref.lower() == "any":
        return max_pts
    return max_pts if user_pref.lower() == song_value.lower() else 0.0


def _proximity_pts(max_pts: float, user_pref: float, song_value: float) -> float:
    """Continuous similarity points for features already on [0, 1].

    Formula: max_pts × (1.0 − |user_pref − song_value|)
    Result range: 0.0  (opposite ends of scale)  →  max_pts  (exact match)
    """
    return max_pts * (1.0 - abs(user_pref - song_value))


def _tempo_pts(max_pts: float, user_bpm: int, song_bpm: int) -> float:
    """Normalise BPM to [0, 1] then apply the same proximity formula."""
    return max_pts * (1.0 - abs(user_bpm - song_bpm) / _MAX_BPM)


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def score_song(song: Song, user: UserProfile) -> float:
    """Return the total point score for one song vs. one user profile.

    Score is in [0.0, MAX_SCORE] (max = 9.0).
    Higher means a better match.

    Songs in user.liked_ids / disliked_ids are NOT filtered here —
    the engine handles that before calling this function.
    """
    return (
        _category_pts (MAX_POINTS["genre"],        user.preferred_genre,    song.genre)        +
        _category_pts (MAX_POINTS["mood"],         user.preferred_mood,     song.mood)         +
        _category_pts (MAX_POINTS["mode"],         user.preferred_mode,     song.mode)         +
        _proximity_pts(MAX_POINTS["energy"],       user.target_energy,      song.energy)       +
        _proximity_pts(MAX_POINTS["valence"],      user.target_valence,     song.valence)      +
        _tempo_pts    (MAX_POINTS["tempo_bpm"],    user.target_tempo_bpm,   song.tempo_bpm)    +
        _proximity_pts(MAX_POINTS["danceability"], user.target_danceability, song.danceability) +
        _proximity_pts(MAX_POINTS["acousticness"], user.target_acousticness, song.acousticness)
    )


def score_breakdown(song: Song, user: UserProfile) -> dict[str, float]:
    """Return per-feature points — useful for explain() and debugging."""
    return {
        "genre":        _category_pts (MAX_POINTS["genre"],        user.preferred_genre,     song.genre),
        "mood":         _category_pts (MAX_POINTS["mood"],         user.preferred_mood,      song.mood),
        "mode":         _category_pts (MAX_POINTS["mode"],         user.preferred_mode,      song.mode),
        "energy":       _proximity_pts(MAX_POINTS["energy"],       user.target_energy,       song.energy),
        "valence":      _proximity_pts(MAX_POINTS["valence"],      user.target_valence,      song.valence),
        "tempo_bpm":    _tempo_pts    (MAX_POINTS["tempo_bpm"],    user.target_tempo_bpm,    song.tempo_bpm),
        "danceability": _proximity_pts(MAX_POINTS["danceability"], user.target_danceability, song.danceability),
        "acousticness": _proximity_pts(MAX_POINTS["acousticness"], user.target_acousticness, song.acousticness),
        "total":        score_song(song, user),
    }
