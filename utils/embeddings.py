"""
Embedding utilities backed by sentence-transformers (all-MiniLM-L6-v2).

Provides:
    - Lazy-loaded singleton model
    - Single + batch embedding
    - Cosine similarity helpers
    - Optional in-process cache so repeated JD embeddings are free
"""

from __future__ import annotations

import functools
import hashlib
from typing import List, Sequence, Union

import numpy as np

from config import settings


# --------------------------------------------------------------------------- #
# Model loading
# --------------------------------------------------------------------------- #

@functools.lru_cache(maxsize=1)
def _load_model():
    """
    Lazy-load the embedding model so importing this module is cheap.

    sentence-transformers is heavy (PyTorch); we only pay the cost when
    an embedding is actually requested.
    """
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


# --------------------------------------------------------------------------- #
# Cache
# --------------------------------------------------------------------------- #

_EMBED_CACHE: dict[str, np.ndarray] = {}


def _key(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def embed_text(text: str) -> np.ndarray:
    """Embed a single string. Cached by content hash."""
    text = (text or "").strip()
    if not text:
        return np.zeros(384, dtype=np.float32)

    k = _key(text)
    cached = _EMBED_CACHE.get(k)
    if cached is not None:
        return cached

    model = _load_model()
    vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    _EMBED_CACHE[k] = vec
    return vec


def embed_batch(texts: Sequence[str]) -> np.ndarray:
    """Batch-embed many texts. Returns a (N, D) matrix."""
    if not texts:
        return np.empty((0, 384), dtype=np.float32)

    model = _load_model()
    cleaned = [(t or "").strip() or " " for t in texts]
    return model.encode(
        cleaned, convert_to_numpy=True, normalize_embeddings=True, batch_size=32
    )


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity in [-1, 1] for two vectors (assumed normalised)."""
    if a is None or b is None:
        return 0.0
    a = np.asarray(a).flatten()
    b = np.asarray(b).flatten()
    if not a.size or not b.size:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def semantic_overlap(query_terms: List[str], target_terms: List[str]) -> float:
    """
    Average best-match cosine similarity between two lists of phrases.

    Used for "skills overlap" — instead of strict string matching,
    we let "Postgres" match "PostgreSQL", "ML" match "Machine Learning", etc.
    """
    if not query_terms or not target_terms:
        return 0.0

    q = embed_batch(query_terms)
    t = embed_batch(target_terms)
    # similarity matrix (Q, T)
    sim = q @ t.T
    # for each required term, take the best match in target
    best_per_query = sim.max(axis=1)
    return float(np.clip(best_per_query.mean(), 0.0, 1.0))


def find_missing_skills(
    required: List[str],
    candidate: List[str],
    threshold: float = 0.55,
) -> List[str]:
    """
    Returns required skills not represented (semantically) in candidate skills.
    Threshold is cosine-similarity; tweak per dataset.
    """
    if not required:
        return []
    if not candidate:
        return list(required)

    r = embed_batch(required)
    c = embed_batch(candidate)
    sim = r @ c.T  # (|required|, |candidate|)
    best = sim.max(axis=1)

    return [required[i] for i, score in enumerate(best) if score < threshold]
