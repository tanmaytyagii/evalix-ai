/* =========================================================
   AI HR Screening Agent — frontend (vanilla JS, no build)
   ========================================================= */

const API = {
  health:    () => `/health`,
  jobs:      () => `/jobs`,
  job:       (id) => `/jobs/${id}`,
  evaluate:  (id) => `/jobs/${id}/evaluate`,
  ranking:   (id) => `/jobs/${id}/ranking`,
  evaluation:(id) => `/evaluations/${id}`,
  override:  (id) => `/evaluations/${id}/override`,
  reportPdf: (id) => `/evaluations/${id}/report.pdf`,
  reportHtml:(id) => `/evaluations/${id}/report.html`,
  reportJson:(id) => `/evaluations/${id}/report.json`,
};

// ------------------------------------------------------------------
// Tiny state
// ------------------------------------------------------------------
const state = {
  jdText: "",
  files: [],                   // File[]
  jobId: null,
  evaluations: [],             // evaluation payloads
  job: null,                   // parsed JD structure
  selectedEvalId: null,
};

const REC_STYLES = {
  "Strong Hire": { bg:"bg-good-soft",  fg:"text-good",  icon:"verified",     dot:"bg-good"  },
  "Shortlist":   { bg:"bg-blue-50",    fg:"text-blue-700", icon:"bookmark",  dot:"bg-blue-600" },
  "Consider":    { bg:"bg-warn-soft",  fg:"text-warn",  icon:"error",        dot:"bg-warn"  },
  "Reject":      { bg:"bg-bad-soft",   fg:"text-bad",   icon:"cancel",       dot:"bg-bad"   },
};

// ------------------------------------------------------------------
// Boot
// ------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
  await checkHealth();
  bindUpload();
  bindResultsTabs();
  bindHeaderCta();
  router();
  window.addEventListener("hashchange", router);
});

