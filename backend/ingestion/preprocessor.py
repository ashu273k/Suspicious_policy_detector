"""
Text Preprocessor — Clean and normalize extracted document text.
"""

import re


def preprocess(text: str) -> str:
    """
    Clean and normalize contract text for analysis.

    Steps:
    1. Fix encoding artifacts
    2. Normalize whitespace
    3. Remove page numbers and headers/footers
    4. Normalize quote marks and dashes
    """
    if not text:
        return ""

    # Fix common encoding issues
    text = text.replace("\x00", "")
    text = text.replace("\ufeff", "")  # BOM

    # Normalize unicode quotes and dashes
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "--")
    text = text.replace("\u2026", "...")

    # Remove page numbers (common patterns)
    text = re.sub(r"\n\s*Page\s+\d+\s*(of\s+\d+)?\s*\n", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"\n\s*-\s*\d+\s*-\s*\n", "\n", text)

    # Remove excessive whitespace but preserve paragraph breaks
    text = re.sub(r"[ \t]+", " ", text)  # Collapse horizontal whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 newlines (1 blank line)

    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Remove common header/footer patterns
    text = re.sub(
        r"(?:CONFIDENTIAL|PROPRIETARY|DRAFT)[\s-]*(?:\n|$)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


def estimate_token_count(text: str) -> int:
    """Estimate token count (~4 chars per token for English text)."""
    return len(text) // 4
