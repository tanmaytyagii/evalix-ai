"""
HR Screening Agent — orchestration layer
========================================

This is the single entry point that the API and the Streamlit UI both
call. It glues together:

    parsers → bias masking → scoring → explainability → persistence → reports

so callers can simply do:

    agent = HRScreeningAgent()
    job_id = agent.register_job(jd_text)
    eval_id, payload = agent.evaluate_resume(job_id, file_bytes, "alice.pdf")

and get back the full evaluation JSON plus a stored DB row.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Optional, Tuple

from config import settings
from database.db import get_db
from parser.jd_parser import JDStructure, parse_jd
from parser.resume_parser import (
    ResumeStructure,
    extract_text,
    parse_resume_text,
)
from reports.report_generator import ReportGenerator
from scoring.explainability import build_evaluation_payload, generate_recruiter_summary
from scoring.rubric import score_candidate
from utils.bias_masking import MaskingReport, mask_pii


@dataclass
class EvaluationOutput:
    evaluation_id: int
    payload: Dict[str, Any]
    masking_report: MaskingReport


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text or "").strip("-").lower()
    return s or "candidate"


class HRScreeningAgent:
    """Façade over parsing, scoring, persistence and reporting."""

    def __init__(self):
        self.db = get_db()
        self.reports = ReportGenerator()

    # ------------------------------------------------------------------ #
    # Job registration
    # ------------------------------------------------------------------ #

    def register_job(self, jd_text: str) -> Tuple[int, JDStructure]:
        jd = parse_jd(jd_text)
        job_id = self.db.insert_job(jd.to_dict())
        self.db.log_event("job.registered", {"job_id": job_id, "title": jd.title})
        return job_id, jd

    def get_job_structure(self, job_id: int) -> Optional[JDStructure]:
        row = self.db.get_job(job_id)
        if not row:
            return None
        import json as _json
        d = _json.loads(row["structured"])
        return JDStructure(**{k: v for k, v in d.items() if k in JDStructure.__dataclass_fields__})

    # ------------------------------------------------------------------ #
    # Resume evaluation
    # ------------------------------------------------------------------ #

    def evaluate_resume(
        self,
        job_id: int,
        file_bytes: bytes,
        filename: str,
    ) -> EvaluationOutput:
        jd = self.get_job_structure(job_id)
        if jd is None:
            raise ValueError(f"Unknown job_id={job_id}")

        # 1. extract raw text
        raw_text = extract_text(file_bytes, filename)

        # 2. parse the resume on the *original* text — names / contact info are
        #    needed by the UI but never reach the scoring LLM
        resume = parse_resume_text(raw_text, filename=filename)

        # 3. bias masking → masked text used for downstream LLM calls
        report: MaskingReport = (
            mask_pii(raw_text, candidate_name=resume.candidate_name)
            if settings.enable_bias_masking
            else MaskingReport(masked_text=raw_text)
        )

        # build a "blinded" copy of the resume for scoring  (raw_text replaced).
        # `replace` preserves nested dataclasses (projects/experience/education).
        blinded = replace(
            resume,
            raw_text=report.masked_text,
            candidate_name="",
            email="",
            phone="",
        )

        # 4. score
        result = score_candidate(jd, blinded)

        # 5. recruiter summary
        summary = generate_recruiter_summary(result, jd, blinded)

        # 6. build canonical payload (uses *original* candidate identity)
        payload = build_evaluation_payload(result, jd, resume, summary)
        payload["bias_masking"] = {
            "enabled": settings.enable_bias_masking,
            "summary": report.summary(),
            "categories_masked": report.masked_categories,
            "items_removed": report.items_removed,
        }

        # 7. persist
        candidate_id = self.db.insert_candidate(resume.to_dict())
        evaluation_id = self.db.insert_evaluation(job_id, candidate_id, payload)
        payload["ids"] = {
            "evaluation_id": evaluation_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
        }
        self.db.log_event(
            "evaluation.completed",
            {"evaluation_id": evaluation_id, "score": result.total_score, "rec": result.recommendation},
        )

        return EvaluationOutput(evaluation_id=evaluation_id, payload=payload, masking_report=report)

    # ------------------------------------------------------------------ #
    # Batch
    # ------------------------------------------------------------------ #

    def evaluate_batch(
        self,
        job_id: int,
        files: List[Tuple[bytes, str]],
    ) -> List[EvaluationOutput]:
        results = []
        for file_bytes, filename in files:
            try:
                results.append(self.evaluate_resume(job_id, file_bytes, filename))
            except Exception as e:
                self.db.log_event(
                    "evaluation.failed",
                    {"job_id": job_id, "filename": filename, "error": str(e)},
                )
        return results

    # ------------------------------------------------------------------ #
    # Ranking
    # ------------------------------------------------------------------ #

    def rank_candidates(self, job_id: int) -> List[Dict[str, Any]]:
        rows = self.db.list_evaluations(job_id=job_id)
        ranked = sorted(rows, key=lambda r: r["total_score"], reverse=True)
        for i, r in enumerate(ranked, start=1):
            r["rank"] = i
        return ranked

    # ------------------------------------------------------------------ #
    # Human-in-the-loop override
    # ------------------------------------------------------------------ #

    def override(
        self,
        evaluation_id: int,
        new_score: float,
        new_recommendation: str,
        reason: str,
        hr_user: str = "hr@company.com",
    ) -> Dict[str, Any]:
        row = self.db.get_evaluation(evaluation_id)
        if row is None:
            raise ValueError(f"Unknown evaluation_id={evaluation_id}")
        old_score = row["total_score"]
        old_rec = row["recommendation"]
        override_id = self.db.insert_override(
            evaluation_id, old_score, new_score, old_rec, new_recommendation, reason, hr_user
        )
        self.db.log_event(
            "evaluation.overridden",
            {"evaluation_id": evaluation_id, "from": old_score, "to": new_score, "by": hr_user},
        )
        return {
            "override_id": override_id,
            "evaluation_id": evaluation_id,
            "old_score": old_score,
            "new_score": new_score,
            "old_recommendation": old_rec,
            "new_recommendation": new_recommendation,
            "reason": reason,
        }

    # ------------------------------------------------------------------ #
    # Reports
    # ------------------------------------------------------------------ #

    def export_reports(self, evaluation_id: int) -> Dict[str, str]:
        row = self.db.get_evaluation(evaluation_id)
        if row is None:
            raise ValueError(f"Unknown evaluation_id={evaluation_id}")
        payload = row["payload"]
        slug = f"eval-{evaluation_id}-{_slugify(payload.get('candidate', {}).get('name', 'candidate'))}"
        paths = self.reports.write_all(payload, slug)
        return {k: str(v) for k, v in paths.items()}
