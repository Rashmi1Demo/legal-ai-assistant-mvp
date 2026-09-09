from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.units import mm



def generate_case_report_pdf(case_data: dict) -> BytesIO:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = styles["BodyText"]
    body_style.leading = 16

    story = []

    story.append(
        Paragraph(
            "Case Analyst - AI-Powered Legal Case Assessment",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Candidate Assessment Demo",
            styles["Italic"],
        )
    )

    story.append(Spacer(1, 12))

    provider = case_data.get("provider", "Not available")
    model = case_data.get("model", "Not available")

    story.append(
        Paragraph(
            f"<b>AI Provider:</b> {provider}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Model:</b> {model}",
            body_style,
        )
    )

    story.append(Spacer(1, 12))

    report = case_data.get("report", {})

    sections = [
        ("Case Summary", "case_summary"),
        ("Strong Points", "strong_points"),
        ("Weak Points", "weak_points"),
        ("Potential Legal Risks", "potential_legal_risks"),
        (
            "Missing Evidence or Information",
            "missing_evidence_or_information",
        ),
        (
            "Key People, Companies, Organizations, and Dates",
            "key_entities_and_dates",
        ),
        ("Suggested Questions", "suggested_questions"),
        ("Recommended Next Steps", "recommended_next_steps"),
    ]

    for title, key in sections:
        story.append(
            Paragraph(
                title,
                heading_style,
            )
        )

        value = report.get(key, "Not available")

        if isinstance(value, list):
            for item in value:
                story.append(
                    Paragraph(
                        f"• {str(item)}",
                        body_style,
                    )
                )
        else:
            story.append(
                Paragraph(
                    str(value),
                    body_style,
                )
            )

        story.append(Spacer(1, 8))

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Disclaimer",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "This report is an AI-generated first-pass legal assessment "
            "prepared for demonstration purposes. It is intended to assist "
            "legal professionals and does not replace professional legal "
            "judgment or final legal review.",
            body_style,
        )
    )

    doc.build(story)

    buffer.seek(0)
    return buffer

def generate_offline_document_pdf(record):
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("Offline Document Export", styles["Title"])
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            "<b>Status:</b> Extracted - AI Analysis Not Available",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Files:</b> {record.filenames}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph("Extracted Document Content", styles["Heading2"])
    )

    elements.append(Spacer(1, 10))

    # Preserve line breaks and protect special HTML characters
    import html

    safe_text = html.escape(record.extracted_text or "")
    safe_text = safe_text.replace("\n", "<br/>")

    elements.append(
        Paragraph(safe_text, styles["BodyText"])
    )

    doc.build(elements)

    buffer.seek(0)
    return buffer    