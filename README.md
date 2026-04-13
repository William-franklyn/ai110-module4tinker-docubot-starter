# DocuBot

---

## CLI Output — Default "pop / happy" Profile

Run with:
```
python -m src.main
```

Terminal output (Casey profile — pop / euphoric / major):

```
  ============================================================
  Music Recommender  |  Content-Based Filtering
  Catalog : 18 songs loaded
  ============================================================
  ============================================================
  Listener : Casey
  Genre    : pop   Mood: euphoric   Mode: major
  Energy   : 0.78   Valence: 0.85   Tempo: 110 BPM
  ============================================================

  #1  Blinding Lights by The Weeknd
       Score : 8.01 / 9.0  [#################...]
       Genre : pop  |  Mood: euphoric  |  Energy: 0.8  |  BPM: 171
       Reasons:
           +  genre match 'pop' (+2.0)
           +  mood match 'euphoric' (+1.5)
           +  mode match 'major' (+0.5)
           ~  energy 0.8 vs target 0.78 (+1.96)
           ~  valence 0.33 vs target 0.85 (+0.48)
           ~  tempo 171 BPM vs target 110 BPM (+0.7)
           ~  danceability 0.51 vs target 0.72 (+0.4)
           ~  acousticness 0.0 vs target 0.05 (+0.47)

  #2  Superstition by Stevie Wonder
       Score : 6.84 / 9.0  [###############.....]
       Genre : soul  |  Mood: euphoric  |  Energy: 0.76  |  BPM: 101
       Reasons:
           ~  genre mismatch: wanted 'pop', got 'soul' (+0.0)
           +  mood match 'euphoric' (+1.5)
           +  mode match 'major' (+0.5)
           ~  energy 0.76 vs target 0.78 (+1.96)
           ~  valence 0.87 vs target 0.85 (+0.98)
           ~  tempo 101 BPM vs target 110 BPM (+0.95)
           ~  danceability 0.8 vs target 0.72 (+0.46)
           ~  acousticness 0.07 vs target 0.05 (+0.49)

  #3  Temperature by Sean Paul
       Score : 6.79 / 9.0  [###############.....]
       Genre : dancehall  |  Mood: euphoric  |  Energy: 0.81  |  BPM: 105
       Reasons:
           ~  genre mismatch: wanted 'pop', got 'dancehall' (+0.0)
           +  mood match 'euphoric' (+1.5)
           +  mode match 'major' (+0.5)
           ~  energy 0.81 vs target 0.78 (+1.94)
           ~  valence 0.89 vs target 0.85 (+0.96)
           ~  tempo 105 BPM vs target 110 BPM (+0.97)
           ~  danceability 0.85 vs target 0.72 (+0.43)
           ~  acousticness 0.07 vs target 0.05 (+0.49)

  #4  Despacito by Luis Fonsi
       Score : 6.68 / 9.0  [##############......]
       Genre : latin pop  |  Mood: euphoric  |  Energy: 0.79  |  BPM: 89
       Reasons:
           ~  genre mismatch: wanted 'pop', got 'latin pop' (+0.0)
           +  mood match 'euphoric' (+1.5)
           +  mode match 'major' (+0.5)
           ~  energy 0.79 vs target 0.78 (+1.98)
           ~  valence 0.81 vs target 0.85 (+0.96)
           ~  tempo 89 BPM vs target 110 BPM (+0.9)
           ~  danceability 0.85 vs target 0.72 (+0.43)
           ~  acousticness 0.23 vs target 0.05 (+0.41)

  #5  SICKO MODE by Travis Scott
       Score : 4.20 / 9.0  [#########...........]
       Genre : hip-hop  |  Mood: aggressive  |  Energy: 0.78  |  BPM: 155
       Reasons:
           ~  genre mismatch: wanted 'pop', got 'hip-hop' (+0.0)
           ~  mood mismatch: wanted 'euphoric', got 'aggressive' (+0.0)
           ~  mode mismatch: wanted 'major', got 'minor' (+0.0)
           ~  energy 0.78 vs target 0.78 (+2.0)
           ~  valence 0.37 vs target 0.85 (+0.52)
           ~  tempo 155 BPM vs target 110 BPM (+0.78)
           ~  danceability 0.59 vs target 0.72 (+0.43)
           ~  acousticness 0.0 vs target 0.05 (+0.47)

  ------------------------------------------------------------
```

---

## How The System Works

I've been thinking about how Spotify always seems to know exactly what I want to hear — even before I do. It turns out the core idea isn't that mysterious: it's basically just the app keeping score on every song in the catalog and surfacing the ones that match your taste the best. My version does the same thing, just a lot smaller and more transparent about how it works.

