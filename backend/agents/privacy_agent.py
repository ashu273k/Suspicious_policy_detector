"""
Privacy Agent — Analyzes data collection, GDPR/CCPA risks, and consent issues.
Uses Prompt 3 (privacy/data collection) from the LexGuard specification.
"""

from .base_agent import BaseAgent


class PrivacyAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "Privacy & Data Protection Agent"

    @property
    def handles_clause_types(self) -> list[str]:
        return [
            "DATA_COLLECTION",
            "NON_DISCLOSURE",
            "GENERAL",
        ]

    def get_prompt(self, clause_text: str, clause_type: str, full_contract: str) -> str:
        return f"""You are a data privacy expert analyzing a contract clause for GDPR, CCPA, and general
privacy risks from the perspective of the data subject (the individual whose data is collected).

Clause text: "{clause_text}"

Return JSON:
{{
  "severity": <"CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE">,
  "data_types_at_risk": [<list: e.g. "location", "biometric", "financial", "behavioral">],
  "consent_issues": <true/false — does the clause bypass meaningful consent?>,
  "data_sharing": <true/false — does it allow sharing with third parties?>,
  "retention_problem": <true/false — unclear or indefinite data retention?>,
  "right_to_delete": <true/false — does it restrict the individual's right to deletion?>,
  "plain_english": <what this means for the person's privacy, 2-3 sentences>,
  "recommendation": <what the individual should demand or watch for>
}}

Return only valid JSON."""
