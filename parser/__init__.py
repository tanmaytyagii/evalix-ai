"""Parsers for Job Descriptions and resumes (PDF / DOCX)."""

from .jd_parser import parse_jd, JDStructure
from .resume_parser import parse_resume, ResumeStructure

__all__ = ["parse_jd", "JDStructure", "parse_resume", "ResumeStructure"]
