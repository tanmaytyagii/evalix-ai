"""
Bias Mitigation Layer
=====================

Removes / masks personally identifying information from a candidate's
text *before* it reaches the LLM scoring stage.

Why:
    Hiring decisions should be evaluated on competencies, not on
    identity proxies (name, gender, age, address, photo). Masking
    these reduces unconscious-bias signals leaking into prompts and
    embeddings.

What gets masked:
    - Person's name (first / last)
    - Gender pronouns and gendered nouns
    - Photographs / image references
    - Postal addresses, ZIP / pincodes
    - Age and date-of-birth references
    - Marital / family / nationality / religion mentions

The original (un-masked) text is preserved separately for HR review,
but only the masked version is sent to the scoring engine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# --------------------------------------------------------------------------- #
# Regex patterns
# --------------------------------------------------------------------------- #

GENDER_TERMS = [
    r"\bhe\b", r"\bshe\b", r"\bhim\b", r"\bher\b", r"\bhis\b", r"\bhers\b",
    r"\bmale\b", r"\bfemale\b", r"\bman\b", r"\bwoman\b", r"\bboy\b", r"\bgirl\b",
    r"\bmr\.?\b", r"\bmrs\.?\b", r"\bms\.?\b", r"\bmiss\b", r"\bsir\b", r"\bmadam\b",
    r"\bgentleman\b", r"\blady\b",
]
GENDER_RE = re.compile("|".join(GENDER_TERMS), flags=re.IGNORECASE)

AGE_RE = re.compile(
    r"\b(?:age[d]?\s*[:\-]?\s*\d{1,2}|\d{1,2}\s*years?\s*old|"
    r"d\.?o\.?b\.?\s*[:\-]?\s*\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|"
    r"date\s*of\s*birth\s*[:\-]?\s*\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b",
    flags=re.IGNORECASE,
)

PHOTO_RE = re.compile(
    r"\b(?:photo(?:graph)?|picture|image|profile\s*pic|headshot|avatar)\b",
    flags=re.IGNORECASE,
)

ADDRESS_RE = re.compile(
    r"\b(?:address|residing\s*at|res\.?\s*addr|location)\s*[:\-]?\s*[^\n]{5,120}",
    flags=re.IGNORECASE,
)
ZIP_RE = re.compile(r"\b\d{5,6}(?:[\s-]\d{4})?\b")

MARITAL_RE = re.compile(
    r"\b(?:marital\s*status|married|unmarried|single|divorced|widowed)\b[^\n]{0,40}",
    flags=re.IGNORECASE,
)

NATIONALITY_RE = re.compile(
    r"\b(?:nationality|religion|caste|community)\s*[:\-]?\s*[^\n]{2,40}",
    flags=re.IGNORECASE,
)

EMAIL_RE = re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}")

NAME_HEADER_RE = re.compile(
    r"^(?:name|candidate\s*name|full\s*name)\s*[:\-]\s*([^\n]+)$",
    flags=re.IGNORECASE | re.MULTILINE,
)


# --------------------------------------------------------------------------- #
# Result container
# --------------------------------------------------------------------------- #

@dataclass
class MaskingReport:
    """Audit trail of what was masked — surfaced in the UI for transparency."""
    masked_text: str
    items_removed: Dict[str, int] = field(default_factory=dict)
    detected_name: Optional[str] = None
    masked_categories: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if not self.items_removed:
            return "No PII detected."
        parts = [f"{k}: {v}" for k, v in self.items_removed.items() if v]
        return "Masked → " + ", ".join(parts)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def mask_pii(text: str, candidate_name: Optional[str] = None) -> MaskingReport:
    """
    Apply bias-mitigation masking to a block of text.

    Args:
        text: Raw resume / profile text.
        candidate_name: Optional, used to additionally mask the candidate's
            name where it appears inline.

    Returns:
        MaskingReport with masked text + audit trail.
    """
    if not text:
        return MaskingReport(masked_text="")

    counts: Dict[str, int] = {}
    masked = text

    # 1. Name header e.g. "Name: John Doe"
    detected_name = candidate_name
    if not detected_name:
        m = NAME_HEADER_RE.search(masked)
        if m:
            detected_name = m.group(1).strip()
    masked, n = NAME_HEADER_RE.subn("Name: [REDACTED]", masked)
    counts["name_headers"] = n

    # 2. Inline candidate name occurrences
    if detected_name:
        for token in re.split(r"\s+", detected_name.strip()):
            if len(token) < 2:
                continue
            pattern = re.compile(rf"\b{re.escape(token)}\b", flags=re.IGNORECASE)
            masked, n = pattern.subn("[REDACTED]", masked)
            counts["name_mentions"] = counts.get("name_mentions", 0) + n

    # 3. Email + phone (PII, not strictly bias — but still removed from LLM input)
    masked, n = EMAIL_RE.subn("[EMAIL]", masked)
    counts["emails"] = n
    masked, n = PHONE_RE.subn("[PHONE]", masked)
    counts["phones"] = n

    # 4. Gendered language
    masked, n = GENDER_RE.subn("[PRONOUN]", masked)
    counts["gender_terms"] = n

    # 5. Age / DOB
    masked, n = AGE_RE.subn("[AGE]", masked)
    counts["age_references"] = n

    # 6. Photo references
    masked, n = PHOTO_RE.subn("[PHOTO]", masked)
    counts["photo_references"] = n

    # 7. Address blocks + ZIP / pincode
    masked, n = ADDRESS_RE.subn("Address: [REDACTED]", masked)
    counts["addresses"] = n
    masked, n = ZIP_RE.subn("[ZIP]", masked)
    counts["zip_codes"] = n

    # 8. Marital / nationality / religion
    masked, n = MARITAL_RE.subn("[REDACTED]", masked)
    counts["marital_status"] = n
    masked, n = NATIONALITY_RE.subn("[REDACTED]", masked)
    counts["nationality_religion"] = n

    categories = [k for k, v in counts.items() if v]
    return MaskingReport(
        masked_text=masked,
        items_removed=counts,
        detected_name=detected_name,
        masked_categories=categories,
    )
