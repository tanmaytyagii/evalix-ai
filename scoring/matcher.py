"""
Semantic Matching Engine
========================

Calculates the low-level similarity signals that the rubric layer
turns into the final score:

    - jd_similarity        : full-text JD ↔ resume cosine
    - skills_overlap       : semantic overlap of required skills
    - tools_overlap        : tools / tech stack overlap
    - experience_relevance : how well candidate roles align with JD
    - project_relevance    : how well candidate projects align with JD

Pure NumPy + sentence-transformers, no LLM call required.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from parser.jd_parser import JDStructure
from parser.resume_parser import ResumeStructure
from utils.embeddings import (
    cosine_similarity,
    embed_text,
    find_missing_skills,
    semantic_overlap,
)


@dataclass
class MatchSignals:
    jd_similarity: float = 0.0
    skills_overlap: float = 0.0
    tools_overlap: float = 0.0
    experience_relevance: float = 0.0
    project_relevance: float = 0.0
    education_match: float = 0.0
    certification_match: float = 0.0

    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    matched_preferred: List[str] = field(default_factory=list)
    matched_certifications: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _matched(required: List[str], candidate: List[str], threshold: float = 0.55) -> List[str]:
    """Inverse of `find_missing_skills` — what *did* the candidate match."""
    if not required or not candidate:
        return []
    missing = set(s.lower() for s in find_missing_skills(required, candidate, threshold))
    return [s for s in required if s.lower() not in missing]


def _education_score(jd: JDStructure, resume: ResumeStructure) -> float:
    if not jd.education:
        return 0.7  # neutral when JD is silent
    if not resume.education:
        return 0.0
    jd_blob = " ".join(jd.education)
    res_blob = " ".join(f"{e.degree} {e.institution}" for e in resume.education)
    return max(0.0, cosine_similarity(embed_text(jd_blob), embed_text(res_blob)))


def _certification_score(jd: JDStructure, resume: ResumeStructure) -> tuple[float, List[str]]:
    if not jd.certifications:
        return 0.7, []
    if not resume.certifications:
        return 0.0, []
    matched = _matched(jd.certifications, resume.certifications, threshold=0.5)
    score = len(matched) / max(len(jd.certifications), 1)
    return min(1.0, score + 0.1), matched


def _experience_relevance(jd: JDStructure, resume: ResumeStructure) -> float:
    if not resume.experience:
        return 0.0
    jd_blob = jd.search_corpus()
    if not jd_blob:
        return 0.5
    sims = []
    for exp in resume.experience:
        blob = f"{exp.title} at {exp.company}. {exp.description}"
        sims.append(cosine_similarity(embed_text(jd_blob), embed_text(blob)))
    base = max(0.0, sum(sims) / len(sims))

    # tenure boost when candidate meets JD's required years
    if jd.min_experience_years and resume.total_experience_years:
        ratio = min(resume.total_experience_years / max(jd.min_experience_years, 1e-3), 1.5)
        base = min(1.0, base * (0.7 + 0.3 * ratio))
    return base


def _project_relevance(jd: JDStructure, resume: ResumeStructure) -> float:
    if not resume.projects:
        return 0.0
    jd_blob = jd.search_corpus()
    sims = []
    for proj in resume.projects:
        blob = f"{proj.name}. {proj.description}. tech: {' '.join(proj.technologies)}"
        sims.append(cosine_similarity(embed_text(jd_blob), embed_text(blob)))
    return max(0.0, sum(sims) / len(sims))


# --------------------------------------------------------------------------- #
# Public
# --------------------------------------------------------------------------- #

def compute_match(jd: JDStructure, resume: ResumeStructure) -> MatchSignals:
    """Compute all semantic signals for one (JD, resume) pair."""
    signals = MatchSignals()

    # 1. Full-text JD ↔ resume cosine
    signals.jd_similarity = max(
        0.0,
        cosine_similarity(
            embed_text(jd.search_corpus()),
            embed_text(resume.search_corpus()),
        ),
    )

    # 2. Skills (required + preferred)
    cand_skills_pool = list(set(resume.skills + resume.tools))
    signals.skills_overlap = semantic_overlap(jd.required_skills, cand_skills_pool)
    signals.tools_overlap = semantic_overlap(jd.tools_technologies, cand_skills_pool)
    signals.matched_skills = _matched(jd.required_skills, cand_skills_pool)
    signals.missing_skills = find_missing_skills(jd.required_skills, cand_skills_pool)
    signals.matched_preferred = _matched(jd.preferred_skills, cand_skills_pool)

    # 3. Experience
    signals.experience_relevance = _experience_relevance(jd, resume)

    # 4. Projects
    signals.project_relevance = _project_relevance(jd, resume)

    # 5. Education + certifications
    signals.education_match = _education_score(jd, resume)
    cert_score, cert_matched = _certification_score(jd, resume)
    signals.certification_match = cert_score
    signals.matched_certifications = cert_matched

    return signals
