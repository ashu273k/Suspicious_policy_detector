"""
PDF Exporter — Generate styled PDF reports using ReportLab.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# Color palette
COLORS = {
    "primary": HexColor("#1a1a2e"),
    "accent": HexColor("#4361ee"),
    "critical": HexColor("#ef233c"),
    "high": HexColor("#ff6b35"),
    "medium": HexColor("#f7b32b"),
    "low": HexColor("#2ec4b6"),
    "none": HexColor("#6c757d"),
    "text": HexColor("#212529"),
    "light": HexColor("#f8f9fa"),
}

SEVERITY_COLORS = {
    "CRITICAL": COLORS["critical"],
    "HIGH": COLORS["high"],
    "MEDIUM": COLORS["medium"],
    "LOW": COLORS["low"],
    "NONE": COLORS["none"],
}


def export_pdf(report: dict) -> bytes:
    """
    Generate a styled PDF report from an analysis report dict.

    Returns:
        PDF file as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = _create_styles()
    elements = []

    # ── Title ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("LexGuard", styles["title"]))
    elements.append(Paragraph("Contract Risk Analysis Report", styles["subtitle"]))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", color=COLORS["accent"], thickness=2))
    elements.append(Spacer(1, 20))

    # ── Document Info ─────────────────────────────────────────────────────
    filename = report.get("filename", "Unknown")
    elements.append(Paragraph(f"<b>Document:</b> {filename}", styles["body"]))
    elements.append(Spacer(1, 8))

    # ── Score Summary ─────────────────────────────────────────────────────
    score = report.get("score", {})
    overall_score = score.get("overall_score", 0)
    grade = score.get("grade", "N/A")
    total = report.get("total_clauses", 0)
    flagged = report.get("flagged_clauses", 0)

    score_data = [
        ["Risk Score", "Grade", "Total Clauses", "Flagged"],
        [f"{overall_score}/100", grade, str(total), str(flagged)],
    ]

    score_table = Table(score_data, colWidths=[1.5 * inch] * 4)
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["accent"]),
        ("ROWHEIGHT", (0, 0), (-1, -1), 30),
        ("BACKGROUND", (0, 1), (-1, 1), COLORS["light"]),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 20))

    # ── Executive Summary ─────────────────────────────────────────────────
    summary = report.get("executive_summary", "")
    if summary:
        elements.append(Paragraph("Executive Summary", styles["heading"]))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(summary, styles["body"]))
        elements.append(Spacer(1, 16))

    # ── Severity Breakdown ────────────────────────────────────────────────
    breakdown = score.get("breakdown", {})
    if breakdown:
        elements.append(Paragraph("Severity Breakdown", styles["heading"]))
        elements.append(Spacer(1, 8))

        breakdown_data = [["Severity", "Count"]]
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"]:
            count = breakdown.get(sev, 0)
            if count > 0:
                breakdown_data.append([sev, str(count)])

        if len(breakdown_data) > 1:
            bt = Table(breakdown_data, colWidths=[3 * inch, 2 * inch])
            bt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#dee2e6")),
                ("ROWHEIGHT", (0, 0), (-1, -1), 24),
            ]))
            elements.append(bt)
            elements.append(Spacer(1, 16))

    # ── Flagged Clauses Detail ────────────────────────────────────────────
    clauses = report.get("analyzed_clauses", [])
    flagged_clauses = [c for c in clauses if c.get("max_severity", "NONE") != "NONE"]

    if flagged_clauses:
        elements.append(PageBreak())
        elements.append(Paragraph("Flagged Clauses", styles["heading"]))
        elements.append(Spacer(1, 12))

        for entry in flagged_clauses:
            clause = entry.get("clause", {})
            severity = entry.get("max_severity", "LOW")
            risk = entry.get("risk_analysis", {})

            # Clause header
            clause_type = clause.get("clause_type", "GENERAL")
            elements.append(Paragraph(
                f"<b>Clause {clause.get('clause_id', '?')}: {clause_type}</b> — "
                f"<font color='{SEVERITY_COLORS.get(severity, COLORS['none']).hexval()}'>{severity}</font>",
                styles["clause_heading"],
            ))
            elements.append(Spacer(1, 4))

            # Original text (truncated)
            original = clause.get("original_text", "")[:500]
            elements.append(Paragraph(f"<i>\"{original}\"</i>", styles["quote"]))
            elements.append(Spacer(1, 4))

            # Analysis
            plain = risk.get("plain_english", "")
            if plain:
                elements.append(Paragraph(f"<b>What this means:</b> {plain}", styles["body"]))

            tip = risk.get("negotiation_tip", risk.get("recommendation", ""))
            if tip:
                elements.append(Paragraph(f"<b>Negotiation tip:</b> {tip}", styles["body"]))

            elements.append(Spacer(1, 8))
            elements.append(HRFlowable(width="80%", color=HexColor("#dee2e6"), thickness=0.5))
            elements.append(Spacer(1, 8))

    # Build PDF
    doc.build(elements)
    return buffer.getvalue()


def _create_styles() -> dict:
    """Create custom paragraph styles for the report."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontSize=28,
            textColor=COLORS["primary"],
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontSize=14,
            textColor=COLORS["accent"],
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "heading": ParagraphStyle(
            "CustomHeading",
            parent=base["Heading1"],
            fontSize=16,
            textColor=COLORS["primary"],
            spaceBefore=12,
            spaceAfter=6,
        ),
        "clause_heading": ParagraphStyle(
            "ClauseHeading",
            parent=base["Heading2"],
            fontSize=12,
            textColor=COLORS["text"],
        ),
        "body": ParagraphStyle(
            "CustomBody",
            parent=base["Normal"],
            fontSize=10,
            textColor=COLORS["text"],
            leading=14,
            spaceAfter=6,
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=base["Normal"],
            fontSize=9,
            textColor=HexColor("#495057"),
            leftIndent=20,
            rightIndent=20,
            leading=13,
            spaceAfter=4,
        ),
    }
