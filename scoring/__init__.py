"""Scoring engine — semantic matcher, rubric, explainability."""

from .matcher import compute_match
from .rubric import score_candidate, RubricResult
from .explainability import generate_recruiter_summary

__all__ = ["compute_match", "score_candidate", "RubricResult", "generate_recruiter_summary"]
