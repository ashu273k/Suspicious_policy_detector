"""
Compare Route — Compare two contracts side by side.
"""

from fastapi import APIRouter, HTTPException
from api.schemas import CompareRequest
from api.routes.analyze import reports as analyze_reports

router = APIRouter()


@router.post("/compare")
async def compare_contracts(request: CompareRequest):
    """
    Compare risk profiles of two previously analyzed contracts.
    Both contracts must have been analyzed first.
    """
    # Get reports for both documents
    report_1 = (
        analyze_reports.get(f"doc_{request.document_id_1}")
        or analyze_reports.get(f"report_{request.document_id_1}")
    )
    report_2 = (
        analyze_reports.get(f"doc_{request.document_id_2}")
        or analyze_reports.get(f"report_{request.document_id_2}")
    )

    if not report_1:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for document '{request.document_id_1}'. Analyze it first.",
        )
    if not report_2:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for document '{request.document_id_2}'. Analyze it first.",
        )

    # Build comparison
    score_1 = report_1.get("score", {})
    score_2 = report_2.get("score", {})

    comparison = {
        "document_1": {
            "filename": report_1.get("filename"),
            "score": score_1.get("overall_score", 0),
            "grade": score_1.get("grade", "N/A"),
            "flagged": report_1.get("flagged_clauses", 0),
            "total": report_1.get("total_clauses", 0),
        },
        "document_2": {
            "filename": report_2.get("filename"),
            "score": score_2.get("overall_score", 0),
            "grade": score_2.get("grade", "N/A"),
            "flagged": report_2.get("flagged_clauses", 0),
            "total": report_2.get("total_clauses", 0),
        },
        "score_difference": abs(
            score_1.get("overall_score", 0) - score_2.get("overall_score", 0)
        ),
        "safer_document": (
            report_1.get("filename")
            if score_1.get("overall_score", 0) <= score_2.get("overall_score", 0)
            else report_2.get("filename")
        ),
        "summary": _generate_comparison_summary(report_1, report_2),
    }

    return comparison


def _generate_comparison_summary(report_1: dict, report_2: dict) -> str:
    """Generate a plain-English comparison summary."""
    s1 = report_1.get("score", {}).get("overall_score", 0)
    s2 = report_2.get("score", {}).get("overall_score", 0)
    f1 = report_1.get("filename", "Document 1")
    f2 = report_2.get("filename", "Document 2")

    diff = abs(s1 - s2)

    if diff < 5:
        return f"Both contracts have similar risk levels. '{f1}' scored {s1}/100 and '{f2}' scored {s2}/100."
    elif s1 < s2:
        return f"'{f1}' is the safer contract (score: {s1}/100) compared to '{f2}' (score: {s2}/100), with a {diff}-point difference."
    else:
        return f"'{f2}' is the safer contract (score: {s2}/100) compared to '{f1}' (score: {s1}/100), with a {diff}-point difference."