// ------------------------------------------------------------------
// Router (hash-based)  #/upload  #/processing  #/results
// ------------------------------------------------------------------
function router() {
  const hash = window.location.hash || "#/upload";
  const route = hash.replace(/^#\//, "").split("/")[0] || "upload";

  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  const target = document.getElementById(`view-${route === "results" ? "results" : route === "processing" ? "processing" : "upload"}`);
  if (target) target.classList.add("active");

  // mark sidebar / nav
  document.querySelectorAll(".nav-link, .side-link").forEach(a => {
    if (a.dataset.route === route) {
      a.classList.add("bg-brand-deep-soft", "text-brand-deep", "font-semibold");
    } else {
      a.classList.remove("bg-brand-deep-soft", "text-brand-deep", "font-semibold");
    }
  });

  // re-render results when navigating in
  if (route === "results" && state.jobId) {
    renderResults();
  } else if (route === "results" && !state.jobId) {
    toast("No screening yet — upload a JD and resumes first.", "warn");
    location.hash = "#/upload";
  }
}

function bindHeaderCta() {
  document.getElementById("header-cta").addEventListener("click", () => {
    location.hash = "#/upload";
  });
}

// ------------------------------------------------------------------
// Health
// ------------------------------------------------------------------
async function checkHealth() {
  try {
    const r = await fetch(API.health());
    const j = await r.json();
    document.getElementById("env-pill-text").textContent = j.llm_configured ? "LLM connected" : "Heuristic mode";
    document.getElementById("env-pill").classList.toggle("bg-warn-soft", !j.llm_configured);
    document.getElementById("env-pill").classList.toggle("text-warn", !j.llm_configured);
    document.getElementById("env-pill").classList.toggle("bg-good-soft", j.llm_configured);
    document.getElementById("env-pill").classList.toggle("text-good", j.llm_configured);
    document.getElementById("llm-status").textContent = j.llm_configured ? "LLM connected" : "Heuristic mode (no API key)";
    document.getElementById("llm-dot").classList.toggle("bg-good", j.llm_configured);
    document.getElementById("llm-dot").classList.toggle("bg-warn", !j.llm_configured);
    document.getElementById("embed-info").textContent = "embedding · " + (j.embedding_model || "").split("/").pop();
  } catch {
    document.getElementById("env-pill-text").textContent = "API offline";
    document.getElementById("env-pill").classList.add("bg-bad-soft", "text-bad");
  }
}

// ------------------------------------------------------------------
// Upload page
// ------------------------------------------------------------------
function bindUpload() {
  const jdEl = document.getElementById("jd-text");
  const fileInput = document.getElementById("file-input");
  const dropzone = document.getElementById("dropzone");
  const btnSample = document.getElementById("btn-sample-jd");
  const btnClear = document.getElementById("btn-clear-jd");
  const btnAnalyse = document.getElementById("btn-analyse");

  jdEl.addEventListener("input", () => { state.jdText = jdEl.value; refreshAnalyseButton(); });
  btnSample.addEventListener("click", () => {
    jdEl.value = SAMPLE_JD; state.jdText = SAMPLE_JD; refreshAnalyseButton();
  });
  btnClear.addEventListener("click", () => {
    jdEl.value = ""; state.jdText = ""; refreshAnalyseButton();
  });

  fileInput.addEventListener("change", (e) => addFiles([...e.target.files]));

  // drag & drop
  ["dragover","dragenter"].forEach(ev => dropzone.addEventListener(ev, (e) => {
    e.preventDefault(); dropzone.classList.add("border-brand-deep","bg-brand-deep-soft");
  }));
  ["dragleave","drop"].forEach(ev => dropzone.addEventListener(ev, (e) => {
    e.preventDefault(); dropzone.classList.remove("border-brand-deep","bg-brand-deep-soft");
  }));
  dropzone.addEventListener("drop", (e) => addFiles([...e.dataTransfer.files]));

  btnAnalyse.addEventListener("click", runAnalysis);
}

function addFiles(list) {
  const allowed = /\.(pdf|docx|txt)$/i;
  for (const f of list) {
    if (!allowed.test(f.name)) { toast(`Unsupported file: ${f.name}`, "warn"); continue; }
    if (state.files.find(x => x.name === f.name && x.size === f.size)) continue;
    state.files.push(f);
  }
  renderFileList();
  refreshAnalyseButton();
}

function removeFile(idx) {
  state.files.splice(idx, 1);
  renderFileList();
  refreshAnalyseButton();
}

function renderFileList() {
  const host = document.getElementById("file-list");
  host.innerHTML = "";
  if (!state.files.length) {
    host.innerHTML = `<div class="flex items-center justify-center p-3 border border-outline-variant border-dotted rounded-lg text-on-surface-variant/60 text-xs">No files selected yet</div>`;
    return;
  }
  state.files.forEach((f, i) => {
    const row = document.createElement("div");
    row.className = "flex items-center justify-between p-3 bg-surface-container-low border border-outline-variant rounded-lg";
    row.innerHTML = `
      <div class="flex items-center gap-3 min-w-0">
        <span class="material-symbols-outlined text-brand-deep">picture_as_pdf</span>
        <span class="text-sm truncate">${f.name}</span>
        <span class="text-[11px] text-on-surface-variant whitespace-nowrap">${(f.size/1024).toFixed(1)} KB</span>
      </div>
      <button class="text-error hover:bg-error-container/40 rounded p-1" title="Remove">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>`;
    row.querySelector("button").addEventListener("click", () => removeFile(i));
    host.appendChild(row);
  });
  document.getElementById("est-time").textContent = `~${Math.max(state.files.length * 5, 5)}s`;
}

function refreshAnalyseButton() {
  const btn = document.getElementById("btn-analyse");
  const help = document.getElementById("analyse-help");
  const ready = !!state.jdText.trim() && state.files.length > 0;
  btn.disabled = !ready;
  if (ready) {
    btn.classList.remove("bg-outline","text-on-surface/40","cursor-not-allowed","opacity-60");
    btn.classList.add("bg-brand-deep","text-white","hover:opacity-90","active:scale-[0.99]");
    help.textContent = "Ready — your screening will start.";
  } else {
    btn.classList.add("bg-outline","text-on-surface/40","cursor-not-allowed","opacity-60");
    btn.classList.remove("bg-brand-deep","text-white","hover:opacity-90","active:scale-[0.99]");
    help.textContent = "Paste a JD and upload at least one resume to enable.";
  }
}

// ------------------------------------------------------------------
// Run analysis (the big one)
// ------------------------------------------------------------------
async function runAnalysis() {
  if (!state.jdText.trim() || !state.files.length) return;

  // jump to processing screen
  location.hash = "#/processing";
  resetSteps();
  setStep(1, "active");
  logProcessing("Parsing job description…");

  try {
    // 1. create the job
    const jobResp = await fetch(API.jobs(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: state.jdText }),
    });
    if (!jobResp.ok) throw new Error("Failed to register JD");
    const jobJson = await jobResp.json();
    state.jobId = jobJson.job_id;
    state.job = jobJson.structured;

    setStep(1, "done");
    setStep(2, "active");
    logProcessing(`Extracting content from ${state.files.length} resume(s)…`);

    // 2. upload + evaluate
    const fd = new FormData();
    state.files.forEach(f => fd.append("files", f));

    setStep(3, "active");
    logProcessing("Applying bias masking layer…");

    const evalResp = await fetch(API.evaluate(state.jobId), { method: "POST", body: fd });
    if (!evalResp.ok) throw new Error("Evaluation request failed");
    const evalJson = await evalResp.json();

    setStep(2, "done"); setStep(3, "done");
    setStep(4, "active");
    logProcessing("Computing rubric + recruiter summary…");

    state.evaluations = (evalJson.evaluations || []).filter(e => e && e.evaluation);
    setStep(4, "done");

    if (!state.evaluations.length) {
      toast("No candidates were successfully evaluated.", "warn");
      location.hash = "#/upload";
      return;
    }

    // small pause so the user actually sees the "done" state
    await sleep(450);
    location.hash = "#/results";
  } catch (e) {
    console.error(e);
    toast(`Analysis failed: ${e.message}`, "bad");
    location.hash = "#/upload";
  }
}

