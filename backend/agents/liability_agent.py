"""
Liability Agent — Detects hidden obligations, one-sided terms, and liability risks.
Uses Prompt 2 (per-clause risk analysis) from the LexGuard specification.
"""

from .base_agent import BaseAgent


class LiabilityAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "Liability & Obligations Agent"

    @property
    def handles_clause_types(self) -> list[str]:
        return [
            "ALL",  # This agent runs on all clause types
        ]

    def get_prompt(self, clause_text: str, clause_type: str, full_contract: str) -> str:
        return f"""You are an adversarial legal analyst reviewing a contract clause on behalf of the WEAKER party
(employee, freelancer, or individual user — not the company that drafted this contract).

Clause type: {clause_type}
Clause text: "{clause_text}"

Analyze this clause strictly for risk to the weaker party. Return JSON:
{{
  "severity": <"CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE">,
  "risk_category": <"FINANCIAL" | "PRIVACY" | "EMPLOYMENT" | "IP" | "LEGAL" | "COMPLIANCE">,
  "risk_summary": <1-2 sentences: what specifically is risky>,
  "plain_english": <explain what this clause actually means in plain language, 2-3 sentences>,
  "real_world_impact": <describe a concrete scenario where this clause could harm the individual>,
  "red_flags": [<list of specific problematic phrases or terms>],
  "is_standard": <true if this is typical industry practice, false if unusually one-sided>,
  "negotiation_tip": <one actionable suggestion to push back or negotiate>
}}

Severity guide:
- CRITICAL: could cause major financial loss, career harm, or loss of rights
- HIGH: significantly limits the individual's rights or creates serious obligations
- MEDIUM: one-sided but common; limited practical impact
- LOW: standard clause, minor concern
- NONE: fair and balanced, no issue

Return only valid JSON."""
