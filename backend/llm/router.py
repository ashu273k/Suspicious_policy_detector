"""
LLM Router — Route all model calls through Groq (single provider).
"""

from .groq_client import call_groq


def call_llm(
    prompt: str,
    doc_token_count: int = 0,
    system_message: str = "",
) -> str:
    """Call the configured model via Groq.

    Args:
        prompt: The prompt text
        doc_token_count: Token count hint used for throttling compatibility
        system_message: Optional system prompt

    Returns:
        LLM response text
    """
    full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
    return call_groq(full_prompt, doc_token_count=doc_token_count)
