# Model Card: Music Recommender Simulation

## Overview
A rule-based, weighted content-based recommender that ranks songs from a
fixed catalog against a user's stated taste profile. There is no machine
learning here — "the model" is a deterministic scoring formula plus a
sorting/filtering ranking rule.

## Intended Use
- **Primary use case:** educational simulation for understanding how
  content-based recommendation works, as a contrast to collaborative
  filtering used at scale by platforms like Spotify or YouTube.
- **Intended users:** students/developers learning recommender system
  concepts; not intended as a production recommendation engine.
- **Out of scope:** this is not designed to handle real user behavioral
  data, real-time interaction signals, large catalogs, or production
  traffic. It should not be presented to end users as a finished product.

## How It Works (summary)
- Input: a song dict (genre, mood, energy, valence, tempo_bpm,
  danceability, acousticness) and a `user_prefs` dict (target values for
  each feature).
- Scoring Rule: `+2.0` points for an exact genre match, `+1.0` for an
  exact mood match; numeric features (energy, valence, tempo, danceability,
  acousticness) award points scaled by closeness to the target, up to a
  per-feature maximum. Total score is an unnormalized sum, capped at 6.0.
- Ranking Rule: sort all scored songs descending; optionally cap
  recommendations-per-artist for basic diversity.
- Output: an ordered list of songs with scores, and a per-feature score
  breakdown for the top result.

## Training Data / Data Used
None — there is no training step. The system uses:
- A small, hand-authored `songs.csv` (19 songs, 17 artists, 16 genres) for
  demonstration purposes only. Attribute values (energy, valence, etc.)
  are illustrative, not derived from real audio analysis.
- User preferences are supplied directly rather than inferred from
  behavior, which sidesteps the "cold start" and behavioral-signal
  problems real systems have to solve.

## Metrics
No formal accuracy metrics are computed — there's no ground truth of
"correct" recommendations for a simulation like this. Correctness is
verified instead via unit tests (`tests/test_recommender.py`) that assert
the scoring math behaves as designed (e.g. closeness beats maximization,
matches score higher than mismatches, ranking sorts correctly).

## Evaluation

### Profiles tested

Five taste profiles were run against the full 19-song catalog (full
terminal output is in README.md's "Sample Recommendation Output"):

1. **High-Energy Pop** (pop/intense, energy 0.95)
2. **Chill Lofi** (lofi/chill, energy 0.35, acousticness 0.85)
3. **Deep Intense Rock** (rock/intense, energy 0.90, low valence)
4. **Adversarial — Metal + Sad**: asks for a genre/mood combination that
   doesn't exist anywhere in the catalog (every metal song here is
   tagged "aggressive," never "sad")
5. **Adversarial — K-pop**: asks for a genre with zero songs in the
   catalog at all

### What surprised us

- The system never signals "I couldn't fully satisfy this request." For
  the contradictory Metal + Sad profile, it silently returned its best
  available compromise (`Thunder Cathedral`, mood "aggressive," not
  "sad") with no indication that the mood target was structurally
  unreachable. A real product would likely want some way to flag
  "no strong match found" rather than confidently ranking a mediocre fit.
- Removing genre credit entirely (the K-pop profile) didn't break the
  system, but it did make it **much less decisive** — the gap between
  #1 and #2 shrank to 0.07 points, far tighter than any real-genre
  profile's top two. That's a useful signal that wasn't obvious until we
  looked for it: a shrinking score gap across the board can itself
  indicate "no genre matched," which could be surfaced to users directly
  ("we don't have much k-pop, but here's our closest fit") instead of
  presented as an equally confident top 5.

### Comparing profile pairs (plain language)

- **High-Energy Pop vs. Chill Lofi:** these two ask for opposite things
  on almost every dimension — high vs. low energy, upbeat vs. mellow
  tempo, produced vs. acoustic — and their top-5 lists share zero songs.
  That's exactly what should happen: a system that gave a chill lofi fan
  gym-workout pop songs would clearly be broken, so the total separation
  here is a good sign the scoring logic is doing its job.
- **Deep Intense Rock vs. High-Energy Pop:** these overlap on mood
  ("intense") and target energy, but differ on genre. Sure enough,
  `Gym Hero` (pop) shows up as the #2 pick for the *rock* fan, and
  `Storm Runner` (rock) shows up as the #3 pick for the *pop* fan — mood
  and energy similarity let songs "leak" across a genre boundary into a
  related list, while the exact-genre song still comfortably holds first
  place in its own list. This makes sense: intensity is intensity,
  regardless of genre label, so some crossover between "intense" profiles
  is reasonable.
