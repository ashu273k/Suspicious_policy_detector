"""
Report Builder — Assemble final JSON report from analysis results.
Uses Prompt 5 (executive summary narrative) from the LexGuard specification.
"""

import json
from llm.router import call_llm
from ingestion.preprocessor import estimate_token_count


NARRATIVE_PROMPT = """You are a legal advisor writing an accessible risk report for a non-lawyer who is about
to sign the following contract. You have been given a structured risk analysis.

Contract type: {contract_type}
Overall risk score: {score}/100 (Grade: {grade})
Flagged clauses: {flagged_count} out of {total_count} total

Top risks identified:
{top_risks_json}

Write a concise plain-English executive summary (3-4 paragraphs):
1. Overall assessment: is this contract broadly fair, one-sided, or dangerous?
2. The 2-3 most important risks they must understand before signing
3. Key negotiation points or things to ask a lawyer about
4. A final recommendation: sign as-is / negotiate first / seek legal advice / do not sign

Tone: clear, direct, and non-alarmist. Use plain English. Avoid legal jargon.
Do not use bullet points — write in natural prose."""


def build_report(
    document_id: str,
    filename: str,
    analyzed_clauses: list[dict],
    score_result: dict,
    contract_type: str = "General Contract",
) -> dict:
    """
    Build a complete analysis report with executive summary.

    Args:
        document_id: Unique document ID
        filename: Original filename
        analyzed_clauses: List of analyzed clause dicts
        score_result: Dict from score aggregator
        contract_type: Type of contract (e.g., "Employment Agreement")

    Returns:
        Complete report dict ready for API response
    """
    # Generate executive summary narrative
    executive_summary = _generate_narrative(
        contract_type=contract_type,
        score=score_result.get("overall_score", 0),
        grade=score_result.get("grade", "N/A"),
        flagged_count=score_result.get("flagged_clauses", 0),
        total_count=score_result.get("total_clauses", 0),
        top_risks=score_result.get("top_risks", []),
    )

    # Build clause details for the report
    clause_details = []
    for entry in analyzed_clauses:
        clause = entry.get("clause", {})
        agent_results = entry.get("agent_results", [])

        # Pick the best (most severe) analysis result for primary display
        primary_result = _get_primary_result(agent_results)

        clause_details.append({
            "clause": clause,
            "risk_analysis": primary_result,
            "agent_results": agent_results,
            "max_severity": entry.get("max_severity", "NONE"),
        })

    return {
        "report_id": f"report_{document_id}",
        "document_id": document_id,
        "filename": filename,
        "score": {
            "overall_score": score_result.get("overall_score", 0),
            "grade": score_result.get("grade", "N/A"),
            "clause_count": score_result.get("total_clauses", 0),
            "breakdown": score_result.get("breakdown", {}),
        },
        "executive_summary": executive_summary,
        "analyzed_clauses": clause_details,
        "total_clauses": score_result.get("total_clauses", 0),
        "flagged_clauses": score_result.get("flagged_clauses", 0),
        "top_risks": score_result.get("top_risks", []),
        "category_breakdown": score_result.get("category_breakdown", {}),
        "status": "complete",
    }


def _generate_narrative(
    contract_type: str,
    score: int,
    grade: str,
    flagged_count: int,
    total_count: int,
    top_risks: list[dict],
) -> str:
    """Generate the executive summary narrative using LLM."""
    try:
        prompt = NARRATIVE_PROMPT.format(
            contract_type=contract_type,
            score=score,
            grade=grade,
            flagged_count=flagged_count,
            total_count=total_count,
            top_risks_json=json.dumps(top_risks, indent=2),
        )
        return call_llm(prompt, doc_token_count=0)
    except Exception as e:
        # Fallback to a template-based summary
        return _template_summary(score, grade, flagged_count, total_count)


def _template_summary(score: int, grade: str, flagged: int, total: int) -> str:
    """Generate a template-based summary as fallback."""
    if grade in ("A", "B"):
        assessment = "This contract appears to be broadly fair and balanced."
    elif grade == "C":
        assessment = "This contract has some concerning clauses that deserve attention."
    elif grade == "D":
        assessment = "This contract is notably one-sided and contains several risky provisions."
    else:
        assessment = "This contract contains serious red flags that could significantly harm your interests."

    return (
        f"{assessment} Our analysis identified {flagged} potentially concerning clauses "
        f"out of {total} total clauses, resulting in a risk score of {score}/100 (Grade: {grade}). "
        f"We recommend reviewing the flagged clauses carefully before signing."
    )


def _get_primary_result(agent_results: list[dict]) -> dict:
    """Get the most informative agent result."""
    if not agent_results:
        return {}

    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
    return max(
        agent_results,
        key=lambda r: severity_order.get(r.get("severity", "NONE"), 0),
    )
