# Model Card — SongSense 1.0

A simple content-based music recommender built to explore how streaming platforms
decide what to play next. Written in Python, no machine learning involved.

---

## 1. Model Name

**SongSense 1.0**

Named because the goal is to match a song to the way a listener *feels*, not just
what genre they clicked last. The "1.0" is honest — this is a first draft, not a
finished product.

---

## 2. Goal / Task

SongSense takes a listener's stated preferences — things like "I want something
high-energy, euphoric, and around 125 BPM" — and scores every song in a catalog
against those preferences. It returns the top five songs that best match.

It is not predicting what you will click. It is not learning from your history.
It is doing one job: given what you *say* you want right now, find the closest
match in a fixed library of songs.

---

## 3. Data Used

**Catalog size:** 18 songs, stored in `data/songs.csv`.

**Features per song (13 total):**

| Feature | Type | What it means |
|---|---|---|
| title, artist | text | Song identity |
| genre | text | Broad label (pop, rock, hip-hop, etc.) |
| mood | text | Emotional label (euphoric, chill, angry, etc.) |
| energy | 0.0 – 1.0 | How loud and intense the song feels |
| valence | 0.0 – 1.0 | How happy or sad it sounds (1.0 = very happy) |
| tempo_bpm | integer | Beats per minute |
| danceability | 0.0 – 1.0 | How easy it is to dance to |
| acousticness | 0.0 – 1.0 | How acoustic vs. electronic it is |
| instrumentalness | 0.0 – 1.0 | How much of the song has no vocals |
| mode | major / minor | Musical key type |
| popularity | integer | A rough 0–100 popularity score |

**Limits of the data:**

- 18 songs is tiny. Real recommenders use millions.
- The catalog was handcrafted, not pulled from a real API. The feature values
  are approximations, not Spotify audio analysis data.
- Genre coverage is uneven. Hip-hop has 3 songs. Grunge has 1. Classical has 2.
  Several genres (jazz, metal, reggae, blues) are missing entirely.
- Mood labels are subjective. One person's "chill" is another person's "melancholy."

---

## 4. Algorithm Summary

There is no machine learning here. The algorithm is a weighted point system.

**Step 1 — Build a listener profile.**
The listener specifies what they want: a preferred genre, a preferred mood, a
preferred mode (major or minor), and target values for energy, valence, tempo,
danceability, and acousticness.

**Step 2 — Score every song.**
For each song in the catalog, the system checks two types of features:

- *Categorical features* (genre, mood, mode): binary. If the song matches what
  you asked for, you get full points. If it doesn't match, you get zero. There
  is no partial credit for "close enough."

- *Continuous features* (energy, valence, tempo, danceability, acousticness):
  proximity scoring. The closer the song is to your target value, the more points
  it earns. A song that hits your energy target exactly gets the full energy score.
  A song that is far off loses most of those points.

**Step 3 — Add up the points.**
All the scores are summed. The maximum possible score is 10.0 points. Ties are
broken by the song's popularity rating.

**Step 4 — Return the top five.**
The five highest-scoring songs are returned as the recommendations.

**Current weights (after the energy experiment):**

| Feature | Max points | Share of total |
|---|---|---|
| Energy | 4.0 | 40% |
| Mood match | 1.5 | 15% |
| Genre match | 1.0 | 10% |
| Valence | 1.0 | 10% |
| Tempo | 1.0 | 10% |
| Mode match | 0.5 | 5% |
| Danceability | 0.5 | 5% |
| Acousticness | 0.5 | 5% |

These weights are defined as named constants in `src/recommender.py` and can be
changed to run experiments.

---

## 5. Observed Behavior / Biases

**Energy dominates everything.**
After doubling the energy weight to 4.0, energy now accounts for 40% of every
song's score. In practice, this means two listeners who want completely different
genres and moods — one asking for happy pop, one asking for angry rock — end up
receiving nearly identical top-five lists if they both target high energy. The
system is less a taste-matcher and more an energy-level sorter with genre labels
on the side.

**The "any" genre problem.**
When a listener sets their genre preference to "any" (because they are open to
everything), the system gives every single song in the catalog a free 1.0 genre
point. This sounds reasonable, but it means genre stops being a filtering signal
at all. The result: a calm lo-fi profile using `genre = "any"` can end up
recommending Bohemian Rhapsody because that song has a slow tempo that matches
the target — the genre-openness accidentally gave a theatrical rock opera a free
pass into a background study playlist.

**Catalog thinness punishes niche listeners.**
A listener who wants classical music can only match 2 of the 18 songs. The system
fills positions 3–5 with whatever scores highest among the remaining 16 songs,
which are not classical. The listener asked for something specific and the system
runs out of answers after two songs.

**Minor mode slight advantage.**
Ten of the 18 songs are in a minor key. A listener who prefers major mode loses
the mode-match bonus on 56% of the catalog. A listener who prefers minor loses it
on 44%. Small effect, but real.

---

## 6. Evaluation Process

**Six listener profiles were tested:**

Three standard profiles representing realistic listener archetypes:

- *High-Energy Pop* — euphoric, danceable, loud. Baseline happy-path test.
- *Chill Lofi* — very quiet, slow, no genre preference. Background study music.
- *Deep Intense Rock* — maximum energy, angry mood, minor key, rock genre.

Three adversarial profiles designed to expose edge cases:

- *Sad Bangers* — high energy but melancholy mood (a contradictory combination
  that almost no song in the catalog satisfies simultaneously).
- *The Completist* — every preference set to "any" or the mathematical midpoint.
  No real preference expressed.
- *Classical Purist* — classical genre, very quiet, high acousticness. Tests what
  happens when the catalog runs out of matching songs.

