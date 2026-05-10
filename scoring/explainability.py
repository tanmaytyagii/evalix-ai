"""
Explainability layer
====================

Turns the deterministic rubric output into recruiter-friendly prose.

Two paths:
    - With OpenAI key  → GPT-4o-mini writes a 3-4 sentence summary
                         grounded in the rubric numbers (no hallucinated
                         skills — the prompt forbids it).
    - Without API key  → A polished template-based summary so the demo
                         stays fully offline-capable.
"""

from __future__ import annotations

from typing import Any, Dict

from parser.jd_parser import JDStructure
from parser.resume_parser import ResumeStructure
from scoring.rubric import RubricResult
from utils.llm_client import chat_text, llm_available


_SYSTEM = """You are a senior HR consultant writing a concise, professional
candidate-fit summary. Your tone is balanced, evidence-based, and free of
identity references. Never invent skills, employers, or achievements that
are not present in the rubric below."""

_USER_TEMPLATE = """Write a 3-4 sentence recruiter summary for the candidate
based on this evaluation. Mention strengths first, then 1 concrete gap, and
end with the recommendation. Do NOT use the candidate's name, gender or
demographic info. Do NOT invent skills.

ROLE: {role} ({domain})

RUBRIC (out of 10 each):
- Skills Match            : {skills}/10  — matched: {matched_skills}; missing: {missing_skills}
- Experience Relevance    : {exp}/10
- Education/Certifications: {edu}/10
- Projects / Portfolio    : {proj}/10
- Communication Quality   : {comm}/10

TOTAL: {total}/100  ({rec}, confidence {conf}%)
STRENGTHS: {strengths}
GAPS: {gaps}
"""


def _template_summary(result: RubricResult, jd: JDStructure) -> str:
    rec = result.recommendation
    role = jd.title or "the role"
    top = result.strengths[0] if result.strengths else "core competencies"
    gap = result.gaps[0] if result.gaps else "no major gaps detected"
    matched = ", ".join(result.signals.matched_skills[:4]) or "general competencies"
    missing = result.signals.missing_skills[:3]

    sentence_1 = (
        f"Candidate shows {rec.lower()}-level alignment with {role}, "
        f"scoring {result.total_score:.1f}/100 with strengths in {top}."
    )
    sentence_2 = f"Demonstrated proficiency includes {matched}."
    sentence_3 = (
        f"Notable gap: {gap}."
        if not missing
        else f"Notable gap: missing {', '.join(missing)} from the required stack."
    )
    sentence_4 = (
        f"Recommendation: {rec} (confidence {result.confidence_score:.0f}%)."
    )
    return " ".join([sentence_1, sentence_2, sentence_3, sentence_4])


def generate_recruiter_summary(
    result: RubricResult,
    jd: JDStructure,
    resume: ResumeStructure,
) -> str:
    """Always returns a non-empty string."""
    if llm_available():
        try:
            text = chat_text(
                _SYSTEM,
                _USER_TEMPLATE.format(
                    role=jd.title or "Open role",
                    domain=jd.domain or "—",
                    skills=result.dimensions["skills_match"].score,
                    matched_skills=", ".join(result.signals.matched_skills[:6]) or "—",
                    missing_skills=", ".join(result.signals.missing_skills[:6]) or "—",
                    exp=result.dimensions["experience_relevance"].score,
                    edu=result.dimensions["education_certifications"].score,
                    proj=result.dimensions["projects_portfolio"].score,
                    comm=result.dimensions["communication_quality"].score,
                    total=result.total_score,
                    rec=result.recommendation,
                    conf=result.confidence_score,
                    strengths="; ".join(result.strengths) or "—",
                    gaps="; ".join(result.gaps) or "—",
                ),
                max_tokens=320,
                temperature=0.3,
            )
            if text:
                return text
        except Exception:
            pass
    return _template_summary(result, jd)


def build_evaluation_payload(
    result: RubricResult,
    jd: JDStructure,
    resume: ResumeStructure,
    summary: str,
) -> Dict[str, Any]:
    """The canonical evaluation JSON used by reports + UI + DB."""
    return {
        "candidate": {
            "name": resume.candidate_name,
            "email": resume.email,
            "phone": resume.phone,
            "location": resume.location,
            "source_filename": resume.source_filename,
            "experience_years": resume.total_experience_years,
        },
        "job": {
            "title": jd.title,
            "domain": jd.domain,
            "company": jd.company,
            "min_experience_years": jd.min_experience_years,
        },
        "evaluation": result.to_dict(),
        "recruiter_summary": summary,
    }
