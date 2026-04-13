"""profiles.py — concrete user taste profiles defined as plain dictionaries.

Each profile is a snapshot of what a specific listener wants right now.
Keys map directly to UserProfile fields so the from_dict() converter below
can build a proper UserProfile without any manual field-by-field wiring.

Feature reference
-----------------
  preferred_genre   str   e.g. "rock", "hip-hop", "folk" — or "any" to skip genre filtering
  preferred_mood    str   e.g. "chill", "intense", "euphoric" — or "any"
  preferred_mode    str   "major", "minor", or "any"
  target_energy     float 0.0 = quiet/ambient  →  1.0 = loud/intense
  target_valence    float 0.0 = sad/dark       →  1.0 = happy/bright
  target_tempo_bpm  int   beats per minute (50–200 typical range)
  target_danceability float 0.0 = hard to dance to  →  1.0 = very groovy
  target_acousticness float 0.0 = electronic/distorted  →  1.0 = pure acoustic
"""

from .user_profile import UserProfile

# ---------------------------------------------------------------------------
# Profile definitions
# ---------------------------------------------------------------------------

# Profile A — someone who wants high-energy, aggressive music right now
INTENSE_ROCK_FAN: dict = {
    "name":               "Riley",
    "preferred_genre":    "grunge",
    "preferred_mood":     "angry",
    "preferred_mode":     "minor",
    "target_energy":       0.88,   # needs to feel loud and urgent
    "target_valence":      0.35,   # dark, not happy
    "target_tempo_bpm":    125,    # fast but not frantic
    "target_danceability": 0.45,   # rhythm matters less than power
    "target_acousticness": 0.02,   # fully electric — no acoustic warmth
}

# Profile B — someone who wants background study music, calm and slow
CHILL_LOFI_FAN: dict = {
    "name":               "Morgan",
    "preferred_genre":    "any",    # lofi spans hip-hop, indie, soul — stay open
    "preferred_mood":     "chill",
    "preferred_mode":     "minor",  # minor keys feel more introspective
    "target_energy":       0.25,   # quiet, won't break focus
    "target_valence":      0.40,   # a little melancholy is fine
    "target_tempo_bpm":    85,     # slow and steady
    "target_danceability": 0.55,   # gentle groove, not a party beat
    "target_acousticness": 0.35,   # warm sound, slight vinyl texture
}

# Profile C — weekend road-trip energy, positive and driving
ROAD_TRIP_FAN: dict = {
    "name":               "Casey",
    "preferred_genre":    "pop",
    "preferred_mood":     "euphoric",
    "preferred_mode":     "major",
    "target_energy":       0.78,
    "target_valence":      0.85,   # must feel good
    "target_tempo_bpm":    110,
    "target_danceability": 0.72,
    "target_acousticness": 0.05,
}

# Profile D — quiet evening at home, introspective and acoustic
ACOUSTIC_EVENING_FAN: dict = {
    "name":               "Drew",
    "preferred_genre":    "folk",
    "preferred_mood":     "peaceful",
    "preferred_mode":     "major",
    "target_energy":       0.28,
    "target_valence":      0.52,
    "target_tempo_bpm":    80,
    "target_danceability": 0.38,
    "target_acousticness": 0.82,   # strongly acoustic
}

# All profiles in one place for easy iteration
ALL_PROFILES: list[dict] = [
    INTENSE_ROCK_FAN,
    CHILL_LOFI_FAN,
    ROAD_TRIP_FAN,
    ACOUSTIC_EVENING_FAN,
]


# ---------------------------------------------------------------------------
# Converter — dict  →  UserProfile
# ---------------------------------------------------------------------------

def from_dict(profile: dict) -> UserProfile:
    """Build a UserProfile from a plain dictionary profile definition.

    Only keys that exist in UserProfile are forwarded; any extra keys
    (e.g. notes, tags) are silently ignored so profiles can carry
    human-readable annotations without breaking the converter.
    """
    valid_fields = {
        "name", "preferred_genre", "preferred_mood", "preferred_mode",
        "target_energy", "target_valence", "target_tempo_bpm",
        "target_danceability", "target_acousticness",
    }
    filtered = {k: v for k, v in profile.items() if k in valid_fields}
    return UserProfile(**filtered)
