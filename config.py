"""
Centralised configuration for the AI HR Screening Agent.

Reads environment variables (with sensible defaults) so every module
shares the same source of truth.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent


def _get_bool(key: str, default: bool) -> bool:
    return str(os.getenv(key, str(default))).strip().lower() in {"1", "true", "yes", "y"}


def _get_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


def _get_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


@dataclass
class Settings:
    # --- App ---
    app_name: str = os.getenv("APP_NAME", "AI HR Screening Agent")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = _get_bool("DEBUG", True)

    # --- OpenAI ---
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_temperature: float = _get_float("OPENAI_TEMPERATURE", 0.1)

    # --- Embeddings ---
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    # --- API ---
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = _get_int("API_PORT", 8000)
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    # --- Storage ---
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/hr_agent.db")
    resumes_dir: Path = PROJECT_ROOT / os.getenv("RESUMES_DIR", "resumes").lstrip("./")
    outputs_dir: Path = PROJECT_ROOT / os.getenv("OUTPUTS_DIR", "outputs").lstrip("./")
    data_dir: Path = PROJECT_ROOT / "data"

    # --- Bias mitigation ---
    enable_bias_masking: bool = _get_bool("ENABLE_BIAS_MASKING", True)

    # --- Scoring rubric weights (must sum to 100) ---
    rubric_weights: dict = field(
        default_factory=lambda: {
            "skills_match": 30,
            "experience_relevance": 25,
            "education_certifications": 15,
            "projects_portfolio": 20,
            "communication_quality": 10,
        }
    )

    # --- Recommendation thresholds ---
    shortlist_threshold: int = _get_int("SHORTLIST_THRESHOLD", 65)
    strong_hire_threshold: int = _get_int("STRONG_HIRE_THRESHOLD", 80)
    consider_threshold: int = 50

    # --- Allowed file types ---
    allowed_resume_extensions: List[str] = field(
        default_factory=lambda: [".pdf", ".docx", ".txt"]
    )

    def ensure_dirs(self) -> None:
        for p in (self.resumes_dir, self.outputs_dir, self.data_dir):
            Path(p).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
