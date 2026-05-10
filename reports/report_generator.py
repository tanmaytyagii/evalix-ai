"""
Report Generation
=================

Renders an evaluation payload into:

    - JSON  (machine-readable, complete)
    - HTML  (recruiter-friendly, dark-themed via Jinja template)
    - PDF   (ReportLab — works without WeasyPrint / wkhtmltopdf)

The PDF path uses ReportLab (pure-Python) so the system runs anywhere
without external native dependencies.
"""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import settings


_TEMPLATES_DIR = Path(__file__).parent / "templates"

_jinja = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


# --------------------------------------------------------------------------- #
# Recommendation badge colour map (used by PDF)
# --------------------------------------------------------------------------- #

_BADGE_COLORS = {
    "Strong Hire": "#34d399",
    "Shortlist":   "#6c8cff",
    "Consider":    "#fbbf24",
    "Reject":      "#f87171",
}


class ReportGenerator:
    """Render an evaluation payload into multiple formats."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir or settings.outputs_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # JSON
    # ------------------------------------------------------------------ #

    def render_json(self, payload: Dict[str, Any]) -> str:
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def write_json(self, payload: Dict[str, Any], filename: str) -> Path:
        out = self.output_dir / filename
        out.write_text(self.render_json(payload), encoding="utf-8")
        return out

    # ------------------------------------------------------------------ #
    # HTML
    # ------------------------------------------------------------------ #

    def render_html(self, payload: Dict[str, Any]) -> str:
        tmpl = _jinja.get_template("report.html")
        ctx = dict(payload)
        ctx["generated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        return tmpl.render(**ctx)

    def write_html(self, payload: Dict[str, Any], filename: str) -> Path:
        out = self.output_dir / filename
        out.write_text(self.render_html(payload), encoding="utf-8")
        return out

    # ------------------------------------------------------------------ #
    # PDF (ReportLab)
    # ------------------------------------------------------------------ #

    def render_pdf(self, payload: Dict[str, Any]) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=18 * mm, rightMargin=18 * mm,
            topMargin=18 * mm, bottomMargin=18 * mm,
            title=f"Candidate Report — {payload.get('candidate', {}).get('name', '')}",
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="H1", parent=styles["Title"], fontSize=20,
                                  textColor=colors.HexColor("#0b0f1a"), spaceAfter=4))
        styles.add(ParagraphStyle(name="Meta", parent=styles["Normal"], fontSize=9,
                                  textColor=colors.HexColor("#6b7280"), spaceAfter=10))
        styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], fontSize=11,
                                  textColor=colors.HexColor("#374151"), spaceBefore=14, spaceAfter=6))
        styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontSize=10, leading=14))
        styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontSize=8.5, leading=12,
                                  textColor=colors.HexColor("#4b5563")))

        candidate = payload.get("candidate", {})
        job = payload.get("job", {})
        ev = payload.get("evaluation", {})
        rec = ev.get("recommendation", "—")
        badge_colour = colors.HexColor(_BADGE_COLORS.get(rec, "#6c8cff"))

        story = []

        # Header
        story.append(Paragraph(candidate.get("name") or "Candidate", styles["H1"]))
        meta_bits = []
        if job.get("title"): meta_bits.append(f"Role: <b>{job['title']}</b>")
        if job.get("company"): meta_bits.append(job["company"])
        if candidate.get("experience_years"): meta_bits.append(f"{candidate['experience_years']} yrs")
        story.append(Paragraph(" · ".join(meta_bits) or "—", styles["Meta"]))

        # Headline metrics table
        headline = [
            ["Total Score", "Confidence", "Recommendation"],
            [
                f"{ev.get('total_score', 0):.1f} / 100",
                f"{ev.get('confidence_score', 0):.0f} %",
                rec,
            ],
        ]
        t = Table(headline, colWidths=[55 * mm, 55 * mm, 55 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#374151")),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, 1), 14),
                    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                    ("BACKGROUND", (2, 1), (2, 1), badge_colour),
                    ("TEXTCOLOR", (2, 1), (2, 1), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e5e7eb")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 12))

        # Recruiter summary
        story.append(Paragraph("Recruiter Summary", styles["H2"]))
        story.append(Paragraph(payload.get("recruiter_summary", "—"), styles["Body"]))

        # Rubric breakdown
        story.append(Paragraph("Scoring Rubric", styles["H2"]))
        rubric_rows = [["Dimension", "Weight", "Score", "Weighted", "Why"]]
        for _, dim in ev.get("dimensions", {}).items():
            rubric_rows.append(
                [
                    dim.get("name", ""),
                    f"{dim.get('weight', 0)}%",
                    f"{dim.get('score', 0):.1f}/10",
                    f"{dim.get('weighted', 0):.1f}",
                    Paragraph(dim.get("reason", ""), styles["Small"]),
                ]
            )
        rt = Table(rubric_rows, colWidths=[40 * mm, 18 * mm, 20 * mm, 22 * mm, 70 * mm])
        rt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.whitesmoke, colors.HexColor("#f9fafb")]),
                    ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e5e7eb")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(rt)

        # Missing skills
        missing = ev.get("signals", {}).get("missing_skills", [])
        if missing:
            story.append(Paragraph("Missing / Low-confidence Skills", styles["H2"]))
            story.append(Paragraph(" · ".join(missing), styles["Body"]))

        # Strengths / gaps
        strengths = ev.get("strengths", [])
        gaps = ev.get("gaps", [])
        if strengths or gaps:
            story.append(Paragraph("Strengths & Gaps", styles["H2"]))
            sg = [["Strengths", "Gaps"],
                  [Paragraph("<br/>".join(f"• {s}" for s in strengths) or "—", styles["Small"]),
                   Paragraph("<br/>".join(f"• {g}" for g in gaps) or "—", styles["Small"])]]
            sgt = Table(sg, colWidths=[85 * mm, 85 * mm])
            sgt.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e5e7eb")),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(sgt)

        # Footer
        story.append(Spacer(1, 16))
        story.append(
            Paragraph(
                f"Generated by AI HR Screening Agent — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                styles["Small"],
            )
        )

        doc.build(story)
        return buf.getvalue()

    def write_pdf(self, payload: Dict[str, Any], filename: str) -> Path:
        out = self.output_dir / filename
        out.write_bytes(self.render_pdf(payload))
        return out

    # ------------------------------------------------------------------ #
    # Convenience
    # ------------------------------------------------------------------ #

    def write_all(self, payload: Dict[str, Any], slug: str) -> Dict[str, Path]:
        return {
            "json": self.write_json(payload, f"{slug}.json"),
            "html": self.write_html(payload, f"{slug}.html"),
            "pdf":  self.write_pdf(payload, f"{slug}.pdf"),
        }
