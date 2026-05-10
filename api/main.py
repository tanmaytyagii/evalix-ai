"""
FastAPI service for the AI HR Screening Agent.

Endpoints:
    GET  /health                          → liveness
    POST /jobs                            → register a JD
    GET  /jobs                            → list jobs
    GET  /jobs/{id}                       → fetch one
    POST /jobs/{id}/evaluate              → upload one or many resumes
    GET  /jobs/{id}/ranking               → leaderboard for a job
    GET  /evaluations/{id}                → fetch full evaluation
    POST /evaluations/{id}/override       → HR override (HITL)
    GET  /evaluations/{id}/report.{fmt}   → download json|html|pdf

Run with:
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

# allow `python api/main.py` style invocation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware                   # noqa: E402
from fastapi.responses import (                                      # noqa: E402
    FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response,
)
from fastapi.staticfiles import StaticFiles                          # noqa: E402
from pydantic import BaseModel, Field                                # noqa: E402

from agent import HRScreeningAgent                                   # noqa: E402
from config import settings                                          # noqa: E402
from database.db import get_db                                       # noqa: E402
from reports.report_generator import ReportGenerator                 # noqa: E402


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "REST API for explainable AI-driven candidate screening. "
        "Parses JDs and resumes, applies bias-mitigation, scores against a "
        "5-dimension rubric, and exports recruiter-ready reports."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = HRScreeningAgent()
reports = ReportGenerator()

# --------------------------------------------------------------------------- #
# Static frontend (Stitch-based SPA in /web)
# --------------------------------------------------------------------------- #
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
if WEB_DIR.exists():
    app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


@app.get("/", include_in_schema=False)
def root():
    """Serve the SPA at the root if the web bundle exists, else redirect to docs."""
    index = WEB_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return RedirectResponse("/docs")


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #

class JobIn(BaseModel):
    text: str = Field(..., description="Raw Job Description text")


class OverrideIn(BaseModel):
    new_score: float
    new_recommendation: str
    reason: str
    hr_user: Optional[str] = "hr@company.com"


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "llm_configured": bool(settings.openai_api_key),
        "embedding_model": settings.embedding_model,
    }


@app.post("/jobs", status_code=201)
def create_job(body: JobIn):
    job_id, jd = agent.register_job(body.text)
    return {"job_id": job_id, "structured": jd.to_dict()}


@app.get("/jobs")
def list_jobs():
    return {"jobs": get_db().list_jobs()}


@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    job = get_db().get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return job


@app.post("/jobs/{job_id}/evaluate")
async def evaluate(
    job_id: int,
    files: List[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(400, "no files uploaded")

    payloads = []
    for f in files:
        data = await f.read()
        try:
            out = agent.evaluate_resume(job_id, data, f.filename or "resume.pdf")
            payloads.append(out.payload)
        except ValueError as e:
            raise HTTPException(400, str(e))
        except Exception as e:
            payloads.append({"error": str(e), "filename": f.filename})

    return {"job_id": job_id, "evaluations": payloads}


@app.get("/jobs/{job_id}/ranking")
def ranking(job_id: int):
    return {"job_id": job_id, "candidates": agent.rank_candidates(job_id)}


@app.get("/evaluations/{evaluation_id}")
def evaluation(evaluation_id: int):
    row = get_db().get_evaluation(evaluation_id)
    if row is None:
        raise HTTPException(404, "evaluation not found")
    return row


@app.post("/evaluations/{evaluation_id}/override")
def override(evaluation_id: int, body: OverrideIn):
    try:
        return agent.override(
            evaluation_id,
            body.new_score,
            body.new_recommendation,
            body.reason,
            body.hr_user or "hr@company.com",
        )
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/evaluations/{evaluation_id}/overrides")
def overrides(evaluation_id: int):
    return {"overrides": get_db().list_overrides(evaluation_id)}


@app.get("/evaluations/{evaluation_id}/report.json")
def report_json(evaluation_id: int):
    row = get_db().get_evaluation(evaluation_id)
    if row is None:
        raise HTTPException(404, "evaluation not found")
    return JSONResponse(row["payload"])


@app.get("/evaluations/{evaluation_id}/report.html", response_class=HTMLResponse)
def report_html(evaluation_id: int):
    row = get_db().get_evaluation(evaluation_id)
    if row is None:
        raise HTTPException(404, "evaluation not found")
    return HTMLResponse(reports.render_html(row["payload"]))


@app.get("/evaluations/{evaluation_id}/report.pdf")
def report_pdf(evaluation_id: int):
    row = get_db().get_evaluation(evaluation_id)
    if row is None:
        raise HTTPException(404, "evaluation not found")
    pdf_bytes = reports.render_pdf(row["payload"])
    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="evaluation-{evaluation_id}.pdf"'},
    )


# --------------------------------------------------------------------------- #
# Entrypoint for `python api/main.py`
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=settings.api_host, port=settings.api_port, reload=True)
