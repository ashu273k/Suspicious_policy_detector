"""
Score Aggregator — Combine per-clause scores into overall contract assessment.
"""

from .risk_scorer import score_contract, score_clause
from .rubric import get_category_multiplier


def aggregate_results(analyzed_clauses: list[dict]) -> dict:
    """
    Aggregate analysis results into a comprehensive score report.

    Args:
        analyzed_clauses: List of dicts from orchestrator with clause + agent_results

    Returns:
        Dict with overall score, grade, breakdown, and top risks
    """
    # Get base score
    score_result = score_contract(analyzed_clauses)

    # Identify flagged clauses (severity > NONE)
    flagged = [
        c for c in analyzed_clauses
        if c.get("max_severity", "NONE") != "NONE"
    ]

    # Sort by severity for top risks
    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
    flagged_sorted = sorted(
        flagged,
        key=lambda c: severity_order.get(c.get("max_severity", "NONE"), 0),
        reverse=True,
    )

    # Build top risks summary
    top_risks = []
    for c in flagged_sorted[:5]:  # Top 5 risks
        clause = c.get("clause", {})
        best_result = _get_best_agent_result(c.get("agent_results", []))

        top_risks.append({
            "clause_id": clause.get("clause_id"),
            "clause_type": clause.get("clause_type"),
            "severity": c.get("max_severity"),
            "summary": best_result.get("risk_summary", best_result.get("plain_english", "")),
            "negotiation_tip": best_result.get("negotiation_tip", best_result.get("recommendation", "")),
        })

    # Category breakdown
    category_counts = {}
    for c in flagged:
        for r in c.get("agent_results", []):
            cat = r.get("risk_category", "GENERAL")
            if cat not in category_counts:
                category_counts[cat] = 0
            category_counts[cat] += 1

    return {
        **score_result,
        "flagged_clauses": len(flagged),
        "total_clauses": len(analyzed_clauses),
        "top_risks": top_risks,
        "category_breakdown": category_counts,
    }


def _get_best_agent_result(agent_results: list[dict]) -> dict:
    """Get the most severe agent result for a clause."""
    if not agent_results:
        return {}

    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
    return max(
        agent_results,
        key=lambda r: severity_order.get(r.get("severity", "NONE"), 0),
    )