// ------------------------------------------------------------------
// Processing UI
// ------------------------------------------------------------------
function resetSteps() {
  document.querySelectorAll(".step").forEach(s => {
    const dot = s.querySelector(".dot");
    dot.className = "dot w-10 h-10 rounded-full flex items-center justify-center mb-3 transition bg-surface-container text-on-surface-variant border border-outline-variant";
    dot.innerHTML = `<span class="material-symbols-outlined text-[20px]">${stepIcon(s.dataset.step)}</span>`;
    s.querySelector(".label").className = "label text-xs font-semibold text-on-surface-variant";
    s.querySelector(".state").className = "state text-[10px] uppercase tracking-wider mt-1 text-outline";
    s.querySelector(".state").textContent = "pending";
  });
  document.getElementById("stepbar").style.width = "0";
  document.getElementById("processing-log").innerHTML = "";
  document.getElementById("processing-eta").textContent = "working…";
}

function setStep(n, status) {
  const step = document.querySelector(`.step[data-step="${n}"]`);
  if (!step) return;
  const dot = step.querySelector(".dot");
  const label = step.querySelector(".label");
  const state = step.querySelector(".state");
  if (status === "active") {
    dot.className = "dot w-10 h-10 rounded-full flex items-center justify-center mb-3 transition bg-brand-deep text-white ring-4 ring-brand-deep/15";
    dot.innerHTML = `<span class="material-symbols-outlined text-[20px] animate-spin">progress_activity</span>`;
    label.className = "label text-xs font-semibold text-brand-deep";
    state.className = "state text-[10px] uppercase tracking-wider mt-1 text-brand-deep";
    state.textContent = "active";
  } else if (status === "done") {
    dot.className = "dot w-10 h-10 rounded-full flex items-center justify-center mb-3 transition bg-good text-white";
    dot.innerHTML = `<span class="material-symbols-outlined icon-fill text-[20px]">check</span>`;
    label.className = "label text-xs font-semibold text-good";
    state.className = "state text-[10px] uppercase tracking-wider mt-1 text-good";
    state.textContent = "done";
  }
  document.getElementById("stepbar").style.width = `${(n - 1) * 25 + (status === "done" ? 25 : 12.5)}%`;
}

function stepIcon(n) {
  return { "1":"description", "2":"groups", "3":"visibility_off", "4":"rule" }[n] || "circle";
}

function logProcessing(text) {
  const log = document.getElementById("processing-log");
  const row = document.createElement("div");
  row.className = "flex items-start gap-3 fade-in";
  row.innerHTML = `
    <div class="w-8 h-8 rounded bg-surface-container flex-shrink-0 flex items-center justify-center">
      <span class="material-symbols-outlined text-[16px] text-brand-deep">analytics</span>
    </div>
    <div class="flex-grow"><div class="text-sm">${text}</div></div>
    <span class="text-[11px] font-mono text-outline">${new Date().toLocaleTimeString()}</span>`;
  log.appendChild(row);
}

// ------------------------------------------------------------------
// Results page
// ------------------------------------------------------------------
function bindResultsTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.remove("bg-brand-deep","text-white","shadow-sm");
        b.classList.add("text-on-surface-variant");
      });
      btn.classList.add("bg-brand-deep","text-white","shadow-sm");
      btn.classList.remove("text-on-surface-variant");
      const t = btn.dataset.tab;
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.add("hidden"));
      document.getElementById(`tab-${t}`).classList.remove("hidden");
    });
  });
}

