"""
Clause Types — Enum for all recognized contract clause categories.
"""

from enum import Enum


class ClauseType(str, Enum):
    NON_COMPETE = "NON_COMPETE"
    NON_DISCLOSURE = "NON_DISCLOSURE"
    ARBITRATION = "ARBITRATION"
    IP_ASSIGNMENT = "IP_ASSIGNMENT"
    DATA_COLLECTION = "DATA_COLLECTION"
    AUTO_RENEWAL = "AUTO_RENEWAL"
    TERMINATION = "TERMINATION"
    LIABILITY_LIMIT = "LIABILITY_LIMIT"
    INDEMNIFICATION = "INDEMNIFICATION"
    GOVERNING_LAW = "GOVERNING_LAW"
    PAYMENT_PENALTY = "PAYMENT_PENALTY"
    GENERAL = "GENERAL"

    @classmethod
    def from_string(cls, value: str) -> "ClauseType":
        """Parse a clause type string, defaulting to GENERAL if unknown."""
        try:
            return cls(value.upper().strip())
        except (ValueError, KeyError):
            return cls.GENERAL
