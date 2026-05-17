"""
IP Agent — Analyzes intellectual property ownership and transfer risks.
Uses Prompt 4 (IP & ownership) from the LexGuard specification.
"""

from .base_agent import BaseAgent


class IPAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "IP & Ownership Agent"

    @property
    def handles_clause_types(self) -> list[str]:
        return [
            "IP_ASSIGNMENT",
            "NON_COMPETE",
            "NON_DISCLOSURE",
        ]

    def get_prompt(self, clause_text: str, clause_type: str, full_contract: str) -> str:
        return f"""You are an intellectual property attorney analyzing a contract clause for IP ownership risks.
Your client is a freelancer, employee, or contractor — NOT the company.

Clause text: "{clause_text}"

Return JSON:
{{
  "severity": <"CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE">,
  "transfers_ip": <true/false>,
  "scope": <"work-related only" | "all work during employment" | "all work ever" | "unclear">,
  "pre_existing_work_at_risk": <true/false — could pre-existing work be captured?>,
  "moral_rights_waived": <true/false>,
  "perpetual_license": <true/false>,
  "plain_english": <2-3 sentences explaining what the individual gives up>,
  "red_flags": [<problematic phrases verbatim from the clause>],
  "recommendation": <what to negotiate for — e.g. carve-outs for side projects>
}}

Return only valid JSON."""