function renderResults() {
  if (!state.evaluations.length) return;
  const evals = [...state.evaluations].sort((a,b) => b.evaluation.total_score - a.evaluation.total_score);
  const job = state.job || evals[0].job;

  document.getElementById("results-job-title").textContent = job?.title || "Untitled role";

  // metrics
  const total = evals.length;
  const avg = (evals.reduce((s,e) => s + e.evaluation.total_score, 0) / total).toFixed(1);
  const strong = evals.filter(e => e.evaluation.recommendation === "Strong Hire").length;
  const shortlist = evals.filter(e => e.evaluation.recommendation === "Shortlist").length;
  const metricsStrip = document.getElementById("metrics-strip");
  metricsStrip.innerHTML = [
    metricCard("Total candidates", total, "Evaluated this batch", "groups"),
    metricCard("Average score", `${avg}<span class='text-on-surface-variant text-base'>/100</span>`, "Across this batch", "analytics"),
    metricCard("Strong Hire", strong, "Score ≥ 80", "verified"),
    metricCard("Shortlist", shortlist, "Score 65 – 80", "bookmark"),
  ].join("");

  // leaderboard
  document.getElementById("leaderboard-count").textContent = `${total} candidate${total > 1 ? "s" : ""}`;
  const tbody = document.getElementById("leaderboard-body");
  tbody.innerHTML = "";
  evals.forEach((e, i) => {
    const ev = e.evaluation;
    const rec = REC_STYLES[ev.recommendation] || REC_STYLES["Shortlist"];
    const rank = String(i + 1).padStart(2, "0");
    const row = document.createElement("tr");
    row.className = "hover:bg-surface-container-low transition-colors cursor-pointer";
    row.innerHTML = `
      <td class="px-6 py-4 font-geist font-bold ${i===0?'text-brand-deep':'text-on-surface-variant'}">${rank}</td>
      <td class="px-6 py-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-brand-deep-soft text-brand-deep flex items-center justify-center font-bold text-sm">${initials(e.candidate.name)}</div>
          <div>
            <div class="text-sm font-semibold text-brand-deep">${escapeHtml(e.candidate.name || e.candidate.source_filename || "Candidate")}</div>
            <div class="text-xs text-on-surface-variant">${escapeHtml(e.candidate.location || e.candidate.email || "—")}</div>
          </div>
        </div>
      </td>
      <td class="px-6 py-4 font-geist font-bold">${ev.total_score.toFixed(1)}<span class="text-on-surface-variant text-[11px] font-normal">/100</span></td>
      <td class="px-6 py-4">
        <div class="flex items-center gap-2">
          <div class="flex-1 h-1.5 bg-surface-container rounded-full overflow-hidden w-20">
            <div class="bg-brand-deep h-full" style="width:${Math.round(ev.confidence_score)}%"></div>
          </div>
          <span class="text-xs text-on-surface-variant">${Math.round(ev.confidence_score)}%</span>
        </div>
      </td>
      <td class="px-6 py-4">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full ${rec.bg} ${rec.fg} text-[11px] font-bold uppercase tracking-tight">
          <span class="material-symbols-outlined icon-fill text-[14px]">${rec.icon}</span> ${ev.recommendation}
        </span>
      </td>`;
    row.addEventListener("click", () => openCandidate(e.ids.evaluation_id));
    tbody.appendChild(row);
  });

  // distribution bars
  const maxScore = Math.max(100, ...evals.map(e => e.evaluation.total_score));
  document.getElementById("score-bars").innerHTML = evals.map(e => {
    const h = Math.max(8, (e.evaluation.total_score / maxScore) * 100);
    const rec = REC_STYLES[e.evaluation.recommendation] || REC_STYLES["Shortlist"];
    return `<div class="flex-1 flex flex-col items-center gap-2">
      <div class="w-full ${rec.dot.replace('bg-','bg-')} rounded-t-lg transition-all" style="height:${h}%"></div>
      <span class="text-[10px] text-on-surface-variant truncate w-full text-center">${escapeHtml(shortName(e.candidate.name))}</span>
    </div>`;
  }).join("");

  // highlights
  const top = evals[0];
  const lo  = evals[evals.length - 1];
  document.getElementById("highlights").innerHTML = `
    <div class="p-3 bg-surface-container-low rounded-lg border-l-4 border-brand-deep">
      <p class="text-sm">Top candidate <strong>${escapeHtml(top.candidate.name || "—")}</strong> scored <strong>${top.evaluation.total_score.toFixed(1)}</strong> with ${Math.round(top.evaluation.confidence_score)}% confidence.</p>
    </div>
    <div class="p-3 bg-surface-container-low rounded-lg border-l-4 border-secondary">
      <p class="text-sm">${evals.length} candidate${evals.length>1?'s':''} screened · ${strong} strong hire · ${shortlist} shortlist · ${evals.filter(e=>e.evaluation.recommendation==='Reject').length} reject.</p>
    </div>`;

  // JD tab
  renderJdTab(job);

  // candidate tab — auto-open top by default
  if (!state.selectedEvalId) openCandidate(top.ids.evaluation_id, /*switchTab=*/false);
  else openCandidate(state.selectedEvalId, /*switchTab=*/false);
}

function metricCard(label, value, sub, icon) {
  return `<div class="bg-surface-container-lowest border border-outline-variant p-card-padding rounded-xl">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs text-on-surface-variant uppercase tracking-wider font-semibold">${label}</span>
      <span class="material-symbols-outlined text-brand-deep">${icon}</span>
    </div>
    <div class="text-[28px] font-geist font-bold leading-none">${value}</div>
    <div class="text-xs text-on-surface-variant mt-2">${sub}</div>
  </div>`;
}

// ------------------------------------------------------------------
// Candidate detail
// ------------------------------------------------------------------
function openCandidate(evalId, switchTab = true) {
  const ev = state.evaluations.find(e => e.ids.evaluation_id === evalId);
  if (!ev) return;
  state.selectedEvalId = evalId;
  if (switchTab) document.querySelector('.tab-btn[data-tab="candidate"]').click();
  renderCandidate(ev);
}

