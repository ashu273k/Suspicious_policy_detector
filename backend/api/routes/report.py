"""
Report Route — Retrieve analysis reports and export as PDF.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from api.schemas import AnalysisReport
from reporting.pdf_exporter import export_pdf

router = APIRouter()


@router.get("/report/{report_id}")
async def get_report(report_id: str):
    """Retrieve a cached analysis report by ID."""
    from api.routes.analyze import reports

    # Try direct report ID
    report = reports.get(report_id) or reports.get(f"report_{report_id}")

    # Try by document ID
    if not report:
        report = reports.get(f"doc_{report_id}")

    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")

    return report


@router.get("/report/{report_id}/pdf")
async def download_pdf(report_id: str):
    """Download the analysis report as a styled PDF."""
    from api.routes.analyze import reports

    report = reports.get(report_id) or reports.get(f"report_{report_id}")
    if not report:
        report = reports.get(f"doc_{report_id}")

    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")

    try:
        pdf_bytes = export_pdf(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

    filename = report.get("filename", "report").replace(".pdf", "").replace(".docx", "")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="lexguard_{filename}_report.pdf"'
        },
    )
