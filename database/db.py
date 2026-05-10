"""
SQLite database layer.

Tables:
    jobs               — JDs uploaded for screening sessions
    candidates         — parsed resumes
    evaluations        — scoring results, indexed by (job, candidate)
    overrides          — human-in-the-loop adjustments (audit trail)
    audit_log          — generic event log

Designed to be easy to swap to Postgres later — no SQLite-specific
extensions, simple schema, JSON blobs for sub-objects.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT,
    company      TEXT,
    domain       TEXT,
    raw_text     TEXT,
    structured   TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT,
    email           TEXT,
    phone           TEXT,
    source_filename TEXT,
    structured      TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              INTEGER NOT NULL,
    candidate_id        INTEGER NOT NULL,
    total_score         REAL NOT NULL,
    recommendation      TEXT NOT NULL,
    confidence_score    REAL NOT NULL,
    payload             TEXT NOT NULL,            -- full evaluation JSON
    recruiter_summary   TEXT,
    created_at          TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE TABLE IF NOT EXISTS overrides (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id     INTEGER NOT NULL,
    old_score         REAL,
    new_score         REAL,
    old_recommendation TEXT,
    new_recommendation TEXT,
    reason            TEXT,
    hr_user           TEXT,
    created_at        TEXT NOT NULL,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,
    payload     TEXT,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_eval_job   ON evaluations(job_id);
CREATE INDEX IF NOT EXISTS ix_eval_cand  ON evaluations(candidate_id);
"""


def _utcnow() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


class Database:
    """Thread-safe SQLite wrapper used by FastAPI + Streamlit."""

    _lock = threading.Lock()

    def __init__(self, path: Optional[str] = None):
        url = path or settings.database_url
        # accept both "sqlite:///..." and plain paths
        if url.startswith("sqlite:///"):
            url = url[len("sqlite:///") :]
        self.path = Path(url)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    # ------------------------------------------------------------------ #
    # internals
    # ------------------------------------------------------------------ #

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            conn = sqlite3.connect(self.path, timeout=10)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()

    def _init_schema(self) -> None:
        with self._conn() as c:
            c.executescript(SCHEMA)

    # ------------------------------------------------------------------ #
    # jobs
    # ------------------------------------------------------------------ #

    def insert_job(self, jd_dict: Dict[str, Any]) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO jobs (title, company, domain, raw_text, structured, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    jd_dict.get("title", ""),
                    jd_dict.get("company", ""),
                    jd_dict.get("domain", ""),
                    jd_dict.get("raw_text", ""),
                    json.dumps(jd_dict),
                    _utcnow(),
                ),
            )
            return cur.lastrowid

    def get_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            row = c.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None

    def list_jobs(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            rows = c.execute("SELECT id, title, company, domain, created_at FROM jobs ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    # candidates
    # ------------------------------------------------------------------ #

    def insert_candidate(self, resume_dict: Dict[str, Any]) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO candidates (name, email, phone, source_filename, structured, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    resume_dict.get("candidate_name", ""),
                    resume_dict.get("email", ""),
                    resume_dict.get("phone", ""),
                    resume_dict.get("source_filename", ""),
                    json.dumps(resume_dict),
                    _utcnow(),
                ),
            )
            return cur.lastrowid

    def get_candidate(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            row = c.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
        return dict(row) if row else None

    # ------------------------------------------------------------------ #
    # evaluations
    # ------------------------------------------------------------------ #

    def insert_evaluation(
        self,
        job_id: int,
        candidate_id: int,
        evaluation_payload: Dict[str, Any],
    ) -> int:
        ev = evaluation_payload.get("evaluation", {})
        with self._conn() as c:
            cur = c.execute(
                """INSERT INTO evaluations
                (job_id, candidate_id, total_score, recommendation,
                 confidence_score, payload, recruiter_summary, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    job_id,
                    candidate_id,
                    float(ev.get("total_score", 0)),
                    ev.get("recommendation", ""),
                    float(ev.get("confidence_score", 0)),
                    json.dumps(evaluation_payload),
                    evaluation_payload.get("recruiter_summary", ""),
                    _utcnow(),
                ),
            )
            return cur.lastrowid

    def get_evaluation(self, evaluation_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            row = c.execute("SELECT * FROM evaluations WHERE id = ?", (evaluation_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["payload"] = json.loads(d["payload"])
        return d

    def list_evaluations(self, job_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self._conn() as c:
            if job_id is not None:
                rows = c.execute(
                    "SELECT * FROM evaluations WHERE job_id = ? ORDER BY total_score DESC",
                    (job_id,),
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT * FROM evaluations ORDER BY total_score DESC"
                ).fetchall()

        out = []
        for r in rows:
            d = dict(r)
            try:
                d["payload"] = json.loads(d["payload"])
            except Exception:
                d["payload"] = {}
            out.append(d)
        return out

    # ------------------------------------------------------------------ #
    # overrides (HITL)
    # ------------------------------------------------------------------ #

    def insert_override(
        self,
        evaluation_id: int,
        old_score: float,
        new_score: float,
        old_recommendation: str,
        new_recommendation: str,
        reason: str,
        hr_user: str = "hr@company.com",
    ) -> int:
        with self._conn() as c:
            cur = c.execute(
                """INSERT INTO overrides
                (evaluation_id, old_score, new_score,
                 old_recommendation, new_recommendation,
                 reason, hr_user, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    evaluation_id,
                    old_score,
                    new_score,
                    old_recommendation,
                    new_recommendation,
                    reason,
                    hr_user,
                    _utcnow(),
                ),
            )
            # update headline numbers on the evaluation row too
            c.execute(
                "UPDATE evaluations SET total_score = ?, recommendation = ? WHERE id = ?",
                (new_score, new_recommendation, evaluation_id),
            )
            return cur.lastrowid

    def list_overrides(self, evaluation_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self._conn() as c:
            if evaluation_id is not None:
                rows = c.execute(
                    "SELECT * FROM overrides WHERE evaluation_id = ? ORDER BY id DESC",
                    (evaluation_id,),
                ).fetchall()
            else:
                rows = c.execute("SELECT * FROM overrides ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    # audit log
    # ------------------------------------------------------------------ #

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO audit_log (event_type, payload, created_at) VALUES (?, ?, ?)",
                (event_type, json.dumps(payload), _utcnow()),
            )


# --------------------------------------------------------------------------- #
# Module-level singleton
# --------------------------------------------------------------------------- #

_db: Optional[Database] = None


def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
