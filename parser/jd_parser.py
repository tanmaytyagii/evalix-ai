"""
Job Description Parser
======================

Hybrid parser:
    1) Heuristic extraction (regex + keyword lists) — always runs, gives
       us a useful baseline even with no API key.
    2) LLM-based structured extraction — overrides / enriches the
       baseline when an OpenAI key is present.

Returns a strongly-typed `JDStructure` dataclass that downstream
modules consume.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from utils.llm_client import chat_json, llm_available
from utils.text_cleaner import clean_text, dedupe_keep_order, split_into_lines


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass
class JDStructure:
    title: str = ""
    company: str = ""
    domain: str = ""
    seniority: str = ""
    location: str = ""
    employment_type: str = ""
    min_experience_years: float = 0.0

    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    tools_technologies: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)

    raw_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def search_corpus(self) -> str:
        """One blob used for embedding similarity vs. resumes."""
        return " | ".join(
            [
                self.title,
                self.domain,
                " ".join(self.required_skills),
                " ".join(self.preferred_skills),
                " ".join(self.tools_technologies),
                " ".join(self.responsibilities),
            ]
        ).strip()


# --------------------------------------------------------------------------- #
# Heuristic helpers
# --------------------------------------------------------------------------- #

_TITLE_RE = re.compile(
    r"(?:job\s*title|position|role)\s*[:\-]\s*(.+)", re.IGNORECASE
)
_COMPANY_RE = re.compile(
    r"(?:company|organisation|organization|firm)\s*[:\-]\s*(.+)", re.IGNORECASE
)
_LOCATION_RE = re.compile(r"(?:location|based\s*in)\s*[:\-]\s*(.+)", re.IGNORECASE)
_EXPERIENCE_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:to\s*\d+\s*)?(?:years?|yrs?)\s*(?:of)?\s*experience",
    re.IGNORECASE,
)
_SECTION_RE = re.compile(
    r"^(required|must[\s-]have|preferred|nice[\s-]to[\s-]have|responsibilities|"
    r"qualifications|skills|tools|technologies|certifications|education)\b[:\-]?",
    re.IGNORECASE | re.MULTILINE,
)


def _section_text(text: str, headings: List[str]) -> str:
    """Pull all lines under any of the given headings until the next heading."""
    lines = text.splitlines()
    out: List[str] = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if capture:
                out.append("")
            continue
        m = _SECTION_RE.match(stripped)
        if m:
            head = m.group(1).lower().replace(" ", "-")
            capture = any(h in head for h in headings)
            continue
        if capture:
            out.append(stripped)
    return "\n".join(out).strip()


def _extract_bullets(block: str) -> List[str]:
    if not block:
        return []
    items: List[str] = []
    for line in split_into_lines(block):
        # split comma-separated lists in a single line
        for part in re.split(r"[,•·;]| and ", line):
            p = part.strip(" -*•·").strip()
            if 2 <= len(p) <= 80:
                items.append(p)
    return dedupe_keep_order(items)


def _heuristic_parse(text: str) -> JDStructure:
    cleaned_oneline = clean_text(text)
    out = JDStructure(raw_text=text)

    if m := _TITLE_RE.search(text):
        out.title = m.group(1).strip().splitlines()[0]
    if m := _COMPANY_RE.search(text):
        out.company = m.group(1).strip().splitlines()[0]
    if m := _LOCATION_RE.search(text):
        out.location = m.group(1).strip().splitlines()[0]
    if m := _EXPERIENCE_RE.search(cleaned_oneline):
        try:
            out.min_experience_years = float(m.group(1))
        except ValueError:
            pass

    out.required_skills = _extract_bullets(
        _section_text(text, ["required", "must-have", "skills", "qualifications"])
    )
    out.preferred_skills = _extract_bullets(
        _section_text(text, ["preferred", "nice-to-have"])
    )
    out.responsibilities = _extract_bullets(_section_text(text, ["responsibilities"]))
    out.tools_technologies = _extract_bullets(
        _section_text(text, ["tools", "technologies"])
    )
    out.certifications = _extract_bullets(_section_text(text, ["certifications"]))
    out.education = _extract_bullets(_section_text(text, ["education"]))

    if not out.title:
        # first non-empty line is often the title
        first = next(iter(split_into_lines(text)), "")
        if 3 <= len(first) <= 100:
            out.title = first
    return out


# --------------------------------------------------------------------------- #
# LLM extraction
# --------------------------------------------------------------------------- #

_LLM_SYSTEM = """You are an expert technical recruiter. Extract a STRICT JSON
representation of the given Job Description. Do not invent skills the JD does
not mention. Use empty arrays / strings when unknown."""

_LLM_USER_TEMPLATE = """Extract the following schema from the JD below.

JSON schema:
{{
  "title": str,
  "company": str,
  "domain": str,                 // e.g. "Backend Engineering", "Data Science"
  "seniority": str,              // "Intern" | "Junior" | "Mid" | "Senior" | "Lead"
  "location": str,
  "employment_type": str,        // "Full-time" | "Internship" | "Contract" | ...
  "min_experience_years": float,
  "required_skills":   [str],
  "preferred_skills":  [str],
  "tools_technologies":[str],
  "certifications":    [str],
  "education":         [str],
  "responsibilities":  [str]
}}

JOB DESCRIPTION:
\"\"\"{jd}\"\"\"

Return JSON only.
"""


def _llm_enrich(text: str, base: JDStructure) -> JDStructure:
    if not llm_available():
        return base

    parsed = chat_json(_LLM_SYSTEM, _LLM_USER_TEMPLATE.format(jd=text[:8000]))
    if not parsed:
        return base

    def _take(field_name: str, fallback):
        val = parsed.get(field_name)
        if isinstance(val, list):
            return dedupe_keep_order([str(x).strip() for x in val if str(x).strip()])
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, (int, float)):
            return val
        return fallback

    base.title = _take("title", base.title)
    base.company = _take("company", base.company)
    base.domain = _take("domain", base.domain)
    base.seniority = _take("seniority", base.seniority)
    base.location = _take("location", base.location)
    base.employment_type = _take("employment_type", base.employment_type)
    try:
        base.min_experience_years = float(_take("min_experience_years", base.min_experience_years) or 0)
    except (TypeError, ValueError):
        pass

    base.required_skills = _take("required_skills", base.required_skills)
    base.preferred_skills = _take("preferred_skills", base.preferred_skills)
    base.tools_technologies = _take("tools_technologies", base.tools_technologies)
    base.certifications = _take("certifications", base.certifications)
    base.education = _take("education", base.education)
    base.responsibilities = _take("responsibilities", base.responsibilities)

    return base


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def parse_jd(text: str, use_llm: Optional[bool] = None) -> JDStructure:
    """Parse a JD into a structured object."""
    text = (text or "").strip()
    base = _heuristic_parse(text)
    if use_llm is None:
        use_llm = llm_available()
    if use_llm:
        base = _llm_enrich(text, base)
    return base