- **Deep Intense Rock vs. Metal + Sad (adversarial):** both profiles
  target high energy and an aggressive-adjacent feel, but one explicitly
  wants low valence ("sad") and the other doesn't specify sadness at all.
  `Thunder Cathedral` (metal/aggressive) tops the Metal + Sad list purely
  because it's the *only* metal song, not because it's actually sad —
  which is the clearest evidence in this evaluation that genre identity
  currently outweighs emotional/mood coherence when the two conflict.
- **K-pop (adversarial) vs. High-Energy Pop:** both target upbeat,
  danceable, high-valence numbers, but K-pop has no genre match anywhere
  in the catalog. The result: `Sunrise City` (real pop) and `Rooftop
  Lights` (indie pop) end up almost tied for #1 in the K-pop list, while
  `Sunrise City` wins by a wide, decisive margin in the true pop list.
  Losing genre credit doesn't just lower every score uniformly — it
  flattens the *differences between* songs, making the ranking much less
  confident overall.

### Explaining one result in plain language

Why does `Gym Hero` keep showing up even for someone who says they want
"Happy Pop," when `Gym Hero` is actually tagged "intense," not "happy"?
Our recipe hands out a guaranteed 2-point bonus just for being in the
right genre — before it even looks at mood or anything else. `Gym Hero`
gets that full 2 points for being pop, plus solid partial credit for
having energy and danceability in the right neighborhood; losing the
1 mood point barely dents that lead. So a song can have the *wrong*
mood and still outrank songs from a *different* genre, because right
now our system trusts "this is pop" more than it trusts "this feels
happy."

---

## Limitations and Bias

**A concrete bias discovered during testing:** the catalog itself is
skewed independent of the scoring math. `lofi` accounts for 3 of the 19
songs (~16%) — every other genre has exactly one — and `chill` is
likewise the most common mood (3 songs). That means a profile anywhere
near lofi/chill effectively gets three "chances" to score well, purely
because there are more candidates in that bucket, not because lofi music
is a genuinely better match for that listener than, say, the catalog's
lone jazz or classical track. On a real platform, genres that happen to
have more catalog depth (historically pop and hip-hop) would win more
recommendation slots for the same structural reason — a form of bias baked
into the data itself, not the algorithm.

- **Small, hand-authored catalog.** 19 songs is nowhere near representative of
  a real streaming catalog; results won't generalize.
- **No collaborative signal.** The system has zero awareness of what other
  users like, so it cannot surface songs a user would love but that don't
  match their *stated* profile (surprise, discovery of adjacent genres).
- **Static preferences.** `user_prefs` values are fixed inputs; the system
  never updates them based on the recommendations it just gave, so it
  can't model how taste evolves or how a real feedback loop would behave.
- **Categorical features are binary.** Genre/mood matching is all-or-
  nothing; a "pop-adjacent" genre like "indie pop" gets zero credit against
  a "pop" preference, even though a person might consider them close.
- **Weight choices are subjective** and were set by the author's judgment,
  not learned or validated against real user satisfaction data.
- **Filter bubble risk**, discussed in detail in `bias_analysis.md`: without
  the `max_per_artist` guardrail, results can be dominated by one artist
  whose songs happen to match the profile well.

## Future Improvements
- Support fuzzy/partial categorical matching (e.g. a genre-similarity
  matrix instead of exact match).
- Let `user_prefs` update from simulated interactions (likes/
  skips), to model feedback loops explicitly rather than just discussing
  them.
- Add a lightweight collaborative-filtering component (e.g. co-listen
  counts between songs) to compare content-based vs. hybrid results.
- Expand the diversity mechanism beyond per-artist caps to genre/mood
  coverage targets.
- Replace the synthetic CSV with a larger, more realistic dataset if this
  moves beyond an educational exercise.

## Ethical Considerations
Even a simple simulation illustrates a real risk in production systems:
content-based scoring alone can create narrow, self-reinforcing feeds
that reduce a listener's exposure to new artists/genres, and can advantage
whichever artists/genres are numerically over-represented in the catalog.
Any production system built on these ideas should pair relevance scoring
with explicit diversity and exploration mechanisms, not treat "highest
score" as automatically "best to show."
