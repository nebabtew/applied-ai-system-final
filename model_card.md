# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**  

---

## 2. Intended Use  

VibeFinder 1.0 is a classroom simulation project designed to explore how content-based music recommendation systems work. It is **not intended for real users**. The system generates song recommendations based on a user's preferred genre, mood, target energy level, and acousticness preference. It assumes users have clear, stable preferences and that matching on genre and mood is the strongest signal for satisfaction.  

---

## 3. How the Model Works  

VibeFinder scores each song on four factors:

1. **Genre Match** (+2.0 points): If the song's genre exactly matches the user's favorite genre, it gets a large bonus.
2. **Mood Match** (+1.0 point): If the song's mood matches the user's favorite mood, it earns a bonus.
3. **Energy Proximity** (+0 to 1.0 points): The system measures how close the song's energy level is to the user's target. A perfect match earns 1.0; a very different energy level earns close to 0.
4. **Acousticness Proximity** (+0 to 1.0 points): Similar to energy, the system scores how close the song is to the user's acousticness preference.

The recommender sums all four scores and ranks songs from highest to lowest. It returns the top 5 recommendations.

---

## 4. Data  

The dataset contains **18 songs** across 12 genres: pop, lofi, R&B, rock, classical, hip-hop, country, electronic, jazz, synthwave, indie pop, and ambient. Each song has attributes including mood, energy level (0.0–1.0), tempo, valence, danceability, and acousticness. The dataset was provided as-is for this simulation; no songs were added or removed. The catalog is small and skews slightly toward pop and lofi genres, which may introduce popularity bias. Notably, some genres (like metal or reggae) are completely missing.  

---

## 5. Strengths  

VibeFinder works well for users with **clear, primary preferences**. When testing three normal user profiles (Late Night R&B, Pop Energy, and Chill Lofi), the system correctly ranked the expected #1 song in all three cases. The weighting scheme effectively captures that genre is often the strongest signal of user satisfaction. For users who know exactly what genre and mood they want, the system delivers reliable results.  

---

## 6. Limitations and Bias 

**Genre Lock-In**: The genre match is weighted twice as much as mood, which traps users in their favorite genre and prevents them from discovering songs in related or different genres.

**Binary Matching**: Genres and moods use exact matching, so "indie pop" and "pop" are treated as completely different, ignoring how closely related they are.

**Dataset Bias**: Pop and lofi songs make up 44% of the catalog, while other genres like country and classical are underrepresented, leading to more options for pop/lofi fans.

**Unused Features**: The system ignores important song qualities like valence (positivity), danceability (groove), and tempo (pace), even though they're available in the data.

**No Top-K Diversity**: The top 5 recommendations could all be from the same genre or artist, offering no variety within a user's preferences.

**Conflicting Preferences**: Users with contradictory tastes, like wanting high energy and high acousticness at the same time, get uniformly low scores across all songs.

## 7. Evaluation  

I tested the recommender with 5 different user profiles to see how well it matched expectations. For the first three normal profiles, the top recommendation was exactly what I expected:

1. **Late Night R&B** (R&B, sad, low energy, medium acoustic): "Midnight Blues" ranked #1 with a score of 4.77 out of 5.0.
2. **Pop Energy** (pop, happy, high energy, low acoustic): "Sunrise City" ranked #1 with 4.84 out of 5.0.
3. **Chill Lofi** (lofi, chill, medium energy, high acoustic): "Midnight Coding" ranked #1 with 4.94 out of 5.0.

For the two adversarial profiles with conflicting preferences, the results showed the system's biases:

4. **Adversarial Rock** (rock, intense, low energy, high acoustic): Despite the conflicting energy and acousticness, "Storm Runner" ranked #1 because of the strong genre match.
5. **Adversarial Neutral** (pop, intense, high energy, high acoustic): Even with neutral numeric preferences, the genre match still dominated, putting "Tempest Overture" at #1.

I also ran a simple experiment by halving the genre weight and doubling the energy weight. This changed the #1 recommendation for the Adversarial Neutral profile from "Tempest Overture" to "Rooftop Lights", proving that genre is the dominant signal in the scoring system.


---

## 8. Future Work  

**Reduce Genre Lock-In**: Lower the genre match weight (e.g., +1.5 instead of +2.0) to encourage cross-genre discovery.

**Use Ignored Features**: Incorporate valence and danceability into scoring. Use the `likes_acoustic` preference to penalize acoustic songs for users who dislike them.

**Fuzzy Matching**: Implement genre/mood similarity so "pop" and "indie pop" are recognized as related.

**Diversity in Top-K**: De-duplicate similar songs and promote diversity in the final recommendations.

**Rebalance Dataset**: Collect or create additional songs to reduce pop/lofi bias and represent underrepresented genres.

**Collaborative Filtering**: Combine content-based scoring with information about other similar users' preferences.

**Better Explanations**: Provide richer justifications for why each song was recommended (e.g., "This song has the energy you like and shares mood with your favorite artist").  

---

## 9. Personal Reflection  

Building VibeFinder taught me that recommender systems involve difficult tradeoffs. Simple scoring rules (like heavy genre weighting) make intuitive sense but can trap users in filter bubbles. The most surprising discovery was how adversarial user inputs—seemingly reasonable preferences that conflict internally—produce universally poor recommendations, revealing the brittleness of content-based approaches. This project changed how I think about Spotify and Apple Music: when they recommend obscure genres or "discover weekly" playlists, they're solving complex optimization problems to balance personalization with diversity, discovery, and fairness. A truly good recommender isn't just accurate—it has to know when to break its own rules.  
