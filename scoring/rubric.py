"""
Explainable Scoring Rubric
==========================

Implements the 5-dimension rubric specified in the product brief:

    1. Skills Match              — 30 %
    2. Experience Relevance      — 25 %
    3. Education & Certifications — 15 %
    4. Projects / Portfolio       — 20 %
    5. Communication Quality      — 10 %

Each dimension exposes:
    - score  (0-10)
    - weight (% contribution)
    - weighted (score * weight / 10)
    - reason (one-line justification)
    - missing (list of gaps where applicable)

The rubric is fully deterministic given the matcher signals — the LLM
is only used for free-text recruiter summary, never for the score
itself. This is what makes the system *explainable*: a human can trace
every number back to a concrete signal.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from config import settings
from parser.jd_parser import JDStructure
from parser.resume_parser import ResumeStructure
from scoring.matcher import MatchSignals, compute_match


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass
class RubricDimension:
    name: str
    score: float           # 0-10
    weight: float          # %
    weighted: float        # score * weight / 10  → contributes to /100
    reason: str = ""
    missing: List[str] = field(default_factory=list)
    matched: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RubricResult:
    candidate_name: str
    total_score: float
    recommendation: str
    confidence_score: float
    dimensions: Dict[str, RubricDimension]
    signals: MatchSignals
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_name": self.candidate_name,
            "total_score": round(self.total_score, 2),
            "recommendation": self.recommendation,
            "confidence_score": round(self.confidence_score, 2),
            "dimensions": {k: v.to_dict() for k, v in self.dimensions.items()},
            "signals": self.signals.to_dict(),
            "strengths": self.strengths,
            "gaps": self.gaps,
        }


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _to_score10(x: float) -> float:
    """Map a [0,1] signal to a 0-10 score."""
    return round(max(0.0, min(1.0, x)) * 10, 2)


def _communication_quality(resume: ResumeStructure) -> tuple[float, str]:
    """
    Heuristic for communication quality based on the structure of the
    resume itself. Rewards: clear summary, well-formed projects,
    quantified bullets, appropriate length.
    """
    text = resume.raw_text or ""
    if not text:
        return 0.0, "No resume text available."

    word_count = len(text.split())
    summary_present = bool(resume.summary and len(resume.summary) > 40)
    structured_sections = sum(
        bool(x) for x in [resume.skills, resume.experience, resume.education, resume.projects]
    )
    quantified_bullets = sum(1 for ch in text if ch in "%$") + sum(
        1 for tok in text.split() if any(c.isdigit() for c in tok)
    )

    score = 0.0
    if summary_present:
        score += 2.5
    score += min(structured_sections, 4) * 1.0          # up to 4
    if 250 <= word_count <= 1200:
        score += 1.5
    elif word_count > 80:
        score += 0.7
    score += min(quantified_bullets / 30, 1.0) * 2.0    # up to 2

    score = min(score, 10.0)
    reason = (
        f"{word_count} words, {structured_sections}/4 standard sections, "
        f"{'has' if summary_present else 'no'} summary, "
        f"{'good' if quantified_bullets > 5 else 'few'} quantified bullets."
    )
    return round(score, 2), reason


def _recommendation(total: float) -> str:
    if total >= settings.strong_hire_threshold:
        return "Strong Hire"
    if total >= settings.shortlist_threshold:
        return "Shortlist"
    if total >= settings.consider_threshold:
        return "Consider"
    return "Reject"


def _confidence(signals: MatchSignals, total: float) -> float:
    """
    Confidence = how strong the underlying signals are, regardless of
    the score itself. A high score backed by very few skill matches
    should report low confidence.
    """
    coverage = 0.0
    coverage += min(signals.jd_similarity, 1.0) * 30
    coverage += min(signals.skills_overlap, 1.0) * 30
    coverage += min(signals.experience_relevance, 1.0) * 20
    coverage += min(signals.project_relevance, 1.0) * 10
    coverage += min(signals.education_match, 1.0) * 10
    # Pull confidence toward the actual total to avoid over-confident extremes
    blended = 0.7 * coverage + 0.3 * total
    return round(max(0.0, min(100.0, blended)), 2)


# --------------------------------------------------------------------------- #
# Main scorer
# --------------------------------------------------------------------------- #

def score_candidate(jd: JDStructure, resume: ResumeStructure) -> RubricResult:
    signals = compute_match(jd, resume)
    weights = settings.rubric_weights

    # 1. Skills Match — combines required-skill overlap + preferred bonus
    pref_bonus = 0.05 * min(len(signals.matched_preferred), 5)  # up to +0.25
    skills_signal = min(1.0, signals.skills_overlap + pref_bonus)
    skills_score = _to_score10(skills_signal)
    skills_dim = RubricDimension(
        name="Skills Match",
        score=skills_score,
        weight=weights["skills_match"],
        weighted=round(skills_score * weights["skills_match"] / 10, 2),
        reason=(
            f"{len(signals.matched_skills)}/{max(len(jd.required_skills), 1)} required skills matched"
            + (f", {len(signals.matched_preferred)} preferred bonus." if signals.matched_preferred else ".")
        ),
        missing=signals.missing_skills,
        matched=signals.matched_skills,
    )

    # 2. Experience Relevance
    exp_score = _to_score10(signals.experience_relevance)
    exp_dim = RubricDimension(
        name="Experience Relevance",
        score=exp_score,
        weight=weights["experience_relevance"],
        weighted=round(exp_score * weights["experience_relevance"] / 10, 2),
        reason=(
            f"{resume.total_experience_years:.1f} yrs of experience; "
            f"role-fit signal {signals.experience_relevance:.2f}."
            + (f" (JD asks for {jd.min_experience_years:.0f}+ yrs)" if jd.min_experience_years else "")
        ),
    )

    # 3. Education & Certifications
    edu_blend = 0.6 * signals.education_match + 0.4 * signals.certification_match
    edu_score = _to_score10(edu_blend)
    edu_dim = RubricDimension(
        name="Education & Certifications",
        score=edu_score,
        weight=weights["education_certifications"],
        weighted=round(edu_score * weights["education_certifications"] / 10, 2),
        reason=(
            f"Education fit {signals.education_match:.2f}; "
            f"certifications matched: "
            + (", ".join(signals.matched_certifications) if signals.matched_certifications else "none")
            + "."
        ),
        matched=signals.matched_certifications,
    )

    # 4. Projects / Portfolio
    proj_score = _to_score10(signals.project_relevance)
    proj_dim = RubricDimension(
        name="Projects / Portfolio",
        score=proj_score,
        weight=weights["projects_portfolio"],
        weighted=round(proj_score * weights["projects_portfolio"] / 10, 2),
        reason=(
            f"{len(resume.projects)} project(s); "
            f"portfolio-JD relevance {signals.project_relevance:.2f}."
        ),
    )

    # 5. Communication Quality
    comm_score, comm_reason = _communication_quality(resume)
    comm_dim = RubricDimension(
        name="Communication Quality",
        score=comm_score,
        weight=weights["communication_quality"],
        weighted=round(comm_score * weights["communication_quality"] / 10, 2),
        reason=comm_reason,
    )

    dimensions = {
        "skills_match": skills_dim,
        "experience_relevance": exp_dim,
        "education_certifications": edu_dim,
        "projects_portfolio": proj_dim,
        "communication_quality": comm_dim,
    }

    total = sum(d.weighted for d in dimensions.values())
    total = round(min(100.0, max(0.0, total)), 2)

    # Strengths + gaps narrative
    sorted_dims = sorted(dimensions.values(), key=lambda d: d.score, reverse=True)
    strengths = [
        f"{d.name} ({d.score:.1f}/10)" for d in sorted_dims[:2] if d.score >= 6.5
    ]
    gaps = [
        f"{d.name} ({d.score:.1f}/10)" for d in sorted_dims[-2:] if d.score < 6.0
    ]
    if signals.missing_skills:
        gaps.append("Missing required skills: " + ", ".join(signals.missing_skills[:5]))

    return RubricResult(
        candidate_name=resume.candidate_name or resume.source_filename or "Candidate",
        total_score=total,
        recommendation=_recommendation(total),
        confidence_score=_confidence(signals, total),
        dimensions=dimensions,
        signals=signals,
        strengths=strengths,
        gaps=gaps,
    )
