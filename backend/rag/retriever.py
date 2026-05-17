"""
RAG Retriever — Similarity search against benchmark clauses for comparison.
"""

from extraction.embedder import embed_text
from .vector_store import search_similar


def find_similar_benchmarks(clause_text: str, n_results: int = 3) -> list[dict]:
    """
    Find benchmark clauses similar to the given clause text.

    Args:
        clause_text: The clause text to compare against benchmarks
        n_results: Number of similar results to return

    Returns:
        List of matching benchmark clauses with similarity scores
    """
    embedding = embed_text(clause_text)
    matches = search_similar(
        query_embedding=embedding,
        collection_name="benchmarks",
        n_results=n_results,
    )

    return [
        {
            "benchmark_text": m["document"],
            "clause_type": m["metadata"].get("clause_type", ""),
            "is_fair": m["metadata"].get("is_fair", True),
            "similarity": 1 - m["distance"],  # Convert distance to similarity
        }
        for m in matches
    ]


def find_similar_past_clauses(clause_text: str, n_results: int = 5) -> list[dict]:
    """
    Find previously analyzed clauses similar to the given clause.
    Useful for comparing across multiple contracts.
    """
    embedding = embed_text(clause_text)
    matches = search_similar(
        query_embedding=embedding,
        collection_name="clauses",
        n_results=n_results,
    )

    return [
        {
            "document_id": m["metadata"].get("document_id", ""),
            "clause_text": m["document"],
            "clause_type": m["metadata"].get("clause_type", ""),
            "similarity": 1 - m["distance"],
        }
        for m in matches
    ]
