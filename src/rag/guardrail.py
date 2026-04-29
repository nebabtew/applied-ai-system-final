import re
from dataclasses import dataclass

from src.rag.retriever import Chunk


@dataclass
class GuardrailResult:
    confidence: float
    passed: bool
    warnings: list[str]


_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "this", "that",
    "these", "those", "of", "in", "to", "for", "with", "and", "or",
    "but", "it", "its", "be", "by", "on", "at", "as",
}

_HALLUCINATION_PATTERNS = [
    r"\b(19|20)\d{2}\b",
    r"released in",
    r"peaked at",
    r"Billboard",
    r"Grammy",
    r"chart",
    r"album of the year",
    r"debut album",
    r"record label",
]


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"\b\w+\b", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) >= 4}


def validate(explanation: str, retrieved_chunks: list) -> GuardrailResult:
    confidence = 1.0
    warnings: list[str] = []

    # Check 1 — Length sanity (weight 0.2)
    sentences = [s for s in re.split(r"[.!?]", explanation) if s.strip()]
    n = len(sentences)
    if not (1 <= n <= 5):
        confidence -= 0.2
        warnings.append(f"Explanation length out of range: {n} sentences")

    # Check 2 — Lexical grounding (weight 0.5)
    expl_words = _tokenize(explanation)
    chunk_words = _tokenize(" ".join(c.text for c in retrieved_chunks))
    ratio = len(expl_words & chunk_words) / len(expl_words) if expl_words else 0.0
    if ratio < 0.30:
        confidence -= 0.5
        warnings.append(f"Low lexical grounding: {ratio:.2f} (threshold 0.30)")

    # Check 3 — Forbidden hallucination patterns (weight 0.3)
    matches = []
    for pattern in _HALLUCINATION_PATTERNS:
        for m in re.finditer(pattern, explanation, re.IGNORECASE):
            matches.append(m.group())
    if matches:
        confidence -= 0.3
        for matched_text in matches[:3]:
            warnings.append(f"Possible hallucinated claim: '{matched_text}'")

    confidence = max(0.0, confidence)
    return GuardrailResult(confidence=confidence, passed=confidence >= 0.7, warnings=warnings)


if __name__ == "__main__":
    base_chunks = [
        Chunk(
            source_file="",
            category="genre",
            name="r&b",
            text="R&B is a genre rooted in introspective emotional storytelling...",
        ),
        Chunk(
            source_file="",
            category="mood",
            name="sad",
            text="Sad music uses slow tempos, acoustic textures, low energy...",
        ),
    ]

    cases = [
        (
            "Test A — clean output",
            "Midnight Blues fits your R&B preference because the genre suits introspective listening. "
            "Sad mood music typically uses slow tempos and acoustic textures, which match this song's profile.",
        ),
        (
            "Test B — hallucinated output",
            "Midnight Blues by Soul Echo was released in 2003 and peaked at #14 on the Billboard R&B chart.",
        ),
        (
            "Test C — ungrounded output",
            "Pizza tastes good. Birds fly south. Trains run on tracks.",
        ),
    ]

    for label, explanation in cases:
        result = validate(explanation, base_chunks)
        print(f"{label}")
        print(f"  confidence : {result.confidence:.2f}")
        print(f"  passed     : {result.passed}")
        if result.warnings:
            for w in result.warnings:
                print(f"  warning    : {w}")
        else:
            print("  warnings   : none")
        print()