function renderCandidate(payload) {
  document.getElementById("candidate-empty").classList.add("hidden");
  const host = document.getElementById("candidate-content");
  host.classList.remove("hidden");
  host.innerHTML = "";

  const c = payload.candidate;
  const ev = payload.evaluation;
  const rec = REC_STYLES[ev.recommendation] || REC_STYLES["Shortlist"];

  // header
  const others = state.evaluations
    .filter(e => e.ids.evaluation_id !== payload.ids.evaluation_id)
    .map(e => `<option value="${e.ids.evaluation_id}">${escapeHtml(e.candidate.name || e.candidate.source_filename)}</option>`).join("");

  host.innerHTML = `
    <section class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8 fade-in">
      <div class="flex items-start gap-4">
        <div class="w-16 h-16 rounded-xl bg-brand-deep-soft text-brand-deep flex items-center justify-center text-xl font-bold border border-outline-variant">${initials(c.name)}</div>
        <div>
          <div class="flex items-center gap-3 mb-1">
            <h2 class="font-geist text-[32px] font-semibold tracking-tight">${escapeHtml(c.name || "Candidate")}</h2>
            <select id="candidate-switch" class="bg-surface-container border border-outline-variant rounded-lg text-sm px-3 py-1.5">
              <option value="${payload.ids.evaluation_id}" selected>${escapeHtml(c.name || "—")}</option>
              ${others}
            </select>
          </div>
          <div class="flex flex-wrap gap-x-4 gap-y-1 text-on-surface-variant text-sm">
            ${c.location ? `<span class="flex items-center gap-1"><span class="material-symbols-outlined text-[18px]">location_on</span> ${escapeHtml(c.location)}</span>` : ""}
            ${c.experience_years ? `<span class="flex items-center gap-1"><span class="material-symbols-outlined text-[18px]">calendar_today</span> ${c.experience_years} yrs</span>` : ""}
            ${c.email ? `<span class="flex items-center gap-1"><span class="material-symbols-outlined text-[18px]">mail</span> ${escapeHtml(c.email)}</span>` : ""}
          </div>
        </div>
      </div>
      <div class="flex gap-2">
        <button data-action="dl-pdf"  class="bg-surface border border-outline-variant text-on-surface px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-surface-container-low"><span class="material-symbols-outlined text-[18px]">picture_as_pdf</span> PDF</button>
        <button data-action="dl-html" class="bg-surface border border-outline-variant text-on-surface px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-surface-container-low"><span class="material-symbols-outlined text-[18px]">code</span> HTML</button>
        <button data-action="dl-json" class="bg-surface border border-outline-variant text-on-surface px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-surface-container-low"><span class="material-symbols-outlined text-[18px]">data_object</span> JSON</button>
      </div>
    </section>

    <!-- top metrics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-gutter mb-8">
      <div class="bg-white border border-outline-variant p-card-padding rounded-xl flex flex-col justify-between">
        <span class="text-xs text-on-surface-variant uppercase tracking-wider font-semibold mb-2">Recommendation</span>
        <div class="flex items-center gap-2 ${rec.fg}">
          <span class="material-symbols-outlined icon-fill text-[32px]">${rec.icon}</span>
          <span class="font-geist text-xl font-semibold">${ev.recommendation}</span>
        </div>
        <div class="mt-3 ${rec.bg} ${rec.fg} px-2 py-1 rounded text-xs w-fit flex items-center gap-1 font-semibold">
          <span class="material-symbols-outlined text-[14px]">trending_up</span> ${ev.total_score.toFixed(1)}/100
        </div>
      </div>
      ${dimMetric("Skills", ev.dimensions.skills_match)}
      ${dimMetric("Experience", ev.dimensions.experience_relevance)}
      ${dimMetric("Projects", ev.dimensions.projects_portfolio)}
    </div>

    <!-- recruiter summary + confidence gauge -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-gutter mb-8">
      <div class="lg:col-span-2 bg-brand-deep-soft border border-brand-deep/20 p-card-padding rounded-xl relative overflow-hidden">
        <div class="absolute top-0 right-0 p-4 opacity-10"><span class="material-symbols-outlined text-[120px] text-brand-deep">psychology_alt</span></div>
        <h3 class="font-geist text-base font-semibold text-brand-deep flex items-center gap-2 mb-3">
          <span class="material-symbols-outlined icon-fill">auto_awesome</span> AI Recruiter Summary
        </h3>
        <p class="text-base leading-relaxed text-on-surface max-w-2xl">${escapeHtml(payload.recruiter_summary || "—")}</p>
        ${(ev.strengths||[]).length ? `<div class="mt-5 flex flex-wrap gap-2">${ev.strengths.map(s=>`<span class="bg-white/80 border border-brand-deep/10 px-3 py-1 rounded-lg text-xs font-medium text-brand-deep">${escapeHtml(s)}</span>`).join("")}</div>` : ""}
      </div>
      <div class="bg-white border border-outline-variant p-card-padding rounded-xl flex flex-col items-center justify-center text-center">
        <h4 class="text-xs uppercase tracking-wider text-on-surface-variant font-semibold mb-4">Confidence</h4>
        ${gaugeSvg(ev.confidence_score)}
        <p class="text-xs text-on-surface-variant mt-3">Signal strength across all rubric dimensions.</p>
      </div>
    </div>

    <!-- charts row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-gutter mb-8">
      <div class="bg-white border border-outline-variant p-card-padding rounded-xl">
        <div class="flex justify-between items-center mb-5">
          <h4 class="font-geist text-base font-semibold">Dimension Contributions</h4>
          <span class="material-symbols-outlined text-on-surface-variant">bar_chart</span>
        </div>
        <div class="space-y-4">
          ${Object.values(ev.dimensions).map(d => `
            <div>
              <div class="flex justify-between text-sm mb-1">
                <span>${escapeHtml(d.name)} <span class="text-on-surface-variant">· ${d.weight}%</span></span>
                <span class="font-semibold">${d.weighted.toFixed(1)} <span class="text-on-surface-variant text-xs">/ ${d.weight}</span></span>
              </div>
              <div class="h-3 w-full bg-surface-container rounded-sm overflow-hidden">
                <div class="h-full bg-brand-deep" style="width:${(d.weighted / d.weight * 100).toFixed(0)}%"></div>
              </div>
            </div>`).join("")}
        </div>
      </div>
      <div class="bg-white border border-outline-variant p-card-padding rounded-xl">
        <div class="flex justify-between items-center mb-5">
          <h4 class="font-geist text-base font-semibold">5-Dimension Radar</h4>
          <span class="material-symbols-outlined text-on-surface-variant">monitoring</span>
        </div>
        <div class="flex justify-center items-center h-56">${radarSvg(ev.dimensions)}</div>
      </div>
    </div>

    <!-- per-dimension cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-gutter mb-8">
      ${Object.values(ev.dimensions).map(d => dimCard(d)).join("")}
    </div>

    <!-- bias masking + override -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-gutter mb-8">
      ${biasCard(payload.bias_masking)}
      ${overrideCard(payload)}
    </div>
  `;

  // wire dropdown
  host.querySelector("#candidate-switch").addEventListener("change", (e) => openCandidate(parseInt(e.target.value), false));

  // wire downloads
  host.querySelector('[data-action="dl-pdf"]').addEventListener("click", () => downloadReport(payload.ids.evaluation_id, "pdf"));
  host.querySelector('[data-action="dl-html"]').addEventListener("click", () => downloadReport(payload.ids.evaluation_id, "html"));
  host.querySelector('[data-action="dl-json"]').addEventListener("click", () => downloadReport(payload.ids.evaluation_id, "json"));

  // wire override
  const slider = host.querySelector("#ovr-score");
  if (slider) {
    slider.addEventListener("input", e => host.querySelector("#ovr-score-val").textContent = e.target.value);
    host.querySelector("#ovr-save").addEventListener("click", () => saveOverride(payload.ids.evaluation_id));
  }
}

