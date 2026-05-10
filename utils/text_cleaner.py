"""
Text cleaning utilities used across resume + JD parsers.

Keeps the rest of the pipeline free of regex noise and ensures
embeddings + LLM calls receive normalised input.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, List

# Common section headers that should never become "skills"
NOISE_TOKENS = {
    "summary", "objective", "experience", "education", "projects",
    "certifications", "skills", "interests", "hobbies", "references",
    "contact", "profile", "about",
}

# Regex helpers
_WHITESPACE_RE = re.compile(r"\s+")
_BULLET_RE = re.compile(r"^[\s•·▪◦●○■□–—\-\*]+", re.MULTILINE)
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9-.]+")
_PHONE_RE = re.compile(
    r"(\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}"
)


def normalise_unicode(text: str) -> str:
    """Convert smart quotes / accented chars to ASCII-friendly form."""
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text)


def collapse_whitespace(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text or "").strip()


def strip_bullets(text: str) -> str:
    return _BULLET_RE.sub("", text or "")


def clean_text(text: str) -> str:
    """One-shot cleaner used by parsers."""
    text = normalise_unicode(text)
    text = strip_bullets(text)
    text = collapse_whitespace(text)
    return text


def split_into_lines(text: str) -> List[str]:
    """Split text into trimmed non-empty lines."""
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def extract_emails(text: str) -> List[str]:
    return list({m.group(0) for m in _EMAIL_RE.finditer(text or "")})


def extract_phone_numbers(text: str) -> List[str]:
    return list({m.group(0).strip() for m in _PHONE_RE.finditer(text or "")})


def extract_urls(text: str) -> List[str]:
    return list({m.group(0) for m in _URL_RE.finditer(text or "")})


def dedupe_keep_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for it in items:
        key = (it or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(it.strip())
    return out


def is_noise_token(token: str) -> bool:
    return (token or "").strip().lower() in NOISE_TOKENS
