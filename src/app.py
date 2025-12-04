import streamlit as st
from recommender import UserProfile, default_recommender

def main():
    st.title("Music Recommender Simulation")
    st.write("Answer a few quick questions to set up your vibe profile.")

    # User Inputs
    genre = st.text_input("What is your favorite genre?", placeholder="e.g., pop, lofi, rock")
    mood = st.text_input("What is your usual listening mood?", placeholder="e.g., chill, happy, intense")
    energy = st.slider("On average, how much energy do you like in your music?", 0.0, 1.0, 0.5)
    likes_acoustic = st.checkbox("Do you usually prefer more acoustic, less produced tracks?")

    if st.button("Get Recommendations"):
        # Build User Profile
        user = UserProfile(
            favorite_genre=genre or "pop",
            favorite_mood=mood or "happy",
            target_energy=energy,
            likes_acoustic=likes_acoustic,
        )

        # Get Recommendations
        try:
            recommender = default_recommender()
            top_songs = recommender.recommend(user, k=5)

            if not top_songs:
                st.warning("No songs available. Check that data/songs.csv exists.")
            else:
                st.subheader("Your Top Recommendations")
                for idx, song in enumerate(top_songs, start=1):
                    explanation = recommender.explain_recommendation(user, song)
                    with st.expander(f"{idx}. {song.title} - {song.artist}"):
                        st.write(f"**Genre:** {song.genre}")
                        st.write(f"**Mood:** {song.mood}")
                        st.write(f"**Why this track:** {explanation}")
                        
        except FileNotFoundError:
             st.error("Could not find the data file. Please ensure 'data/songs.csv' exists.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
