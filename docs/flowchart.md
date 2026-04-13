# Recommendation Engine — Data Flow

```mermaid
flowchart TD
    CSV[("songs.csv\ncatalog")] -->|_load| ENGINE["RecommendationEngine"]
    USER[("UserProfile\ngenre · mood · mode\nenergy · valence\ntempo · danceability\nacousticness")] --> LOOP

    ENGINE --> LOOP

    LOOP(["For each Song in catalog"])
    LOOP --> HEARD{"Song already heard?\nliked_ids or disliked_ids"}
    HEARD -- Yes --> SKIP(["skip — do not score"])
    HEARD -- No --> SCORER

    subgraph SCORER["score_song(song, user)   max = 9.0 pts"]
        direction TB

        subgraph CAT["Categorical  —  full points or zero"]
            G["+2.0  genre match"]
            M["+1.5  mood  match"]
            MO["+0.5  mode  match"]
        end

        subgraph CONT["Continuous  —  max_pts × (1.0 − |user_target − song_value|)"]
            E["+2.0  energy proximity"]
            V["+1.0  valence proximity"]
            T["+1.0  tempo_bpm proximity"]
            D["+0.5  danceability proximity"]
            A["+0.5  acousticness proximity"]
        end

        G & M & MO & E & V & T & D & A --> SUM["Σ  total points  (0.0 – 9.0)"]
    end

    SCORER --> COLLECT
    SKIP -.->|"score omitted"| COLLECT
    COLLECT[("scored_list\n(song, score) per unheard song")]

    COLLECT --> SORT["Sort DESC by score\ntiebreak: song.popularity"]
    SORT --> SLICE["Slice first N results"]
    SLICE --> OUT[/"Top K Recommendations\n(song, score) pairs"/]
```

## Reading the diagram

| Shape | Meaning |
|---|---|
| Cylinder `(( ))` | Persistent data — the CSV file or the scored list |
| Stadium `([ ])` | Loop step or terminal action |
| Diamond `{ }` | Decision / branch |
| Rectangle | Process step |
| Rounded rectangle `(( ))` | Data store |
| Subgraph border | Groups steps that belong to one function |
| Dashed arrow `-.->` | Skipped songs contribute nothing to the list |

## One song's journey — walkthrough

1. **Load** — `RecommendationEngine._load()` reads every row of `songs.csv` into a `Song` dataclass.
2. **Loop** — `recommend()` iterates over every `Song` in `self.catalog`.
3. **Filter** — if the song's `id` is in `user.liked_ids` or `user.disliked_ids` it is skipped entirely (the user has already heard it).
4. **Score** — `scorer.score_song(song, user)` runs two parallel sub-calculations:
   - **Categorical**: genre, mood, and mode each earn their full ceiling or zero.
   - **Continuous**: energy, valence, tempo, danceability, and acousticness each earn a fraction of their ceiling based on how close they are to the user's target.
5. **Collect** — the `(song, score)` pair is appended to `scored_list`.
6. **Rank** — after every song has been evaluated, `scored_list` is sorted by score descending.  Ties are broken by `song.popularity` (also descending) so the more popular song surfaces first.
7. **Slice** — only the first `top_n` pairs are returned to the caller.
