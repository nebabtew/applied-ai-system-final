import os
from pathlib import Path
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    source_file: str
    category: str  # "genre" or "mood"
    name: str
    text: str


class Retriever:
    def __init__(self, knowledge_base_dir: str = "knowledge_base"):
        self.chunks: list[Chunk] = []
        kb_path = Path(knowledge_base_dir)

        for category in ("genres", "moods"):
            category_label = category.rstrip("s")  # "genres" -> "genre", "moods" -> "mood"
            folder = kb_path / category
            if not folder.exists():
                continue
            for md_file in sorted(folder.glob("*.md")):
                text = md_file.read_text(encoding="utf-8")
                name = md_file.stem.lower()
                self.chunks.append(Chunk(
                    source_file=str(md_file),
                    category=category_label,
                    name=name,
                    text=text,
                ))

        # Allow single-char tokens so "R&B" → ["R", "B"] rather than being dropped
        self.vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
        self.matrix = self.vectorizer.fit_transform([c.text for c in self.chunks])

    def retrieve(self, song: dict, k: int = 3) -> list[Chunk]:
        query = f"{song.get('genre', '')} {song.get('mood', '')}".strip()
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        top_indices = scores.argsort()[::-1][:k]
        return [self.chunks[i] for i in top_indices]


if __name__ == "__main__":
    retriever = Retriever()
    test_song = {"genre": "R&B", "mood": "sad"}
    results = retriever.retrieve(test_song, k=3)
    print(f"Top {len(results)} chunks for song {test_song}:\n")
    for chunk in results:
        print(f"  category={chunk.category!r}, name={chunk.name!r}")
        print(f"  text preview: {chunk.text[:80]!r}")
        print()