**Five formal experiments were run in `src/evaluate.py`:**

1. Perfect Match — engineered a profile to mirror one song exactly; verified it
   scored at the top by a large margin.
2. Orphan Genre — requested a genre (jazz) that does not exist in the catalog;
   confirmed genre points collapse and scores compress into a narrow band.
3. Contradictory Profile — paired high energy with a peaceful mood; confirmed the
   system picks the least-wrong song rather than a correct one.
4. Genre Weight Impact — compared the same listener with `genre = "pop"` vs
   `genre = "any"`; measured exactly how many points the genre lock-in adds.
5. Score Spread — scored all 18 songs for four profiles; measured the gap between
   highest and lowest score to check how discriminating the system is.

**The weight-shift experiment:**
Energy weight was doubled (2.0 → 4.0) and genre weight was halved (2.0 → 1.0)
to test whether energy proximity should drive recommendations more than genre
labels. The result: recommendations became more accurate for listeners who have
strong energy preferences, but created a filter bubble where high-energy profiles
all converge on the same handful of songs regardless of mood or genre.

---

## 7. Intended Use and Non-Intended Use

**This system is designed for:**

- Learning how content-based filtering works. It is a teaching tool, not a
  product.
- Experimenting with scoring weights to understand how small changes in a formula
  can shift recommendations in surprising ways.
- Prototyping — a starting point for someone who wants to build something more
  sophisticated later.

**This system should not be used for:**

- Real music recommendations to real users. The catalog is 18 songs. Any user
  will exhaust the meaningful matches almost immediately.
- Cold-start users who have not stated their preferences. The system has no way
  to infer what someone wants — it needs a fully filled-out profile to work.
- Situations where diverse discovery matters. The system can only recommend what
  is already in the catalog. It cannot introduce anyone to something genuinely new.
- Replacing collaborative filtering. It has no concept of "people like you also
  liked." Two users with opposite preferences could share a top-five list purely
  because they both target high energy.

---

## 8. Ideas for Improvement

**1. Replace "any" genre with an exclusion list.**
Instead of "I want any genre," allow listeners to say "I want anything except
country and metal." This preserves discovery while still filtering out things the
listener actively dislikes. Right now, `genre = "any"` is a blunt instrument that
turns off genre filtering entirely.

**2. Rebalance the catalog and add more songs per genre.**
Most genres have one song. Classical has two. Hip-hop has three. A real recommender
needs enough coverage to give meaningful results across the full preference space.
At minimum, each genre should have five or more songs so that niche listeners get
five real matches, not two good ones and three unrelated backfills.

**3. Add a lightweight feedback loop.**
After a recommendation, ask: did the listener like it? If yes, nudge the weights
slightly toward that song's features. If no, nudge them away. Even five or six
thumbs-up/down interactions would let the system personalize over time without
requiring full collaborative filtering or a training dataset.

---

## 9. Personal Reflection

**The moment it actually clicked for me**

The biggest learning moment wasn't writing the code — it was running the weight
experiment and watching the recommendations break in a specific, explainable way.

When I doubled the energy weight, I expected the playlists to shift a little. What
actually happened was that two profiles with opposite emotional goals — one wanting
happy pop, one wanting melancholy sad songs — ended up sharing most of the same
top-five list. Both got Smells Like Teen Spirit. Both got Mr. Brightside. The
system had technically done its job: it found the songs closest to both energy
targets. But it had completely ignored what the listeners actually wanted to feel.

That gap — between what the math optimized for and what a human would call a
good recommendation — is the thing I keep thinking about. The algorithm wasn't
wrong. It was just solving a slightly different problem than I thought I was asking
it to solve.

**Where AI tools helped, and where I had to slow down**

Having an AI assistant write the boilerplate (the CSV loader, the scoring loop,
the sorted() ranking) was genuinely fast. That kind of structural code is
predictable and I could read it, understand it, and trust it quickly.

The part where I had to slow down was interpreting the output. When Bohemian
Rhapsody showed up in the chill lofi playlist, my first instinct was "the code
is wrong." It wasn't. The code was doing exactly what I told it to do — Bohemian
Rhapsody's tempo matched the target, and the "any" genre setting gave it free
points. The AI couldn't tell me whether that was a bug or a feature. That required
actually understanding the weights and running the math myself.

The lesson: AI tools are good at writing the mechanism. They are not good at
telling you whether the mechanism is doing what you actually want.

**What surprised me about a 30-line algorithm feeling like a recommendation**

I expected it to feel fake. It doesn't, entirely. When you run the High-Energy Pop
profile and Blinding Lights comes out on top — the right answer, immediately, with
a clear score — it genuinely feels like the system understood something. Even
though all it did was add up eight numbers.

What surprised me is that the *illusion* of intelligence comes from the output
format, not the logic. A ranked list with reasons attached ("genre match: pop",
"energy 0.80 vs target 0.85") reads as understanding even when the mechanism is
just subtraction and multiplication. That is a useful thing to know when thinking
about how real AI products are perceived by users. The explanation is doing a lot
of the work.

**What I would try next**

The thing I most want to try is connecting this to real data. The Spotify API
exposes actual audio features — real energy scores, real tempo, real danceability
— for any song. With a large enough catalog pulled from real API data, most of the
catalog-thinness problems go away. The scoring logic itself would not need to
change much. The experiment with energy vs. genre weights would become much more
meaningful when run over thousands of songs instead of 18.

After that, I would try adding even a simple collaborative signal: store the
profiles of past users who liked a song, and if a new user shares a profile with
them, boost that song's score slightly. That single addition would turn this from
content-based filtering into a hybrid recommender, and it would probably fix the
filter bubble problem without needing to touch the weights at all.

---
