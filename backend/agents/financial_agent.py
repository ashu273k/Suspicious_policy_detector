"""
Financial Agent — Detects hidden fees, auto-renewals, penalty clauses,
and payment terms unfavorable to the weaker party.
"""

from .base_agent import BaseAgent


class FinancialAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "Financial Risk Agent"

    @property
    def handles_clause_types(self) -> list[str]:
        return [
            "AUTO_RENEWAL",
            "PAYMENT_PENALTY",
            "TERMINATION",
            "INDEMNIFICATION",
            "LIABILITY_LIMIT",
        ]

    def get_prompt(self, clause_text: str, clause_type: str, full_contract: str) -> str:
        return f"""You are a financial risk analyst reviewing contract clauses for hidden costs,
penalties, and financial traps. You represent the WEAKER party — NOT the company.

Clause type: {clause_type}
Clause text: "{clause_text}"

Analyze for financial risks to the individual. Return JSON:
{{
  "severity": <"CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE">,
  "risk_category": "FINANCIAL",
  "auto_renewal": <true/false — does it auto-renew without clear opt-out?>,
  "hidden_fees": <true/false — are there fees not clearly disclosed?>,
  "penalty_clauses": <true/false — are there disproportionate penalties?>,
  "early_termination_cost": <true/false — costly to exit early?>,
  "uncapped_liability": <true/false — is financial exposure unlimited?>,
  "risk_summary": <1-2 sentences on what's financially risky>,
  "plain_english": <2-3 sentences explaining the financial impact>,
  "estimated_exposure": <rough estimate of potential financial exposure, or "unclear">,
  "red_flags": [<specific problematic financial terms>],
  "negotiation_tip": <one actionable suggestion to reduce financial risk>
}}

Return only valid JSON."""
