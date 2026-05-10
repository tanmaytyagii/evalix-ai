"""
Thin wrapper around the OpenAI client that the rest of the codebase
calls into. Centralising this means:

    - one place to swap providers (Anthropic, Azure OpenAI, local)
    - consistent JSON parsing + retries
    - graceful fallback when no API key is present, so the demo still
      works in offline / sandbox mode
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from config import settings


# --------------------------------------------------------------------------- #
# OpenAI client (lazy)
# --------------------------------------------------------------------------- #

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not settings.openai_api_key:
        return None
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=settings.openai_api_key)
        return _client
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.S)
_JSON_INLINE_RE = re.compile(r"(\{.*\}|\[.*\])", re.S)


def _safe_json(text: str) -> Optional[Any]:
    """Best-effort JSON extraction from a model reply."""
    if not text:
        return None
    # strip code fences
    m = _JSON_BLOCK_RE.search(text)
    if m:
        text = m.group(1)
    else:
        m = _JSON_INLINE_RE.search(text)
        if m:
            text = m.group(1)
    try:
        return json.loads(text)
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def chat_json(
    system_prompt: str,
    user_prompt: str,
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: int = 1500,
) -> Dict[str, Any]:
    """
    Call the LLM and return parsed JSON.

    Returns `{}` on any failure — callers should treat empty dict
    as "no LLM signal", not as an error.
    """
    client = _get_client()
    if client is None:
        return {}

    try:
        resp = client.chat.completions.create(
            model=model or settings.openai_model,
            temperature=temperature if temperature is not None else settings.openai_temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = resp.choices[0].message.content or ""
        parsed = _safe_json(content)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def chat_text(
    system_prompt: str,
    user_prompt: str,
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: int = 600,
) -> str:
    """Plain-text completion. Returns empty string on failure."""
    client = _get_client()
    if client is None:
        return ""
    try:
        resp = client.chat.completions.create(
            model=model or settings.openai_model,
            temperature=temperature if temperature is not None else settings.openai_temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return ""


def llm_available() -> bool:
    return _get_client() is not None
