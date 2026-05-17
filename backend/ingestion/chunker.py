"""
Semantic Chunker — Split contract text into meaningful chunks.
Uses sentence boundaries and paragraph markers for context-preserving chunking.
"""

import re


def chunk_text(
    text: str,
    max_chunk_size: int = 2000,
    overlap: int = 200,
) -> list[dict]:
    """
    Split text into overlapping chunks for processing.

    Args:
        text: Full document text
        max_chunk_size: Maximum characters per chunk
        overlap: Character overlap between chunks for context

    Returns:
        List of dicts with keys: chunk_id, text, start_char, end_char
    """
    if not text.strip():
        return []

    # Split into paragraphs first
    paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks = []
    current_chunk = ""
    chunk_start = 0
    char_offset = 0

    for para in paragraphs:
        # If adding this paragraph exceeds max size, save current chunk
        if current_chunk and len(current_chunk) + len(para) + 2 > max_chunk_size:
            chunks.append({
                "chunk_id": len(chunks),
                "text": current_chunk.strip(),
                "start_char": chunk_start,
                "end_char": chunk_start + len(current_chunk.strip()),
            })

            # Start new chunk with overlap from end of previous
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + "\n\n" + para
            chunk_start = char_offset - len(overlap_text)
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
                chunk_start = char_offset

        char_offset += len(para) + 2  # +2 for paragraph separator

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append({
            "chunk_id": len(chunks),
            "text": current_chunk.strip(),
            "start_char": chunk_start,
            "end_char": chunk_start + len(current_chunk.strip()),
        })

    return chunks


def chunk_for_clause_extraction(text: str, max_tokens: int = 4000) -> list[str]:
    """
    Split text into chunks sized for LLM clause extraction.
    Estimates ~4 chars per token.

    Returns:
        List of text chunks ready for the clause extraction prompt.
    """
    max_chars = max_tokens * 4
    chunks = chunk_text(text, max_chunk_size=max_chars, overlap=400)
    return [c["text"] for c in chunks]
