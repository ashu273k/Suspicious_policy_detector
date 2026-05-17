"""
Base Agent — Abstract base class for all analysis agents.
"""

import json
import re
from abc import ABC, abstractmethod
from llm.router import call_llm


class BaseAgent(ABC):
    """
    Abstract base class for LexGuard analysis agents.
    Each agent specializes in detecting a specific category of contract risk.
    """

    def __init__(self, doc_token_count: int = 0):
        self.doc_token_count = doc_token_count

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""
        ...

    @property
    @abstractmethod
    def handles_clause_types(self) -> list[str]:
        """List of clause types this agent specializes in."""
        ...

    @abstractmethod
    def get_prompt(self, clause_text: str, clause_type: str, full_contract: str) -> str:
        """Build the analysis prompt for this agent."""
        ...

    def analyze(self, clause: dict, full_contract: str = "") -> dict:
        """
        Run analysis on a single clause.

        Args:
            clause: Dict with clause_id, original_text, clause_type, etc.
            full_contract: Full contract text for context

        Returns:
            Dict with agent-specific risk analysis results
        """
        clause_text = clause.get("original_text", "")
        clause_type = clause.get("clause_type", "GENERAL")

        prompt = self.get_prompt(clause_text, clause_type, full_contract)

        try:
            response = call_llm(prompt, doc_token_count=self.doc_token_count)
            result = self._parse_response(response)
            result["agent"] = self.name
            result["clause_id"] = clause.get("clause_id")
            return result
        except Exception as e:
            return {
                "agent": self.name,
                "clause_id": clause.get("clause_id"),
                "severity": "LOW",
                "error": str(e),
            }

    def can_handle(self, clause_type: str) -> bool:
        """Check if this agent should analyze a given clause type."""
        return clause_type in self.handles_clause_types or "ALL" in self.handles_clause_types

    def _parse_response(self, response: str) -> dict:
        """Parse JSON response from LLM, handling formatting issues."""
        response = response.strip()
        response = re.sub(r"^```(?:json)?\s*\n?", "", response)
        response = re.sub(r"\n?```\s*$", "", response)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in response
            match = re.search(r"\{[\s\S]*\}", response)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass

            return {
                "severity": "LOW",
                "risk_summary": response[:500],
                "parse_error": True,
            }
