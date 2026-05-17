"""
Clause Extractor — Uses LLM to extract and label clauses from contract text.
Implements Prompt 1 from the LexGuard specification.
"""

import json
import re
from llm.router import call_llm
from ingestion.preprocessor import estimate_token_count
from ingestion.chunker import chunk_for_clause_extraction


EXTRACTION_PROMPT = """You are a legal document analyst. Given the contract text below, extract every distinct contractual clause.

For each clause, return a JSON array with this structure:
{{
  "clause_id": <sequential int>,
  "original_text": <verbatim clause text>,
  "clause_type": <one of: NON_COMPETE, NON_DISCLOSURE, ARBITRATION, IP_ASSIGNMENT,
                  DATA_COLLECTION, AUTO_RENEWAL, TERMINATION, LIABILITY_LIMIT,
                  INDEMNIFICATION, GOVERNING_LAW, PAYMENT_PENALTY, GENERAL>,
  "parties_affected": <"employee" | "contractor" | "user" | "vendor" | "both">,
  "summary": <one sentence plain-English summary>
}}

Rules:
- Extract every clause, even seemingly standard ones
- Do NOT paraphrase original_text — copy it verbatim
- If a clause covers multiple types, pick the primary one
- Return only valid JSON, no markdown fences

CONTRACT TEXT:
{contract_text}"""


def extract_clauses(contract_text: str) -> list[dict]:
    """
    Extract structured clauses from contract text using LLM.

    Args:
        contract_text: Full preprocessed contract text

    Returns:
        List of clause dicts with clause_id, original_text, clause_type, etc.
    """
    token_count = estimate_token_count(contract_text)

    # For very long documents, chunk and extract per-chunk
    if token_count > 6000:
        return _extract_chunked(contract_text, token_count)

    prompt = EXTRACTION_PROMPT.format(contract_text=contract_text)
    response = call_llm(prompt, doc_token_count=token_count)

    clauses = _parse_clause_response(response)
    return _renumber_clauses(clauses)


def _extract_chunked(contract_text: str, total_tokens: int) -> list[dict]:
    """Extract clauses from multiple chunks and merge."""
    chunks = chunk_for_clause_extraction(contract_text)
    all_clauses = []

    for chunk in chunks:
        prompt = EXTRACTION_PROMPT.format(contract_text=chunk)
        response = call_llm(prompt, doc_token_count=total_tokens)
        clauses = _parse_clause_response(response)
        all_clauses.extend(clauses)

    # Deduplicate by original_text similarity
    seen_texts = set()
    unique_clauses = []
    for clause in all_clauses:
        text_key = clause.get("original_text", "")[:100].strip().lower()
        if text_key not in seen_texts:
            seen_texts.add(text_key)
            unique_clauses.append(clause)

    return _renumber_clauses(unique_clauses)


def _parse_clause_response(response: str) -> list[dict]:
    """Parse LLM response into clause dicts, handling formatting issues."""
    # Strip markdown code fences if present
    response = response.strip()
    response = re.sub(r"^```(?:json)?\s*\n?", "", response)
    response = re.sub(r"\n?```\s*$", "", response)

    try:
        data = json.loads(response)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "clauses" in data:
            return data["clauses"]
        else:
            return [data]
    except json.JSONDecodeError:
        # Try to extract JSON array from response
        match = re.search(r"\[[\s\S]*\]", response)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        print(f"⚠️  Failed to parse clause extraction response")
        return []


def _renumber_clauses(clauses: list[dict]) -> list[dict]:
    """Renumber clause IDs sequentially."""
    for i, clause in enumerate(clauses):
        clause["clause_id"] = i + 1
    return clauses
