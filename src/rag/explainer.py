import os

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def explain(
    song: dict,
    user_prefs: dict,
    retrieved_chunks: list,
    model_name: str = "gemini-2.5-flash",
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "[LLM unavailable] Recommended based on genre and mood match."

    context = "\n\n".join(
        f"[{chunk.category.upper()}: {chunk.name}]\n{chunk.text}"
        for chunk in retrieved_chunks
    )

    prompt = f"""You are a music recommendation assistant.

Use ONLY the information in the RETRIEVED CONTEXT below to explain why this song fits the user's vibe.
Do NOT invent facts about the song, artist, release date, or chart performance.
If the context does not support a claim, do not make that claim.
Keep the explanation to 2-3 sentences. Be specific.

USER PROFILE:
- Favorite genre: {user_prefs.get("genre", "unknown")}
- Favorite mood: {user_prefs.get("mood", "unknown")}
- Target energy: {user_prefs.get("energy", "unknown")}
- Acousticness preference: {user_prefs.get("acousticness", "unknown")}

SONG:
- Title: {song.get("title", "unknown")}
- Artist: {song.get("artist", "unknown")}
- Genre: {song.get("genre", "unknown")}
- Mood: {song.get("mood", "unknown")}
- Energy: {song.get("energy", "unknown")}
- Acousticness: {song.get("acousticness", "unknown")}

RETRIEVED CONTEXT:
{context}
"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "[LLM unavailable] Recommended based on genre and mood match."


if __name__ == "__main__":
    from src.rag.retriever import Retriever

    test_song = {
        "id": 11,
        "title": "Midnight Blues",
        "artist": "Soul Echo",
        "genre": "R&B",
        "mood": "sad",
        "energy": 0.25,
        "acousticness": 0.78,
    }
    test_user_prefs = {
        "genre": "R&B",
        "mood": "sad",
        "energy": 0.30,
        "acousticness": 0.60,
    }

    retriever = Retriever()
    chunks = retriever.retrieve(test_song, k=3)

    print("Retrieved chunks:")
    for chunk in chunks:
        print(f"  [{chunk.category}] {chunk.name}")
    print()

    explanation = explain(test_song, test_user_prefs, chunks)
    print("Explanation:")
    print(explanation)
