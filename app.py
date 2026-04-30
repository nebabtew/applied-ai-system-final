import streamlit as st

from src.recommender import load_songs, score_song, recommend_songs
from src.rag.retriever import Retriever
from src.rag.explainer import explain
from src.rag.guardrail import validate


st.set_page_config(page_title="VibeFinder 2.0", page_icon="🎵", layout="wide")


PRESETS = {
    "— Custom —": None,
    "Late Night R&B": {"genre": "R&B", "mood": "sad", "energy": 0.30, "acousticness": 0.60},
    "Pop Energy": {"genre": "pop", "mood": "happy", "energy": 0.85, "acousticness": 0.15},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.40, "acousticness": 0.75},
}


@st.cache_resource
def get_songs():
    return load_songs("data/songs.csv")


@st.cache_resource
def get_retriever():
    return Retriever()


def safe_index(options, value, default=0):
    if value in options:
        return options.index(value)
    return default


def main():
    songs = get_songs()
    retriever = get_retriever()

    genres = sorted({s["genre"] for s in songs})
    moods = sorted({s["mood"] for s in songs})

    if "preset_applied" not in st.session_state:
        st.session_state.preset_applied = None

    # ---------- Sidebar ----------
    with st.sidebar:
        st.title("Your Vibe")

        preset_name = st.selectbox("Preset", list(PRESETS.keys()), key="preset_select")

        # If preset just changed and is not custom, pre-fill widget state.
        if preset_name != st.session_state.preset_applied:
            preset = PRESETS[preset_name]
            if preset is not None:
                st.session_state["genre_select"] = preset["genre"] if preset["genre"] in genres else genres[0]
                st.session_state["mood_select"] = preset["mood"] if preset["mood"] in moods else moods[0]
                st.session_state["energy_slider"] = preset["energy"]
                st.session_state["acoustic_slider"] = preset["acousticness"]
            st.session_state.preset_applied = preset_name

        genre = st.selectbox(
            "Genre",
            genres,
            index=safe_index(genres, st.session_state.get("genre_select", genres[0])),
            key="genre_select",
        )
        mood = st.selectbox(
            "Mood",
            moods,
            index=safe_index(moods, st.session_state.get("mood_select", moods[0])),
            key="mood_select",
        )
        energy = st.slider("Energy", 0.0, 1.0, st.session_state.get("energy_slider", 0.5), step=0.05, key="energy_slider")
        acousticness = st.slider(
            "Acousticness",
            0.0, 1.0,
            st.session_state.get("acoustic_slider", 0.5),
            step=0.05,
            key="acoustic_slider",
        )
        k = st.slider("How many recommendations?", 1, 5, 3)

        run = st.button("🔮 Find my vibe", type="primary", use_container_width=True)

    # ---------- Main ----------
    st.title("🎵 VibeFinder 2.0")
    st.caption(
        "A content-based music recommender wrapped in a RAG explainer "
        "and a three-check guardrail."
    )

    with st.expander("How it works"):
        st.markdown(
            "**Stage 1 — Scoring.** Each song earns up to 5.0 points: "
            "genre match (+2.0), mood match (+1.0), energy proximity (up to +1.0), "
            "acousticness proximity (up to +1.0). Songs are sorted descending.\n\n"
            "**Stage 2 — Retrieval.** A TF-IDF retriever indexes 24 markdown docs "
            "(12 genres + 12 moods) in `knowledge_base/`. The top 3 chunks for the "
            "song's `<genre> <mood>` query are pulled.\n\n"
            "**Stage 3 — Grounded explanation.** Gemini 1.5 Flash gets the song, the "
            "user profile, and ONLY the retrieved chunks. The prompt forbids inventing "
            "facts about the artist or chart performance.\n\n"
            "**Stage 4 — Guardrail.** Three checks run on the explanation: "
            "length sanity (1–5 sentences, weight 0.2), lexical grounding against the "
            "chunks (≥30%, weight 0.5), and forbidden hallucination patterns "
            "(years, 'Billboard', 'Grammy', etc., weight 0.3). Confidence ≥ 0.7 passes."
        )

    user_prefs = {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "acousticness": acousticness,
    }

    if not run:
        st.info("Pick a profile in the sidebar and click Find my vibe to run the pipeline.")
        st.caption("VibeFinder 2.0 · CodePath AI110 Module 5 final project")
        return

    st.subheader(
        f"Active profile · {genre} / {mood} · energy {energy:.2f} · acousticness {acousticness:.2f}"
    )

    recs = recommend_songs(user_prefs, songs, k=k)

    # Run pipeline once per card; collect results for header metrics.
    cards = []
    with st.spinner("Running recommender + retrieval + Gemini + guardrail..."):
        for song, score, _reasons_str in recs:
            _score, reasons = score_song(user_prefs, song)
            chunks = retriever.retrieve(song, k=3)
            explanation = explain(song, user_prefs, chunks)
            guard = validate(explanation, chunks)
            cards.append((song, score, reasons, chunks, explanation, guard))

    # ---------- Top metrics ----------
    if cards:
        avg_score = sum(c[1] for c in cards) / len(cards)
        avg_conf = sum(c[5].confidence for c in cards) / len(cards)
        n_passed = sum(1 for c in cards if c[5].passed)

        m1, m2, m3 = st.columns(3)
        m1.metric("Avg recommendation score", f"{avg_score:.2f} / 5.0")
        m2.metric("Avg guardrail confidence", f"{avg_conf:.2f}")
        m3.metric("Guardrail passed", f"{n_passed} / {len(cards)}")

    # ---------- Cards ----------
    for i, (song, score, reasons, chunks, explanation, guard) in enumerate(cards, start=1):
        status_icon = "✅" if guard.passed else "⚠️"
        st.markdown(
            f"### #{i} · {song['title']} — {song['artist']}  "
            f"`{song['genre']}` `{song['mood']}`  ·  "
            f"score {score:.2f}  ·  {status_icon} confidence {guard.confidence:.2f}"
        )

        left, right = st.columns([1, 2])

        with left:
            st.markdown("**🧮 Score breakdown**")
            for r in reasons:
                st.markdown(f"- {r}")
            st.progress(min(score / 5.0, 1.0), text=f"{score:.2f} / 5.00")
            with st.expander("Song attributes"):
                st.markdown(
                    f"- energy: `{song['energy']}`\n"
                    f"- acousticness: `{song['acousticness']}`\n"
                    f"- valence: `{song['valence']}`\n"
                    f"- danceability: `{song['danceability']}`\n"
                    f"- tempo_bpm: `{song['tempo_bpm']}`"
                )

        with right:
            st.markdown("**📚 Retrieved context**")
            chips = "  ".join(f"`{c.category}: {c.name}`" for c in chunks)
            st.markdown(chips)
            with st.expander("Show retrieved chunk text"):
                for c in chunks:
                    st.markdown(f"**[{c.category.upper()}: {c.name}]** _(from {c.source_file})_")
                    st.text(c.text)

            st.markdown("**💬 Grounded explanation**")
            st.info(explanation)

            st.markdown("**🛡️ Guardrail report**")
            g_left, g_right = st.columns([1, 2])
            with g_left:
                st.metric("Confidence", f"{guard.confidence:.2f}")
                st.markdown("✅ Passed" if guard.passed else "⚠️ Failed")
            with g_right:
                if guard.warnings:
                    for w in guard.warnings:
                        st.warning(w)
                else:
                    st.success("All three checks passed (length, grounding, no hallucination patterns).")

        st.divider()

    st.caption("VibeFinder 2.0 · CodePath AI110 Module 5 final project")


if __name__ == "__main__":
    main()
