"""engine.py — loads the song catalog and runs recommendations end-to-end."""

import csv
from pathlib import Path

from .song import Song
from .user_profile import UserProfile
from .scorer import score_song, score_breakdown, MAX_POINTS, MAX_SCORE

_DEFAULT_CATALOG = Path(__file__).parent.parent / "data" / "songs.csv"


class RecommendationEngine:
    """Content-based music recommender backed by a CSV catalog.

    Usage
    -----
        engine = RecommendationEngine()          # loads data/songs.csv
        results = engine.recommend(user, top_n=5)
        for song, score in results:
            print(f"{score:.2f}  {song}")
    """

    def __init__(self, catalog_path: Path | str = _DEFAULT_CATALOG) -> None:
        self.catalog: list[Song] = self._load(Path(catalog_path))

    # ------------------------------------------------------------------
    # Catalog loading
    # ------------------------------------------------------------------

    @staticmethod
    def _load(path: Path) -> list[Song]:
        songs = []
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                songs.append(Song(
                    id              = int(row["id"]),
                    title           = row["title"],
                    artist          = row["artist"],
                    genre           = row["genre"],
                    mood            = row["mood"],
                    energy          = float(row["energy"]),
                    valence         = float(row["valence"]),
                    tempo_bpm       = int(row["tempo_bpm"]),
                    danceability    = float(row["danceability"]),
                    acousticness    = float(row["acousticness"]),
                    instrumentalness= float(row["instrumentalness"]),
                    mode            = row["mode"],
                    popularity      = int(row["popularity"]),
                ))
        return songs

    # ------------------------------------------------------------------
    # Ranking rule — why this is separate from the scoring rule
    # ------------------------------------------------------------------
    # score_song() answers "how well does ONE song fit this user?"
    # recommend()  answers "which N songs should I show first, and how?"
    #
    # The ranking layer is where we add policy decisions that go beyond
    # pure math: filtering out already-heard songs, enforcing artist
    # diversity, and using popularity as a tiebreaker.  Mixing those
    # concerns into the scorer would make the scorer hard to test.

    def recommend(
        self,
        user: UserProfile,
        top_n: int = 5,
        exclude_heard: bool = True,
    ) -> list[tuple[Song, float]]:
        """Return up to top_n (song, score) pairs, best match first.

        Parameters
        ----------
        user:
            The listener whose taste profile drives the scores.
        top_n:
            Maximum number of recommendations to return.
        exclude_heard:
            When True, songs in user.liked_ids or user.disliked_ids are
            skipped — the user has already heard them.
        """
        heard = set(user.liked_ids + user.disliked_ids) if exclude_heard else set()

        scored = [
            (song, score_song(song, user))
            for song in self.catalog
            if song.id not in heard
        ]

        # Primary sort: score descending. Tiebreaker: popularity descending.
        scored.sort(key=lambda pair: (pair[1], pair[0].popularity), reverse=True)

        return scored[:top_n]

    def explain(self, song: Song, user: UserProfile) -> None:
        """Print a feature-by-feature point breakdown for one song."""
        breakdown = score_breakdown(song, user)
        total = breakdown.pop("total")
        print(f"\n  {song}")
        print(f"  {'─' * 52}")
        for feature, earned in breakdown.items():
            ceiling = MAX_POINTS[feature]
            bar = "#" * int((earned / ceiling) * 20) if ceiling else ""
            print(f"  {feature:<14} {earned:>4.1f} / {ceiling:.1f}  {bar}")
        print(f"  {'─' * 52}")
        print(f"  {'TOTAL':<14} {total:>4.1f} / {MAX_SCORE:.1f}")
