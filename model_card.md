# Model Card: Vibe Compass 1.0

## Model Name

**Vibe Compass 1.0** — it takes a person's stated "vibe" (genre, mood,
and a few numeric feelings like energy and acousticness) and points them
toward the songs in our catalog that match it best.

## Goal / Task

Given what someone says they like — a favorite genre, a favorite mood,
and target values for energy, valence, tempo, danceability, and
acousticness — suggest the top 5 songs from our catalog that best match
those preferences. It's not trying to predict what a person will click
next based on other users; it's just comparing stated taste to song
attributes and ranking the results.

## Data Used

- 19 songs, all made up by hand for this project — not real streaming
  data or real audio analysis.
- Each song has 7 features: `genre`, `mood`, `energy`, `tempo_bpm`,
  `valence`, `danceability`, `acousticness`.
- 16 different genres and 15 different moods are represented, but the
  catalog isn't evenly spread — `lofi` has 3 songs and `chill` is the
  most common mood (3 songs), while every other genre/mood has just 1.
- There's no user history, no likes/skips, and no real listeners behind
  this data — every "preference" in this project is something we typed
  in ourselves to test the system.

## Algorithm Summary (plain language, no code)

Every song gets scored against what the user asked for, out of a
possible 6 points:

- If the song's genre is an exact match to the user's favorite genre,
  it gets 2 points. If not, 0.
- If the song's mood is an exact match, it gets 1 point. If not, 0.
- For the rest of the features (energy, valence, tempo, danceability,
  acousticness), the song doesn't need to match exactly — it just needs
  to be *close* to what the user wants. The closer it is, the more of
  that feature's points it earns; a song that's exactly on target gets
  full credit, and a song at the opposite extreme gets none.
- All the points get added up into one final score.
- Every song in the catalog gets scored this way, then we sort from
  highest score to lowest and show the top 5.

There's no learning involved — every time you run it with the same
inputs, you get the exact same output. It's really just "compare, score,
sort."

## Observed Behavior / Biases

- **Genre beats mood, almost every time.** Because an exact genre match
  is worth 2 points — double what mood is worth — a song with the
  "right" genre but the "wrong" mood usually still beats a song from a
  different genre with the "right" mood. For example, a listener who
  asks for "happy pop" still gets an "intense" pop song ranked near the
  top, ahead of songs from other genres that actually match "happy."
- **The catalog itself is lopsided.** `lofi` has 3 songs while every
  other genre has 1. That means a lofi-ish listener gets 3 chances to
  score well just because there's more lofi to choose from — not
  because lofi is a better fit than, say, our one jazz song. A real
  streaming catalog has the same problem, just bigger: whatever genre a
  platform has the most of tends to get recommended more, regardless of
  whether it's really the best match for any one listener.
- **It never says "I'm not sure."** If you ask for a genre/mood
  combination that doesn't exist in the catalog (like "sad metal," when
  every metal song here is tagged "aggressive"), the system doesn't flag
  that — it just confidently returns its best imperfect guess as if it
  were a great match.

## Evaluation Process

We tested the system with five different taste profiles and looked at
the top 5 results for each (full output is in README.md):

1. **High-Energy Pop** — upbeat, intense pop
2. **Chill Lofi** — mellow, acoustic, low-energy lofi
3. **Deep Intense Rock** — high-energy, moodier rock
4. **An adversarial profile**: genre = metal, mood = sad — a combination
   that doesn't actually exist in our catalog, to see if the system
   would notice
5. **Another adversarial profile**: genre = k-pop — a genre with zero
   songs in our catalog at all, to see what happens when nothing can
   match

We also ran one experiment: doubling the points for energy and cutting
the points for genre in half, then comparing the before/after rankings
for the High-Energy Pop profile. The order of the top songs barely
changed, but the score gaps between songs got much smaller — meaning the
system became less confident/decisive, not necessarily more "correct."

Comparing pairs of profiles side by side also helped confirm the system
was behaving sensibly: totally opposite profiles (High-Energy Pop vs.
Chill Lofi) shared zero songs in their results, which is exactly what
should happen, while similar profiles (Deep Intense Rock vs. High-Energy
Pop, which both want an "intense" mood) had some songs cross over between
their lists.

## Intended Use and Non-Intended Use

**Intended for:**
- Learning how a simple, rule-based recommender works under the hood.
- Showing how weighting choices (like "genre is worth more than mood")
  directly shape what gets recommended.
- Practicing how to test a system for bias and unexpected behavior.

**Not intended for:**
- Actually recommending music to real users — the catalog is tiny and
  made up, and the "taste profiles" aren't based on real listening
  behavior.
- Any use where the recommendations need to be fair across genres,
  artists, or demographics — this system was never checked for that
  kind of fairness, and the catalog imbalance we found means it
  probably isn't fair as-is.
- Situations where the system needs to admit uncertainty — right now it
  always confidently returns a top 5, even when nothing in the catalog
  is a good match.

## Ideas for Improvement

1. **Let genre be "fuzzy" instead of all-or-nothing.** Right now "pop"
   and "indie pop" are treated as completely unrelated, even though
   they're clearly close. A similarity score between genres (instead of
   exact match only) would feel more natural.
2. **Add a confidence signal.** When no song is a strong match (like our
   k-pop test), the system should be able to say "these aren't great
   matches" instead of presenting a top 5 as if it were fully satisfied.
3. **Let the profile change over time.** Right now `user_prefs` never
   updates. A more realistic version would nudge a listener's profile
   based on which recommended songs they said they liked, so it could
   actually learn and adapt.

## Personal Reflection

The biggest learning moment was realizing that "bias" in a system like
this doesn't have to come from a bug — it can come from a totally
correct implementation of a design choice that just turns out to matter
more than expected. Giving genre double the points of mood seemed like a
small, reasonable decision, but it ended up meaning genre almost always
wins whenever the two disagree. Nothing was "wrong" with the math; the
math just revealed what the weights actually meant in practice.

Using an AI coding assistant sped up a lot of the repetitive parts —
writing CSV-loading boilerplate, generating extra test cases, drafting
new catalog rows in the right format — but I had to double-check its
math suggestions carefully, especially around the closeness formula for
numeric features. It's easy for a plausible-looking scoring formula to
quietly reward "bigger is better" instead of "closer is better," and
that's exactly the kind of subtle bug that wouldn't show up until you
specifically tested for it (like we did with the energy-closeness test).

What surprised me most is how convincing a fairly simple point-counting
system can feel. There's no learning, no neural network, nothing
"smart" happening — it's addition and sorting — but seeing it correctly
separate "chill lofi" fans from "intense rock" fans, and watching it
explain its own reasoning line by line, genuinely felt like a real
recommendation, not just a spreadsheet formula. That's a useful reminder
that a system doesn't need to be complex to feel intelligent to the
person using it, which cuts both ways: it's a great way to build trust
quickly, but it's also easy to over-trust a system whose "reasoning" is
really just a handful of hardcoded point values.

If I kept extending this project, I'd want to try feeding it real
listening data (even something small, like my own liked songs from a
streaming export) and see how differently the recommendations would
need to be weighted to feel right for actual, messy human taste instead
of the neat profiles I made up for testing.