Instead of tracking what millions of other users are listening to (that's the "collaborative filtering" side that Spotify does), I went with a simpler approach: look at the songs themselves. Every song in the catalog has measurable qualities — how loud and intense it is, how happy or dark it feels, what genre it belongs to, how fast the beat is. And every user has a preference profile that describes what they're in the mood for right now. The recommender just goes through every song, figures out how well each one fits the user, and sorts them by score.

The features I'm tracking for each song and user:

- **genre** — the big umbrella (rock, hip-hop, classical, folk...)
- **mood** — the emotional vibe: euphoric, melancholy, chill, aggressive, peaceful, dark, romantic
- **energy** — how loud and intense the track feels, from 0.0 (silent/ambient) to 1.0 (full blast)
- **valence** — musical positivity, basically: 0.0 is sad and dark, 1.0 is happy and upbeat
- **tempo_bpm** — beats per minute; whether a song feels slow and heavy or fast and driving
- **danceability** — how easy it is to groove to the rhythm
- **acousticness** — is it unplugged and warm, or fully electronic?
- **instrumentalness** — mostly vocals, or mostly just instruments?
- **mode** — major keys feel brighter, minor keys feel darker; it's subtle but real

### The Algorithm Recipe

Once I had those features figured out, I needed to decide how much each one matters when scoring a song. Here's what I landed on — and the reasoning behind each choice:

**Genre match → +2.0 points**
This is the biggest single signal. If someone tells me they want folk music and I serve them hip-hop, it doesn't matter how chill or acoustic that hip-hop song is — it's the wrong call. Genre is the outer envelope everything else lives inside.

**Mood match → +1.5 points**
Mood is the second thing I really care about. The difference between "angry" and "chill" is felt immediately. Two songs can have the exact same energy level and still feel completely different depending on whether one is aggressive and the other is peaceful. So mood gets strong weight, just slightly behind genre.

**Energy closeness → up to +2.0 points**
This one is continuous — it doesn't snap to a yes/no. The closer the song's energy is to what the user wants, the more points it earns (up to 2.0 for a perfect match). I gave this the same ceiling as genre because energy is the most physically perceptible quality in music. If someone wants something quiet and I give them something blasting, nothing else about the song will save it.

**Valence closeness → up to +1.0 points**
Valence refines the emotional tone after energy sets the intensity. A user who wants something energetic but dark (think Nirvana) is very different from one who wants energetic and happy (think Dua Lipa), even though their energy targets look the same.

**Tempo closeness → up to +1.0 points**
BPM gets normalised over a 0–200 scale before scoring, so a 40-BPM difference doesn't feel the same at 80 BPM vs 160 BPM. It's a supporting signal, not a lead one.

**Danceability closeness → up to +0.5 points**
Useful for separating "high energy but heavy" (metal) from "high energy and groovy" (pop) when the other features look similar.

**Acousticness closeness → up to +0.5 points**
Honestly, I almost gave this more weight. It's the cleanest line between electric rock and acoustic folk. But it's so genre-specific that giving it too much power would mess up recommendations for people with mixed tastes, so I kept it modest.

**Mode match → +0.5 points**
Major vs. minor is a real thing — most people have a consistent pull toward one or the other even if they can't name it. But it's subtle enough that I didn't want it to override anything important, so it just gets a small bonus.

**Maximum possible score: 9.0 points**

---

### Biases I'm Already Expecting

No system is perfect, and this one has some clear blind spots I want to be upfront about.

The biggest one is that **genre holds a lot of power**. At 2.0 points, a wrong genre match is a pretty heavy penalty — enough that a song which perfectly nails the user's mood, energy, and tempo in a slightly adjacent genre might never bubble up to the top. That's a real problem for listeners who are more "vibe-driven" than "genre-driven." Someone who loves chill, low-energy music probably doesn't care much whether it's labeled r&b, folk, or dream pop — but my system might rank a perfectly-fitting folk song lower than a mediocre r&b one just because the genre string matched.

Another issue: **the catalog is static**. Real platforms update in real time based on what you skipped, what you replayed, what time of day it is. My system scores based on a frozen profile. If I set my target energy to 0.8 and then start skipping every high-energy song, the system won't notice. Adding a simple feedback loop — where skips lower the target energy and saves raise it — would make this a lot more realistic.

And finally: **"any" genre is too generous**. If a user says they're open to any genre, the system gives them the full 2.0 genre points for every single song in the catalog. That means genre stops being a differentiator entirely, and the ranking falls back almost entirely on energy + mood. For open-ended listeners this might actually be fine, but it's something to watch.

---

## Recommendation Engine — Data Flow

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

        subgraph CONT["Continuous  —  max_pts × (1 − |user_target − song_value|)"]
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

> Full walkthrough and shape legend: [docs/flowchart.md](docs/flowchart.md)

---


DocuBot is a small documentation assistant that helps answer developer questions about a codebase.  
It can operate in three different modes:

1. **Naive LLM mode**  
   Sends the entire documentation corpus to a Gemini model and asks it to answer the question.

2. **Retrieval only mode**  
   Uses a simple indexing and scoring system to retrieve relevant snippets without calling an LLM.

3. **RAG mode (Retrieval Augmented Generation)**  
   Retrieves relevant snippets, then asks Gemini to answer using only those snippets.

The docs folder contains realistic developer documents (API reference, authentication notes, database notes), but these files are **just text**. They support retrieval experiments and do not require students to set up any backend systems.

---

## Setup

### 1. Install Python dependencies

    pip install -r requirements.txt

### 2. Configure environment variables

Copy the example file:

    cp .env.example .env

Then edit `.env` to include your Gemini API key:

    GEMINI_API_KEY=your_api_key_here

If you do not set a Gemini key, you can still run retrieval only mode.

---

## Running DocuBot

Start the program:

    python main.py

Choose a mode:

- **1**: Naive LLM (Gemini reads the full docs)  
- **2**: Retrieval only (no LLM)  
- **3**: RAG (retrieval + Gemini)

You can use built in sample queries or type your own.

---

## Running Retrieval Evaluation (optional)

    python evaluation.py

This prints simple retrieval hit rates for sample queries.

---

## Modifying the Project

You will primarily work in:

- `docubot.py`  
  Implement or improve the retrieval index, scoring, and snippet selection.

- `llm_client.py`  
  Adjust the prompts and behavior of LLM responses.

- `dataset.py`  
  Add or change sample queries for testing.

---

## Requirements

- Python 3.9+
- A Gemini API key for LLM features (only needed for modes 1 and 3)
- No database, no server setup, no external services besides LLM calls
