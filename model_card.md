# Model Card: VibeFinder 2.0 (RAG + Guardrails)

## 1. Intended Use
VibeFinder is a classroom simulation designed to demonstrate content-based recommendation logic and Retrieval-Augmented Generation (RAG). It is intended for educational purposes, not commercial deployment.

## 2. How It Works (Algorithm Summary)
**VibeFinder 1.0 Logic:** Uses a proximity scoring formula (1.0 - absolute difference) to score how closely a song's attributes (energy, acousticness) match a user's preferences. It adds flat bonuses for exact genre (2.0 pts) and mood (1.0 pt) matches.
**VibeFinder 2.0 Logic:** Adds an AI Explainer. A TF-IDF retriever pulls relevant documents from a Markdown knowledge base. An LLM (Gemini 1.5 Flash) uses that retrieved text via a grounded prompt to explain the recommendation to the user.

## 3. Data Used
- **Song Catalog:** 18 total songs spanning 12 distinct genres (expanded from an original 10-song baseline).
- **Knowledge Base:** 24 total Markdown documents detailing specific musical genres and emotional moods. 

## 4. Strengths
The system correctly prioritizes primary signals (genre overlap) while using secondary signals (energy/acousticness proximity) to break ties. In 2.0, the RAG system successfully prevents the LLM from inventing external facts by strictly grounding it in the knowledge base.

## 5. Limitations and Bias (VibeFinder 1.0)
1. **Genre Lock-In:** A 2.0 weight on genre creates filter bubbles.
2. **Binary Matching:** Punishes similar but non-exact genres (e.g., indie pop vs. pop).
3. **Dataset Bias:** Pop/lofi make up 44% of the catalog.
4. **Unused Features:** Valence and danceability are loaded but never scored.
5. **No Top-K Diversity:** Top 5 results can be entirely the same artist/genre.

## 6. New Biases Introduced (VibeFinder 2.0)
- **Language Bias:** The LLM may favor English-language descriptors and Western music theory constructs.
- **Knowledge Base Bias:** The retrieved chunks reflect the subjective writing biases of the author who defined the "moods."
- **Retrieval Bias:** TF-IDF favors literal, exact word overlap over semantic meaning.
- **Training Data Bias:** The inherent, unknown biases present in Gemini's base training data.

## 7. Reliability Evidence and Testing
The system was evaluated against 3 distinct user profiles ("Late Night R&B", "Pop Energy", "Chill Lofi"). 
The guardrail component successfully caught hallucinations during Test B. When the LLM was forced to output fake details (e.g., release year and Billboard chart performance), two of the three checks fired: the lexical grounding check (−0.5, zero token overlap with retrieved chunks) and the hallucination pattern check (−0.3, matched "2003", "released in", "peaked at"). The length check did not fire. Final confidence: 0.20 (passed = False).

## 8. AI Collaboration Reflection
- **Helpful AI Interaction:** Claude Code cleanly wrote the TF-IDF retriever logic using `scikit-learn` on the first try, saving significant manual development time.
- **Flawed AI Interaction:** When batch-creating the knowledge base corpus, Claude Code created 6 completely empty mood files rather than actually writing the content, requiring me to step in and fix the generation.

## 9. Ideas for Improvement (Future Work)
- Integrate fuzzy matching for adjacent genres (e.g., scoring indie-pop and pop as 0.8 matches).
- Implement a diversity penalty to prevent recommending three songs by the same artist in a row.
- Move from TF-IDF to a dense vector embedding model to capture semantic meaning during retrieval.