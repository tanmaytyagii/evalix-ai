"""
Top-level launcher.

Usage:
    streamlit run app.py        → opens the dashboard
    python   app.py api         → launches the FastAPI service
    python   app.py demo        → runs an end-to-end demo on sample data
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def _running_under_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


def _run_streamlit_dashboard():
    """Execute the dashboard module in this script's runtime."""
    import runpy
    runpy.run_path(str(ROOT / "frontend" / "dashboard.py"), run_name="__main__")


def _run_api():
    import uvicorn
    from config import settings
    uvicorn.run("api.main:app", host=settings.api_host, port=settings.api_port, reload=True)


def _run_demo():
    """End-to-end smoke test on the bundled sample resumes."""
    from agent import HRScreeningAgent

    agent = HRScreeningAgent()
    jd_path = ROOT / "data" / "sample_jd.txt"
    if not jd_path.exists():
        print("No sample JD found at", jd_path)
        return
    job_id, jd = agent.register_job(jd_path.read_text(encoding="utf-8"))
    print(f"✔ Registered job #{job_id} — {jd.title}")

    samples_dir = ROOT / "data" / "sample_resumes"
    files = sorted(p for p in samples_dir.glob("*.txt"))
    if not files:
        print("No sample resumes found.")
        return

    for f in files:
        out = agent.evaluate_resume(job_id, f.read_bytes(), f.name)
        ev = out.payload["evaluation"]
        print(
            f"  • {out.payload['candidate']['name']:<25}  "
            f"{ev['total_score']:>5.1f}/100  "
            f"({ev['recommendation']:<11}, conf {ev['confidence_score']:.0f}%)"
        )

    ranking = agent.rank_candidates(job_id)
    print("\nLeaderboard:")
    for r in ranking:
        nm = r["payload"]["candidate"]["name"] or r["payload"]["candidate"]["source_filename"]
        print(f"  #{r['rank']:<2} {nm:<25} {r['total_score']:>5.1f}  {r['recommendation']}")


# When loaded via `streamlit run app.py`, this branch fires every rerun.
if _running_under_streamlit():
    _run_streamlit_dashboard()
elif __name__ == "__main__":
    arg = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    if arg == "api":
        _run_api()
    elif arg == "demo":
        _run_demo()
    else:
        print(__doc__)
