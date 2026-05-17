"""
Vector Store — ChromaDB initialization and CRUD operations.
"""

import chromadb
from pathlib import Path
from config import CHROMA_PERSIST_DIR

_client = None
_collections = {}


def init_vector_store():
    """Initialize ChromaDB persistent client and default collections."""
    global _client, _collections

    _client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))

    # Create default collections
    _collections["clauses"] = _client.get_or_create_collection(
        name="contract_clauses",
        metadata={"description": "Extracted contract clauses with embeddings"},
    )
    _collections["benchmarks"] = _client.get_or_create_collection(
        name="benchmark_clauses",
        metadata={"description": "Standard fair/exploitative benchmark clauses"},
    )

    print(f"📦 ChromaDB initialized at {CHROMA_PERSIST_DIR}")
    return _client


def get_collection(name: str):
    """Get a ChromaDB collection by name."""
    if name not in _collections:
        if _client is None:
            init_vector_store()
        _collections[name] = _client.get_or_create_collection(name=name)
    return _collections[name]


def store_clauses(document_id: str, clauses: list[dict]):
    """
    Store clause embeddings in ChromaDB.

    Args:
        document_id: Unique document identifier
        clauses: List of clause dicts with 'embedding' key
    """
    collection = get_collection("clauses")

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for clause in clauses:
        if "embedding" not in clause:
            continue

        clause_id = f"{document_id}_clause_{clause.get('clause_id', 0)}"
        ids.append(clause_id)
        embeddings.append(clause["embedding"])
        documents.append(clause.get("original_text", ""))
        metadatas.append({
            "document_id": document_id,
            "clause_id": str(clause.get("clause_id", 0)),
            "clause_type": clause.get("clause_type", "GENERAL"),
            "summary": clause.get("summary", ""),
        })

    if ids:
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )


def search_similar(
    query_embedding: list[float],
    collection_name: str = "benchmarks",
    n_results: int = 5,
) -> list[dict]:
    """
    Search for similar clauses by embedding.

    Returns:
        List of dicts with id, document, metadata, distance
    """
    collection = get_collection(collection_name)

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
    except Exception:
        return []

    matches = []
    if results and results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            matches.append({
                "id": doc_id,
                "document": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })

    return matches


def delete_document(document_id: str):
    """Remove all clauses for a document from the vector store."""
    collection = get_collection("clauses")
    try:
        collection.delete(where={"document_id": document_id})
    except Exception:
        pass
