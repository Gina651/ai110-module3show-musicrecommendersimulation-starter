# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version is a pure **content-based** recommender: it never looks at
what other users did, only at how closely a song's own attributes
(genre, mood, energy, valence, tempo, danceability, acousticness) match
one user's stated taste profile. Every recommendation can be explained
feature-by-feature — there's no hidden model, just a weighted scoring
formula and a sort.

---

## How The System Works

**What features does each `Song` use?**
`genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`,
`acousticness` — pulled straight from `data/songs.csv`.

**What information does `UserProfile` store?**
A preferred value for each of those same features (`preferred_genre`,
`preferred_mood`, `preferred_energy`, `preferred_valence`,
`preferred_tempo_bpm`, `preferred_danceability`,
`preferred_acousticness`), plus a `weights` dict that says how much each
feature should count toward the final score. In a real platform these
preferred values would be *inferred* from listening behavior (likes,
skips, replays); here they're set directly so the math stays inspectable.

**How does the system compute a score for each song?**
Two different rules depending on the feature type, both in `src/scorer.py`:
- *Categorical* features (`genre`, `mood`): exact match = `1.0`, otherwise `0.0`.
- *Numeric* features (`energy`, `valence`, `tempo_bpm`, `danceability`,
  `acousticness`): scored by **closeness**, not magnitude —
  `1 - (|song_value - preferred_value| / max_range)`. A user who wants
  moderate energy (0.5) should get moderate-energy songs recommended,
  not just the single highest-energy song in the catalog.
- The final score is a **weighted average** across all seven features,
  using `UserProfile.weights`. Genre and mood are weighted highest by
  default (0.30 / 0.20) on the idea that a genre or mood mismatch breaks
  the "vibe" more than being slightly off on tempo.

**How are songs actually chosen for the recommendation list?**
`src/ranker.py` scores every song independently, sorts descending by
score, and returns the top N. It also supports an optional
`max_per_artist` cap — a simple guardrail that limits how many songs from
the same artist can appear in one list, even if they all scored well
(see `bias_analysis.md` for why this matters).

```
Song attributes  ─┐
                   ├──> score_song() ──> single relevance score
UserProfile prefs ─┘         │
                              ▼
                  rank_songs() sorts ALL scored songs,
                  applies top_n / max_per_artist,
                  returns the final ordered list
```

We need both a **Scoring Rule** and a **Ranking Rule** because they
answer different questions: scoring is per-song and has no idea what
else is in the catalog, while ranking looks at the whole scored list and
can apply list-level policies (ordering, cutoffs, diversity) that no
single song's score captures on its own.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

```
=== Recommendations for Pop Fan ===
1. Sunrise City       — Neon Echo      [pop/happy]        score=0.991
2. Gym Hero           — Max Pulse      [pop/intense]      score=0.753
3. Rooftop Lights     — Indigo Parade  [indie pop/happy]  score=0.679
4. Night Drive Loop   — Neon Echo      [synthwave/moody]  score=0.440
5. Storm Runner       — Voltline       [rock/intense]     score=0.399

=== Same user, max 1 song per artist ===
1. Sunrise City       — Neon Echo      [pop/happy]        score=0.991
2. Gym Hero           — Max Pulse      [pop/intense]      score=0.753
3. Rooftop Lights     — Indigo Parade  [indie pop/happy]  score=0.679
4. Storm Runner       — Voltline       [rock/intense]     score=0.399
5. Coffee Shop Stories— Slow Stereo    [jazz/relaxed]     score=0.351

=== Recommendations for Chill/Study Listener ===
1. Library Rain       — Paper Lanterns [lofi/chill]       score=0.994
2. Midnight Coding    — LoRoom         [lofi/chill]       score=0.970
3. Focus Flow         — LoRoom         [lofi/focused]     score=0.780
4. Spacewalk Thoughts — Orbit Bloom    [ambient/chill]    score=0.655
5. Coffee Shop Stories— Slow Stereo    [jazz/relaxed]     score=0.468
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

- **Genre weight, 0.30 → tested against a lower weight:** raising genre's
  weight relative to mood/energy made exact-genre songs dominate the top
  results even when their mood/energy were a mediocre fit; lowering it let
  numeric closeness "outvote" genre, which sometimes surfaced songs from
  an unrelated genre just because their energy/tempo lined up. 0.30
  struck a reasonable middle ground for this catalog.
- **Adding `acousticness` to the score:** including it (weight 0.05) had
  only a small effect on `pop` vs `lofi` profiles, since genre/mood
  already separate those clusters — but it noticeably helped distinguish
  between the two `lofi` tracks (`Midnight Coding` vs `Library Rain`) for
  the chill/study profile, since one is meaningfully more acoustic than
  the other.
- **`max_per_artist=1` guardrail:** for the "Pop Fan" profile this swapped
  out the second `Neon Echo` track for a jazz track that scored lower
  individually but added catalog variety — see `bias_analysis.md` for the
  full before/after comparison.

---

## Limitations and Risks

- It only works on a tiny, hand-authored 10-song catalog — nowhere near
  representative of a real streaming library.
- It has no concept of collaborative signal (what *other* users liked),
  so it can't surface a song a user would love that doesn't match their
  *stated* profile.
- Genre/mood matching is exact-string only. `indie pop` scores zero
  genre-match against a `pop` preference even though the genres are
  musically adjacent — see `bias_analysis.md` for a concrete example from
  this catalog.
- It doesn't understand lyrics, instrumentation, or anything not already
  encoded as a numeric/categorical attribute in `songs.csv`.
- Without a diversity guardrail, it can over-favor one artist whose
  catalog happens to match a user's profile well (also detailed in
  `bias_analysis.md`).

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this made the "data → prediction" pipeline concrete: a
recommendation isn't magic, it's a weighted comparison between two
structured records (a song's attributes and a user's stated preferences),
followed by a sort. Seeing the exact same math applied consistently also
made it obvious where bias creeps in — not through any single "wrong"
calculation, but through the *aggregate* effect of scoring every item
independently and always taking the top N: an artist with several
strong-matching songs, or a genre label that happens to match exactly,
gets structurally over-represented, even though no individual score is
unfair. That's the same dynamic — scaled up with far more behavioral data
— behind real filter-bubble concerns in production recommenders.
