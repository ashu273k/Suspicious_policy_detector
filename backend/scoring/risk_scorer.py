"""
Risk Scorer — Calculate severity scores for individual clauses.
"""

from config import RISK_WEIGHTS


def score_clause(severity: str) -> int:
    """Get the numeric score for a severity level."""
    return RISK_WEIGHTS.get(severity.upper(), 0)


def score_contract(flagged_clauses: list[dict]) -> dict:
    """
    Calculate overall contract risk score from flagged clauses.

    Args:
        flagged_clauses: List of dicts with 'severity' key (or 'max_severity')

    Returns:
        Dict with overall_score (0-100), grade (A-F), clause_count, breakdown
    """
    raw = 0
    for c in flagged_clauses:
        sev = c.get("max_severity", c.get("severity", "NONE"))
        raw += RISK_WEIGHTS.get(sev, 0)

    normalized = min(100, raw)

    return {
        "overall_score": normalized,
        "grade": _get_grade(normalized),
        "clause_count": len(flagged_clauses),
        "breakdown": _count_by_severity(flagged_clauses),
    }


def _get_grade(score: int) -> str:
    """Convert numeric score to letter grade."""
    if score > 70:
        return "F"
    elif score > 50:
        return "D"
    elif score > 30:
        return "C"
    elif score > 15:
        return "B"
    else:
        return "A"


def _count_by_severity(clauses: list[dict]) -> dict:
    """Count clauses by severity level."""
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "NONE": 0}
    for c in clauses:
        sev = c.get("max_severity", c.get("severity", "NONE"))
        if sev in counts:
            counts[sev] += 1
    return counts