function dimMetric(label, d) {
  if (!d) return "";
  return `<div class="bg-white border border-outline-variant p-card-padding rounded-xl">
    <span class="text-xs text-on-surface-variant uppercase tracking-wider font-semibold block mb-2">${label}</span>
    <div class="flex items-end gap-2">
      <span class="font-geist text-[36px] font-bold leading-none">${d.score.toFixed(1)}</span>
      <span class="text-sm text-on-surface-variant mb-1">/ 10</span>
    </div>
    <div class="w-full bg-surface-container h-1.5 rounded-full mt-3"><div class="bg-brand-deep h-1.5 rounded-full" style="width:${(d.score*10).toFixed(0)}%"></div></div>
  </div>`;
}

function dimCard(d) {
  const matched = (d.matched || []).slice(0, 8).map(m => `<span class="px-2 py-1 rounded-full bg-good-soft text-good text-xs font-medium">${escapeHtml(m)}</span>`).join("");
  const missing = (d.missing || []).slice(0, 8).map(m => `<span class="px-2 py-1 rounded-full bg-bad-soft text-bad text-xs font-medium">missing · ${escapeHtml(m)}</span>`).join("");
  return `<div class="bg-white border border-outline-variant p-card-padding rounded-xl">
    <div class="flex justify-between items-start mb-2">
      <div>
        <h5 class="font-geist text-base font-semibold">${escapeHtml(d.name)}</h5>
        <span class="text-xs text-on-surface-variant">weight ${d.weight}%</span>
      </div>
      <div class="text-right">
        <div class="font-geist text-lg font-bold text-brand-deep">${d.score.toFixed(1)}<span class="text-on-surface-variant text-xs font-normal">/10</span></div>
        <div class="text-xs text-on-surface-variant">→ ${d.weighted.toFixed(1)} pts</div>
      </div>
    </div>
    <div class="h-2 w-full bg-surface-container rounded-full overflow-hidden"><div class="h-full bg-brand-deep" style="width:${(d.score*10).toFixed(0)}%"></div></div>
    <p class="text-sm text-on-surface-variant mt-3">${escapeHtml(d.reason || "")}</p>
    ${(matched||missing) ? `<div class="mt-3 flex flex-wrap gap-1.5">${matched}${missing}</div>` : ""}
  </div>`;
}

function biasCard(bm) {
  if (!bm) return "";
  const items = Object.entries(bm.items_removed || {}).filter(([_,v]) => v > 0);
  return `<details class="bg-white border border-outline-variant p-card-padding rounded-xl" ${items.length ? "" : ""}>
    <summary class="cursor-pointer flex items-center gap-2 font-geist font-semibold">
      <span class="material-symbols-outlined text-brand-deep">shield</span> Bias masking audit trail
      <span class="ml-auto text-xs text-on-surface-variant">${bm.enabled ? "enabled" : "disabled"}</span>
    </summary>
    <p class="text-sm text-on-surface-variant mt-3">${escapeHtml(bm.summary || "—")}</p>
    ${items.length ? `<div class="grid grid-cols-2 gap-2 mt-4">
      ${items.map(([k,v]) => `<div class="bg-surface-container-low rounded-lg p-2 text-sm"><span class="font-semibold">${v}</span> · <span class="text-on-surface-variant">${k.replace(/_/g, ' ')}</span></div>`).join("")}
    </div>` : `<p class="text-xs text-on-surface-variant mt-3">No PII items detected to mask.</p>`}
  </details>`;
}

