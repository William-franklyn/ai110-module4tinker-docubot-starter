from dataclasses import dataclass


@dataclass
class Song:
    """One row from songs.csv.

    Numerical features (energy, valence, danceability, acousticness,
    instrumentalness) are all on a 0.0–1.0 scale so they can be compared
    directly without extra normalisation.

    tempo_bpm lives on a different scale (~50–200) and is normalised
    separately inside the scorer.
    """

    id: int
    title: str
    artist: str
    genre: str              # e.g. "pop", "hip-hop", "classical", "folk"
    mood: str               # e.g. "euphoric", "melancholy", "chill", "dark"
    energy: float           # 0.0 = silent/ambient  →  1.0 = intense/loud
    valence: float          # 0.0 = sad/negative    →  1.0 = happy/positive
    tempo_bpm: int          # beats per minute
    danceability: float     # 0.0 = hard to dance to  →  1.0 = very groove-friendly
    acousticness: float     # 0.0 = fully electronic  →  1.0 = fully acoustic
    instrumentalness: float # 0.0 = vocal-heavy       →  1.0 = no vocals
    mode: str               # "major" (brighter) or "minor" (darker)
    popularity: int         # 0–100 platform score; used as a tiebreaker only

    def __str__(self) -> str:
        return f'"{self.title}" by {self.artist} [{self.genre} / {self.mood}]'
