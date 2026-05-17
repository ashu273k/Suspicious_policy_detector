"""
Clause Embedder — Generate sentence-transformer embeddings for clauses.
Stores embeddings in ChromaDB for similarity search.
"""

from sentence_transformers import SentenceTransformer
from config import HF_MODEL_NAME

_model = None


def _get_model() -> SentenceTransformer:
    """Lazy model initialization."""
    global _model
    if _model is None:
        _model = SentenceTransformer(HF_MODEL_NAME)
    return _model


def embed_text(text: str) -> list[float]:
    """Generate embedding for a single text string."""
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_clauses(clauses: list[dict]) -> list[dict]:
    """
    Generate embeddings for a list of clause dicts.
    Adds 'embedding' key to each clause dict.

    Args:
        clauses: List of clause dicts with 'original_text' key

    Returns:
        Same list with 'embedding' added to each dict
    """
    model = _get_model()

    texts = [c.get("original_text", c.get("summary", "")) for c in clauses]

    if not texts:
        return clauses

    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    for clause, emb in zip(clauses, embeddings):
        clause["embedding"] = emb.tolist()

    return clauses