function overrideCard(payload) {
  const ev = payload.evaluation;
  return `<details class="bg-white border border-outline-variant p-card-padding rounded-xl" open>
    <summary class="cursor-pointer flex items-center gap-2 font-geist font-semibold">
      <span class="material-symbols-outlined text-brand-deep">edit</span> HR override
    </summary>
    <div class="mt-4 space-y-4">
      <div>
        <label class="text-xs text-on-surface-variant uppercase tracking-wider font-semibold">New score</label>
        <div class="flex items-center gap-3 mt-1">
          <input id="ovr-score" type="range" min="0" max="100" value="${ev.total_score.toFixed(0)}" step="1" class="flex-grow accent-brand-deep">
          <span id="ovr-score-val" class="font-geist text-lg font-bold w-12 text-right">${ev.total_score.toFixed(0)}</span>
        </div>
      </div>
      <div>
        <label class="text-xs text-on-surface-variant uppercase tracking-wider font-semibold">New recommendation</label>
        <select id="ovr-rec" class="w-full mt-1 bg-surface-container border border-outline-variant rounded-lg text-sm px-3 py-2">
          ${["Strong Hire","Shortlist","Consider","Reject"].map(r => `<option ${r===ev.recommendation?"selected":""}>${r}</option>`).join("")}
        </select>
      </div>
      <div>
        <label class="text-xs text-on-surface-variant uppercase tracking-wider font-semibold">Reason</label>
        <textarea id="ovr-reason" rows="2" placeholder="Required — why are you overriding?" class="w-full mt-1 bg-surface-container border border-outline-variant rounded-lg text-sm p-3"></textarea>
      </div>
      <button id="ovr-save" class="bg-brand-deep text-white px-5 py-2 rounded-lg text-sm font-semibold hover:opacity-90 active:scale-[0.99]">Save override</button>
    </div>
  </details>`;
}

async function saveOverride(evalId) {
  const score = parseFloat(document.getElementById("ovr-score").value);
  const rec = document.getElementById("ovr-rec").value;
  const reason = document.getElementById("ovr-reason").value.trim();
  if (!reason) { toast("Please provide a reason.", "warn"); return; }

  try {
    const r = await fetch(API.override(evalId), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_score: score, new_recommendation: rec, reason }),
    });
    if (!r.ok) throw new Error(await r.text());
    toast("Override saved.", "good");

    // patch in-memory
    const ev = state.evaluations.find(e => e.ids.evaluation_id === evalId);
    if (ev) {
      ev.evaluation.total_score = score;
      ev.evaluation.recommendation = rec;
    }
    renderResults();
  } catch (e) {
    toast(`Override failed: ${e.message}`, "bad");
  }
}

async function downloadReport(evalId, fmt) {
  const url = fmt === "pdf" ? API.reportPdf(evalId) : fmt === "html" ? API.reportHtml(evalId) : API.reportJson(evalId);
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error("download failed");
    const blob = await r.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `evaluation-${evalId}.${fmt}`;
    document.body.appendChild(a); a.click(); a.remove();
    toast(`${fmt.toUpperCase()} report downloaded.`, "good");
  } catch (e) {
    toast(`Could not download ${fmt}: ${e.message}`, "bad");
  }
}

