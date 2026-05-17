"""
Scoring Rubric — Weights and thresholds for different risk categories.
"""

# Category-specific severity multipliers
# Some categories are weighted more heavily due to their impact
CATEGORY_MULTIPLIERS = {
    "FINANCIAL": 1.2,
    "PRIVACY": 1.1,
    "EMPLOYMENT": 1.0,
    "IP": 1.15,
    "LEGAL": 1.0,
    "COMPLIANCE": 0.9,
}

# Clause type risk baselines
# These represent the inherent risk level of each clause type
CLAUSE_TYPE_BASELINES = {
    "NON_COMPETE": "MEDIUM",
    "NON_DISCLOSURE": "LOW",
    "ARBITRATION": "MEDIUM",
    "IP_ASSIGNMENT": "HIGH",
    "DATA_COLLECTION": "MEDIUM",
    "AUTO_RENEWAL": "MEDIUM",
    "TERMINATION": "LOW",
    "LIABILITY_LIMIT": "MEDIUM",
    "INDEMNIFICATION": "HIGH",
    "GOVERNING_LAW": "LOW",
    "PAYMENT_PENALTY": "MEDIUM",
    "GENERAL": "LOW",
}


def get_category_multiplier(category: str) -> float:
    """Get the scoring multiplier for a risk category."""
    return CATEGORY_MULTIPLIERS.get(category, 1.0)


def get_baseline_risk(clause_type: str) -> str:
    """Get the baseline risk level for a clause type."""
    return CLAUSE_TYPE_BASELINES.get(clause_type, "LOW")
