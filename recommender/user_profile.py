from dataclasses import dataclass, field


@dataclass
class UserProfile:
    """A listener's taste fingerprint — the target the scorer aims to match.

    Each numerical preference mirrors the matching feature on Song so the
    scorer can subtract them directly (both live in the same 0.0–1.0 space).

    "any" is a valid value for preferred_genre, preferred_mood, and
    preferred_mode — the scorer treats it as an automatic full match so it
    never penalises the user for an open preference.
    """

    name: str

    # --- categorical preferences ---
    preferred_genre: str = "any"   # e.g. "pop", "rock", "any"
    preferred_mood: str  = "any"   # e.g. "chill", "euphoric", "any"
    preferred_mode: str  = "any"   # "major", "minor", or "any"

    # --- numerical preferences (0.0–1.0) ---
    target_energy: float        = 0.5
    target_valence: float       = 0.5
    target_danceability: float  = 0.5
    target_acousticness: float  = 0.5

    # --- tempo (separate scale) ---
    target_tempo_bpm: int = 100   # the BPM the user feels most comfortable at

    # --- history (populated at runtime, not set by the user directly) ---
    liked_ids: list[int]    = field(default_factory=list)
    disliked_ids: list[int] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"User '{self.name}' | genre={self.preferred_genre} "
            f"mood={self.preferred_mood} energy={self.target_energy:.2f} "
            f"valence={self.target_valence:.2f} bpm={self.target_tempo_bpm}"
        )


# ---------------------------------------------------------------------------
# Ready-made example profiles — useful for quick manual tests
# ---------------------------------------------------------------------------

CHILL_LISTENER = UserProfile(
    name="Alex",
    preferred_genre="r&b",
    preferred_mood="chill",
    target_energy=0.35,
    target_valence=0.45,
    target_danceability=0.65,
    target_acousticness=0.20,
    target_tempo_bpm=90,
)

HYPE_LISTENER = UserProfile(
    name="Jordan",
    preferred_genre="hip-hop",
    preferred_mood="intense",
    target_energy=0.85,
    target_valence=0.40,
    target_danceability=0.70,
    target_acousticness=0.05,
    target_tempo_bpm=150,
)

ACOUSTIC_LISTENER = UserProfile(
    name="Sam",
    preferred_genre="folk",
    preferred_mood="peaceful",
    target_energy=0.30,
    target_valence=0.55,
    target_danceability=0.40,
    target_acousticness=0.80,
    target_tempo_bpm=85,
)