// ------------------------------------------------------------------
// JD tab
// ------------------------------------------------------------------
function renderJdTab(job) {
  if (!job) return;
  const chip = (txt, cls = "") => `<span class="px-3 py-1 rounded-full bg-surface-container text-on-surface text-xs font-medium border border-outline-variant ${cls}">${escapeHtml(txt)}</span>`;
  const group = (label, items, cls = "") => items?.length
    ? `<div class="mb-6">
        <h4 class="text-xs uppercase tracking-wider text-on-surface-variant font-semibold mb-3">${label}</h4>
        <div class="flex flex-wrap gap-2">${items.map(x => chip(x, cls)).join("")}</div>
      </div>` : "";

  document.getElementById("jd-content").innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-3 gap-gutter mb-8">
      ${metricCard("Title", escapeHtml(job.title || "—"), escapeHtml(job.company || "—"), "work")}
      ${metricCard("Domain", escapeHtml(job.domain || "—"), escapeHtml(job.seniority || ""), "category")}
      ${metricCard("Min experience", `${job.min_experience_years || 0} yrs`, escapeHtml(job.location || ""), "calendar_today")}
    </div>
    ${group("Required skills", job.required_skills, "bg-good-soft text-good border-good/30")}
    ${group("Preferred skills", job.preferred_skills)}
    ${group("Tools / Technologies", job.tools_technologies)}
    ${group("Certifications", job.certifications)}
    ${group("Education", job.education)}
    ${job.responsibilities?.length ? `<div class="mt-8">
       <h4 class="text-xs uppercase tracking-wider text-on-surface-variant font-semibold mb-3">Responsibilities</h4>
       <ul class="list-disc pl-5 text-sm space-y-1">${job.responsibilities.map(r => `<li>${escapeHtml(r)}</li>`).join("")}</ul>
    </div>` : ""}
  `;
}

// ------------------------------------------------------------------
// Charts (CSS / SVG, no library)
// ------------------------------------------------------------------
function gaugeSvg(value) {
  // semicircle from -π to 0
  const v = Math.max(0, Math.min(100, value));
  const angle = -Math.PI + (v / 100) * Math.PI;
  const cx = 80, cy = 80, r = 64;
  const x = cx + r * Math.cos(angle);
  const y = cy + r * Math.sin(angle);
  // arc path
  const largeArc = v > 50 ? 1 : 0;
  return `<svg viewBox="0 0 160 100" class="w-44 h-28">
    <path d="M 16 80 A 64 64 0 0 1 144 80" stroke="#e5eeff" stroke-width="14" fill="none" stroke-linecap="round"/>
    <path d="M 16 80 A 64 64 0 ${largeArc} 1 ${x} ${y}" stroke="#0f0069" stroke-width="14" fill="none" stroke-linecap="round"/>
    <text x="80" y="78" text-anchor="middle" font-size="28" font-family="Geist,Inter,sans-serif" font-weight="700" fill="#0b1c30">${v.toFixed(0)}<tspan font-size="12" fill="#777683">%</tspan></text>
  </svg>`;
}

function radarSvg(dims) {
  const arr = Object.values(dims);
  const n = arr.length;
  const cx = 110, cy = 110, R = 90;
  const pts = arr.map((d, i) => {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    const r = (d.score / 10) * R;
    return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
  });
  const ringPts = (rad) => arr.map((_, i) => {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    return `${cx + rad * Math.cos(angle)},${cy + rad * Math.sin(angle)}`;
  }).join(" ");
  const labels = arr.map((d, i) => {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    const lx = cx + (R + 18) * Math.cos(angle);
    const ly = cy + (R + 18) * Math.sin(angle);
    return `<text x="${lx}" y="${ly}" text-anchor="middle" dy="4" font-size="9" fill="#474551">${escapeHtml(d.name.split(" ")[0])}</text>`;
  }).join("");

  return `<svg viewBox="0 0 220 220" class="w-56 h-56">
    ${[0.25, 0.5, 0.75, 1].map(f => `<polygon points="${ringPts(R*f)}" fill="none" stroke="#dce9ff" stroke-width="1"/>`).join("")}
    <polygon points="${pts.map(p => p.join(",")).join(" ")}" fill="rgba(15,0,105,0.18)" stroke="#0f0069" stroke-width="2"/>
    ${pts.map(([x,y]) => `<circle cx="${x}" cy="${y}" r="3" fill="#0f0069"/>`).join("")}
    ${labels}
  </svg>`;
}

// ------------------------------------------------------------------
// Toast
// ------------------------------------------------------------------
function toast(msg, kind = "info") {
  const host = document.getElementById("toast-host");
  const colours = {
    good: "bg-good-soft text-good border-good/30",
    warn: "bg-warn-soft text-warn border-warn/30",
    bad:  "bg-bad-soft text-bad border-bad/30",
    info: "bg-surface-container text-on-surface border-outline-variant",
  };
  const t = document.createElement("div");
  t.className = `border ${colours[kind]} px-4 py-2 rounded-lg shadow-sm text-sm fade-in min-w-[260px]`;
  t.textContent = msg;
  host.appendChild(t);
  setTimeout(() => { t.style.opacity = "0"; t.style.transition = "opacity 200ms"; }, 3000);
  setTimeout(() => t.remove(), 3300);
}

// ------------------------------------------------------------------
// Helpers
// ------------------------------------------------------------------
function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function initials(name) {
  if (!name) return "—";
  const parts = name.trim().split(/\s+/);
  return (parts[0][0] + (parts[1]?.[0] || "")).toUpperCase();
}
function shortName(name) {
  if (!name) return "—";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0];
  return `${parts[0][0]}. ${parts[parts.length-1]}`;
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ------------------------------------------------------------------
// Sample JD
// ------------------------------------------------------------------
const SAMPLE_JD = `Job Title: AI/ML Engineer (Backend-Focused)
Company: Northwind AI Labs
Location: Bengaluru, India (Hybrid)
Employment Type: Full-time

About the role
We are looking for a passionate ML engineer with 2+ years of experience building production-grade
ML systems. You will own the full lifecycle of model deployment — from training pipelines to
serving APIs that power our enterprise customers.

Required Skills:
- Python, FastAPI, REST APIs
- Machine Learning, Deep Learning, NLP
- SQL, PostgreSQL
- Docker, AWS
- Git, CI/CD

Preferred Skills:
- LLMs, RAG pipelines, vector databases (FAISS / Chroma / Pinecone)
- Kubernetes, Terraform
- Streamlit / front-end prototyping

Responsibilities:
- Design + ship ML APIs to production
- Build evaluation harnesses for model quality
- Collaborate with data + product teams
- Mentor junior engineers

Education: B.Tech / M.Tech in CS / related field

Certifications (nice-to-have): AWS ML Specialty, GCP ML Engineer
`;
