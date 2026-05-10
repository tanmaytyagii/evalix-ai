"""
Streamlit dashboard for the AI HR Screening Agent.

Pages:
    1. Upload         — paste JD + drop resumes
    2. Processing     — animated progress while pipeline runs
    3. Results        — leaderboard + per-candidate deep dive + override
"""

from __future__ import annotations

import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List

# allow `streamlit run frontend/dashboard.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from agent import HRScreeningAgent  # noqa: E402
from config import settings  # noqa: E402
from frontend.charts import (  # noqa: E402
    confidence_gauge,
    radar_chart,
    ranking_bar_chart,
    rubric_bar_chart,
)
from frontend.styles import get_css, EVALIX_LOGO_SVG, badge_for, bar, metric_card  # noqa: E402
from reports.report_generator import ReportGenerator  # noqa: E402
from utils.llm_client import llm_available  # noqa: E402


# --------------------------------------------------------------------------- #
# Setup
# --------------------------------------------------------------------------- #

st.set_page_config(
    page_title="Evalix AI Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_css(), unsafe_allow_html=True)

# Inject ambient orbs
st.markdown("""
<div class="ambient-orb orb-1"></div>
<div class="ambient-orb orb-2"></div>
<div class="ambient-orb orb-3"></div>
""", unsafe_allow_html=True)

# Top Nav
st.markdown("""
<div class="top-right-nav">
  <div class="nav-bell">🔔</div>
  <div class="nav-avatar">T</div>
</div>
""", unsafe_allow_html=True)


@st.cache_resource
def _get_agent():
    return HRScreeningAgent()


@st.cache_resource
def _get_reports():
    return ReportGenerator()


agent = _get_agent()
reports = _get_reports()


# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #

st.session_state.setdefault("page", "upload")
st.session_state.setdefault("job_id", None)
st.session_state.setdefault("jd_struct", None)
st.session_state.setdefault("evaluations", [])  # list of payloads


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #

with st.sidebar:
    # Sidebar Logo
    st.markdown(
        f"""
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">{EVALIX_LOGO_SVG}</div>
            <div class="sidebar-logo-text">Evalix AI</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("### Navigation")

    if st.button("📥 Upload Resumes", use_container_width=True):
        st.session_state.page = "upload"
    if st.button("📊 Analytics & Results", use_container_width=True,
                 disabled=not st.session_state.evaluations):
        st.session_state.page = "results"

    st.markdown("<br>", unsafe_allow_html=True)

    # Status Section
    st.markdown("### System Status")
    llm_status = "green" if llm_available() else "yellow"
    llm_text = "LLM Active" if llm_available() else "Heuristic Mode"
    
    bias_status = "green" if settings.enable_bias_masking else "yellow"
    bias_text = "Bias Masking On" if settings.enable_bias_masking else "Bias Masking Off"
    
    embedding_model = settings.embedding_model.split('/')[-1][:12] + "..." if len(settings.embedding_model.split('/')[-1]) > 12 else settings.embedding_model.split('/')[-1]
    
    st.markdown(
        f"""
        <div class="sidebar-status-item">
            <div class="status-indicator {llm_status}"></div>
            <span>{llm_text}</span>
        </div>
        <div class="sidebar-status-item">
            <div class="status-indicator blue"></div>
            <span>🧠 {embedding_model}</span>
        </div>
        <div class="sidebar-status-item">
            <div class="status-indicator {bias_status}"></div>
            <span>🛡 {bias_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("Evalix AI • Enterprise Edition")


# --------------------------------------------------------------------------- #
# Hero
# --------------------------------------------------------------------------- #

st.markdown(
    """
<div class="hero">
  <div class="hero-content">
      <h1><span class="gradient-text">Evalix AI</span> Candidate Evaluation</h1>
      <p>Automate resume parsing, perform semantic matching against job requirements, and generate unbiased, rubric-based technical scoring in seconds.</p>
      <div class="hero-badges">
          <span class="hero-badge">⚡️ 10x Faster Screening</span>
          <span class="hero-badge">🛡 Bias Masking Enabled</span>
          <span class="hero-badge">📊 Explainable AI</span>
      </div>
  </div>
  <div class="hero-illustration">
      <div class="illust-bg-glow"></div>
      <div class="illust-resume">
          <div class="illust-header">
              <div class="illust-avatar"></div>
              <div class="illust-lines">
                  <div class="illust-line w-1"></div>
                  <div class="illust-line w-2"></div>
              </div>
          </div>
          <div class="illust-stars">★★★★☆</div>
          <div class="illust-lines mt">
              <div class="illust-line w-3"></div>
              <div class="illust-line w-1"></div>
          </div>
          <div class="illust-badge">
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
          </div>
      </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Page 1 — Upload
# --------------------------------------------------------------------------- #

def _sample_jd() -> str:
    return (
        "Job Title: AI/ML Engineer (Backend-Focused)\n"
        "Company: Northwind AI Labs\n"
        "Location: Bengaluru, India (Hybrid)\n\n"
        "We are looking for a passionate ML engineer with 2+ years of experience "
        "building production-grade ML systems.\n\n"
        "Required Skills:\n"
        "- Python, FastAPI, REST APIs\n"
        "- Machine Learning, Deep Learning, NLP\n"
        "- SQL, PostgreSQL\n"
        "- Docker, AWS\n"
        "- Git, CI/CD\n\n"
        "Preferred Skills:\n"
        "- LLMs, RAG pipelines, vector databases\n"
        "- Kubernetes, Terraform\n\n"
        "Responsibilities:\n"
        "- Design + ship ML APIs to production\n"
        "- Build evaluation harnesses for model quality\n"
        "- Collaborate with data + product teams\n\n"
        "Education: B.Tech / M.Tech in CS / related field"
    )


def render_upload_page():
    col1, col2 = st.columns([1.05, 1])

    with col1:
        st.markdown('<h2 class="section">1 · Job Description</h2>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Paste sample JD", use_container_width=True):
                st.session_state["jd_text"] = _sample_jd()
        with c2:
            if st.button("Clear", use_container_width=True):
                st.session_state["jd_text"] = ""
        jd_text = st.text_area(
            "Paste the JD",
            key="jd_text",
            height=320,
            placeholder="Paste the full job description here…",
        )

    with col2:
        st.markdown('<h2 class="section">2 · Candidate Resumes</h2>', unsafe_allow_html=True)
        files = st.file_uploader(
            "PDF, DOCX or TXT — drop multiple resumes",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )

        st.markdown('<h2 class="section">3 · Run</h2>', unsafe_allow_html=True)
        ready = bool(jd_text and (files or []))
        clicked = st.button(
            "🚀 Analyse candidates",
            type="primary", use_container_width=True, disabled=not ready,
        )
        if not ready:
            st.caption("Upload at least one resume and paste a JD to enable.")

    if clicked:
        run_pipeline(jd_text, files)


def run_pipeline(jd_text: str, files):
    st.session_state.page = "processing"
    st.session_state.evaluations = []

    progress = st.progress(0)
    status = st.empty()

    status.info("Parsing job description …")
    job_id, jd = agent.register_job(jd_text)
    st.session_state.job_id = job_id
    st.session_state.jd_struct = jd.to_dict()
    progress.progress(15)

    n = max(len(files), 1)
    payloads: List[Dict[str, Any]] = []
    for i, f in enumerate(files):
        status.info(f"Evaluating **{f.name}** …")
        try:
            data = f.read()
            out = agent.evaluate_resume(job_id, data, f.name)
            payloads.append(out.payload)
        except Exception as e:
            st.warning(f"Could not parse {f.name}: {e}")
        progress.progress(15 + int(80 * (i + 1) / n))

    status.success("Done — opening results dashboard.")
    progress.progress(100)
    time.sleep(0.6)

    st.session_state.evaluations = payloads
    st.session_state.page = "results"
    st.rerun()


# --------------------------------------------------------------------------- #
# Page 3 — Results
# --------------------------------------------------------------------------- #

def render_results_page():
    if not st.session_state.evaluations:
        st.info("No evaluations yet — head back to the Upload tab.")
        return

    payloads = st.session_state.evaluations
    payloads = sorted(payloads, key=lambda p: p["evaluation"]["total_score"], reverse=True)

    # ---- Top metrics ----
    total = len(payloads)
    strong = sum(1 for p in payloads if p["evaluation"]["recommendation"] == "Strong Hire")
    short = sum(1 for p in payloads if p["evaluation"]["recommendation"] == "Shortlist")
    avg = sum(p["evaluation"]["total_score"] for p in payloads) / max(total, 1)

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(metric_card("Total Candidates", str(total), "Evaluated this batch", "👥"), unsafe_allow_html=True)
    m2.markdown(metric_card("Average Score", f"{avg:.1f}", "Out of 100", "🎯"), unsafe_allow_html=True)
    m3.markdown(metric_card("Strong Hire", str(strong), "Top tier matches", "⭐"), unsafe_allow_html=True)
    m4.markdown(metric_card("Shortlist", str(short), "Qualified candidates", "📝"), unsafe_allow_html=True)

    # ---- Tabs ----
    tab_lead, tab_detail, tab_jd = st.tabs(["🏁 Leaderboard", "🔍 Candidate detail", "📋 JD"])

    with tab_lead:
        st.markdown('<h2 class="section">Ranking</h2>', unsafe_allow_html=True)

        # leaderboard custom HTML table
        table_html = ['<table class="elite-table"><thead><tr>']
        table_html.append('<th>Candidate</th><th>Confidence</th><th>Score</th><th>Recommendation</th><th>Skills</th><th>Exp</th>')
        table_html.append('</tr></thead><tbody>')
        
        for i, p in enumerate(payloads, start=1):
            ev = p["evaluation"]
            name = p["candidate"]["name"] or p["candidate"]["source_filename"]
            initials = name[:2].upper() if name else "??"
            score = round(ev["total_score"], 1)
            conf = f'{ev["confidence_score"]:.0f}%'
            rec = ev["recommendation"]
            match_skills = len(ev["signals"]["matched_skills"])
            miss_skills = len(ev["signals"]["missing_skills"])
            exp = f'{p["candidate"].get("experience_years", 0)} yrs'
            
            table_html.append('<tr>')
            table_html.append(f'<td><div class="candidate-cell"><div class="candidate-avatar">{initials}</div><strong>{name}</strong></div></td>')
            table_html.append(f'<td><span style="color:var(--text-secondary)">{conf}</span></td>')
            table_html.append(f'<td><strong>{score}</strong></td>')
            table_html.append(f'<td>{badge_for(rec)}</td>')
            table_html.append(f'<td><span style="color:var(--success)">{match_skills}</span> / {match_skills + miss_skills}</td>')
            table_html.append(f'<td><span style="color:var(--text-secondary)">{exp}</span></td>')
            table_html.append('</tr>')
            
        table_html.append('</tbody></table>')
        st.markdown("".join(table_html), unsafe_allow_html=True)

        st.markdown('<h2 class="section">Score distribution</h2>', unsafe_allow_html=True)
        # adapt our chart helper to payloads
        adapter = [
            {
                "id": i,
                "total_score": p["evaluation"]["total_score"],
                "recommendation": p["evaluation"]["recommendation"],
                "payload": p,
            }
            for i, p in enumerate(payloads)
        ]
        st.plotly_chart(ranking_bar_chart(adapter), use_container_width=True)

    with tab_detail:
        names = [
            f"{i+1}. {p['candidate']['name'] or p['candidate']['source_filename']}  ·  "
            f"{p['evaluation']['total_score']:.1f}"
            for i, p in enumerate(payloads)
        ]
        idx = st.selectbox("Choose a candidate", range(len(payloads)),
                           format_func=lambda i: names[i])
        render_candidate_detail(payloads[idx])

    with tab_jd:
        render_jd_tab()


def render_candidate_detail(payload: Dict[str, Any]):
    c = payload["candidate"]
    ev = payload["evaluation"]
    rec = ev["recommendation"]

    # Header
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown(f"### {c['name'] or 'Candidate'}")
        meta = []
        if c.get("email"):    meta.append(c["email"])
        if c.get("phone"):    meta.append(c["phone"])
        if c.get("location"): meta.append(c["location"])
        if c.get("experience_years"): meta.append(f"{c['experience_years']} yrs")
        st.caption(" · ".join(meta) or " ")
    with h2:
        st.markdown(badge_for(rec), unsafe_allow_html=True)

    # Top metrics + Circular Progress
    a, b, c_ = st.columns([1, 1, 1.5])
    
    with a:
        from frontend.styles import circular_progress
        st.markdown('<div style="display:flex; justify-content:center; align-items:center; height:100%;" class="metric-card">', unsafe_allow_html=True)
        st.markdown(circular_progress(ev["total_score"]), unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; margin-top:12px; color:var(--text-secondary); font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:0.1em;">Total Score</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    b.markdown(metric_card("AI Confidence", f'{ev["confidence_score"]:.0f}%', "Prediction certainty", "🧠"),
               unsafe_allow_html=True)
    c_.markdown(metric_card("Skill Match",
                            f'{len(ev["signals"]["matched_skills"])}/'
                            f'{len(ev["signals"]["matched_skills"]) + len(ev["signals"]["missing_skills"])}',
                            "Required skills found", "⚡"), unsafe_allow_html=True)

    # Recruiter summary
    st.markdown('<h2 class="section">Recruiter summary</h2>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="summary-card">{payload["recruiter_summary"]}</div>',
        unsafe_allow_html=True,
    )

    # Charts
    st.markdown('<h2 class="section">Rubric breakdown</h2>', unsafe_allow_html=True)
    cc1, cc2 = st.columns([1, 1])
    with cc1:
        st.plotly_chart(rubric_bar_chart(ev["dimensions"]), use_container_width=True)
    with cc2:
        st.plotly_chart(radar_chart(ev["dimensions"]), use_container_width=True)

    st.plotly_chart(confidence_gauge(ev["confidence_score"]), use_container_width=True)

    # Per-dimension cards
    st.markdown('<h2 class="section">Dimension detail</h2>', unsafe_allow_html=True)
    for _, dim in ev["dimensions"].items():
        cls = "match" if dim["score"] >= 7 else ("miss" if dim["score"] < 5 else "")
        chips_match = "".join(f'<span class="chip match">{m}</span>' for m in dim.get("matched", [])[:8])
        chips_miss = "".join(f'<span class="chip miss">missing · {m}</span>' for m in dim.get("missing", [])[:8])
        st.markdown(
            f"""
<div class="metric-card" style="margin-bottom:10px">
  <div style="display:flex; justify-content:space-between;">
    <div><strong>{dim['name']}</strong>
      <span style="color:var(--muted); font-weight:400"> · weight {dim['weight']}%</span>
    </div>
    <div><strong style="color:var(--accent)">{dim['score']:.1f}/10</strong>
      <span style="color:var(--muted)"> → {dim['weighted']:.1f} pts</span>
    </div>
  </div>
  {bar(dim['score'])}
  <div style="color:var(--muted); font-size:13px; margin-top:6px">{dim['reason']}</div>
  <div style="margin-top:8px">{chips_match}{chips_miss}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    # Bias masking transparency
    if payload.get("bias_masking", {}).get("enabled"):
        with st.expander("🛡 Bias masking audit trail"):
            bm = payload["bias_masking"]
            st.write(bm["summary"])
            if bm["items_removed"]:
                st.json(bm["items_removed"])

    # Override + downloads
    with st.expander("✏️  HR override & downloads", expanded=True):
        oc1, oc2 = st.columns([1.4, 1])
        with oc1:
            new_score = st.slider("Override total score",
                                  0.0, 100.0, float(ev["total_score"]), 0.5,
                                  key=f"slider_{payload['ids']['evaluation_id']}")
            new_rec = st.selectbox(
                "Override recommendation",
                ["Strong Hire", "Shortlist", "Consider", "Reject"],
                index=["Strong Hire", "Shortlist", "Consider", "Reject"].index(rec),
                key=f"rec_{payload['ids']['evaluation_id']}",
            )
            reason = st.text_input("Reason (required)",
                                   key=f"reason_{payload['ids']['evaluation_id']}")
            if st.button("Save override", key=f"save_{payload['ids']['evaluation_id']}"):
                if not reason:
                    st.warning("Please provide a reason.")
                else:
                    out = agent.override(
                        payload["ids"]["evaluation_id"],
                        new_score, new_rec, reason,
                    )
                    st.success(f"Override logged · {out['old_score']:.1f} → {out['new_score']:.1f}")
                    # patch in-memory copy so the UI reflects it
                    payload["evaluation"]["total_score"] = new_score
                    payload["evaluation"]["recommendation"] = new_rec

        with oc2:
            st.markdown("**Download report**")
            slug = f"eval-{payload['ids']['evaluation_id']}"
            json_bytes = reports.render_json(payload).encode("utf-8")
            html_bytes = reports.render_html(payload).encode("utf-8")
            pdf_bytes  = reports.render_pdf(payload)

            st.download_button("⬇️  JSON", json_bytes,
                               file_name=f"{slug}.json", mime="application/json",
                               use_container_width=True)
            st.download_button("⬇️  HTML", html_bytes,
                               file_name=f"{slug}.html", mime="text/html",
                               use_container_width=True)
            st.download_button("⬇️  PDF", pdf_bytes,
                               file_name=f"{slug}.pdf", mime="application/pdf",
                               use_container_width=True)


def render_jd_tab():
    jd = st.session_state.jd_struct or {}
    if not jd:
        st.info("No JD parsed yet.")
        return
    cols = st.columns([1, 1, 1])
    cols[0].markdown(metric_card("Role Title", jd.get("title") or "—", jd.get("company") or "Company not specified", "💼"),
                     unsafe_allow_html=True)
    cols[1].markdown(metric_card("Domain & Level", jd.get("domain") or "—", jd.get("seniority") or "Level not specified", "📈"),
                     unsafe_allow_html=True)
    cols[2].markdown(metric_card("Experience Req.",
                                 f'{jd.get("min_experience_years", 0)}+ yrs',
                                 jd.get("location") or "Location not specified", "⏳"),
                     unsafe_allow_html=True)

    def chip_list(label: str, items: List[str]):
        st.markdown(f'<h2 class="section">{label}</h2>', unsafe_allow_html=True)
        if not items:
            st.caption("—")
            return
        st.markdown(
            "".join(f'<span class="chip match">{x}</span>' for x in items),
            unsafe_allow_html=True,
        )

    chip_list("Required skills", jd.get("required_skills", []))
    chip_list("Preferred skills", jd.get("preferred_skills", []))
    chip_list("Tools / Technologies", jd.get("tools_technologies", []))
    chip_list("Certifications", jd.get("certifications", []))
    chip_list("Education", jd.get("education", []))


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #

if st.session_state.page == "upload":
    render_upload_page()
elif st.session_state.page == "results":
    render_results_page()
else:
    render_upload_page()
