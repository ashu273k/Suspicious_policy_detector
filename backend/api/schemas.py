"""
LexGuard API — Pydantic schemas for request/response models.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class RiskCategory(str, Enum):
    FINANCIAL = "FINANCIAL"
    PRIVACY = "PRIVACY"
    EMPLOYMENT = "EMPLOYMENT"
    IP = "IP"
    LEGAL = "LEGAL"
    COMPLIANCE = "COMPLIANCE"


class ContractGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


# ── Request Schemas ──────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    document_id: str = Field(..., description="ID of the uploaded document")


class CompareRequest(BaseModel):
    document_id_1: str = Field(..., description="First document ID")
    document_id_2: str = Field(..., description="Second document ID")


# ── Response Schemas ─────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    char_count: int
    status: str = "uploaded"


class ClauseInfo(BaseModel):
    clause_id: int
    original_text: str
    clause_type: str
    parties_affected: str
    summary: str


class RiskAnalysis(BaseModel):
    severity: str
    risk_category: str = ""
    risk_summary: str = ""
    plain_english: str = ""
    real_world_impact: str = ""
    red_flags: list[str] = []
    is_standard: bool = True
    negotiation_tip: str = ""


class PrivacyAnalysis(BaseModel):
    severity: str
    data_types_at_risk: list[str] = []
    consent_issues: bool = False
    data_sharing: bool = False
    retention_problem: bool = False
    right_to_delete: bool = False
    plain_english: str = ""
    recommendation: str = ""


class IPAnalysis(BaseModel):
    severity: str
    transfers_ip: bool = False
    scope: str = ""
    pre_existing_work_at_risk: bool = False
    moral_rights_waived: bool = False
    perpetual_license: bool = False
    plain_english: str = ""
    red_flags: list[str] = []
    recommendation: str = ""


class AnalyzedClause(BaseModel):
    clause: ClauseInfo
    risk_analysis: Optional[RiskAnalysis] = None
    privacy_analysis: Optional[PrivacyAnalysis] = None
    ip_analysis: Optional[IPAnalysis] = None
    agent_results: list[dict] = []


class SeverityBreakdown(BaseModel):
    CRITICAL: int = 0
    HIGH: int = 0
    MEDIUM: int = 0
    LOW: int = 0
    NONE: int = 0


class ScoreResult(BaseModel):
    overall_score: int
    grade: str
    clause_count: int
    breakdown: SeverityBreakdown


class AnalysisReport(BaseModel):
    report_id: str
    document_id: str
    filename: str
    score: ScoreResult
    executive_summary: str = ""
    analyzed_clauses: list[AnalyzedClause] = []
    total_clauses: int = 0
    flagged_clauses: int = 0
    status: str = "complete"


class CompareReport(BaseModel):
    report_id: str
    document_1: AnalysisReport
    document_2: AnalysisReport
    comparison_summary: str = ""
