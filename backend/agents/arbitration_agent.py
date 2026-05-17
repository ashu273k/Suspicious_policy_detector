"""
Arbitration Agent — Detects one-sided dispute resolution, venue restrictions,
and class-action waivers.
"""

from .base_agent import BaseAgent


class ArbitrationAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "Arbitration & Dispute Resolution Agent"

    @property
    def handles_clause_types(self) -> list[str]:
        return [
            "ARBITRATION",
            "GOVERNING_LAW",
            "GENERAL",
        ]

    def get_prompt(self, clause_text: str, clause_type: str, full_contract: str) -> str:
        return f"""You are an adversarial legal analyst specializing in dispute resolution clauses.
You represent the WEAKER party (employee, freelancer, consumer) — NOT the company.

Clause type: {clause_type}
Clause text: "{clause_text}"

Analyze for one-sided dispute resolution mechanisms. Return JSON:
{{
  "severity": <"CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE">,
  "risk_category": "LEGAL",
  "mandatory_arbitration": <true/false>,
  "class_action_waiver": <true/false>,
  "venue_restriction": <true/false — is the venue inconvenient for the individual?>,
  "cost_shifting": <true/false — does the individual bear arbitration costs?>,
  "limited_discovery": <true/false — are discovery rights restricted?>,
  "risk_summary": <1-2 sentences on what's risky>,
  "plain_english": <2-3 sentences explaining impact in plain language>,
  "red_flags": [<specific problematic phrases from the clause>],
  "negotiation_tip": <one actionable suggestion to push back>
}}

Return only valid JSON."""
