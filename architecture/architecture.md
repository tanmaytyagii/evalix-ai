# Architecture

## High-level system

```mermaid
flowchart LR
  subgraph Client
    UI[Streamlit Dashboard]
    HR[HR Reviewer]
  end

  subgraph API[FastAPI Service]
    R1[/POST /jobs/]
    R2[/POST /jobs/:id/evaluate/]
    R3[/GET  /jobs/:id/ranking/]
    R4[/POST /evaluations/:id/override/]
    R5[/GET  /evaluations/:id/report.{pdf,html,json}/]
  end

  subgraph Agent[HR Screening Agent]
    JDP[JD Parser<br/>regex + LLM]
    RP[Resume Parser<br/>pdfplumber / docx / LLM]
    BM[Bias Masking Layer]
    SM[Semantic Matcher<br/>sentence-transformers]
    RB[Explainable Rubric<br/>5 dimensions, deterministic]
    EX[Recruiter Summary<br/>GPT-4o-mini]
  end

  subgraph Storage
    DB[(SQLite<br/>jobs · candidates ·<br/>evaluations · overrides · audit_log)]
    FS[(Reports<br/>JSON / HTML / PDF)]
  end

  HR --> UI
  UI --> API
  API --> Agent
  Agent --> DB
  Agent --> FS
  API --> FS
  RP --> BM --> SM --> RB --> EX
  JDP --> SM
```

## Per-resume processing pipeline

```mermaid
flowchart TD
  A[Resume Upload<br/>PDF / DOCX / TXT] --> B[Text Extraction]
  B --> C[Heuristic Resume Parser]
  C --> D{LLM available?}
  D -- yes --> E[GPT-4o-mini structured extraction]
  D -- no  --> F[Use heuristics only]
  E --> G[Structured Resume]
  F --> G

  G --> H[Bias Masking<br/>name · gender · age · address · photo]
  H --> I[Semantic Matcher<br/>embeddings + cosine similarity]
  I --> J[Explainable Rubric<br/>5 weighted dimensions]
  J --> K[Recruiter Summary<br/>LLM grounded in rubric]
  K --> L[Confidence + Recommendation]
  L --> M[(Persist · SQLite)]
  L --> N[Render Reports<br/>JSON · HTML · PDF]
```

## Scoring rubric

```mermaid
flowchart LR
  S1[Skills Match<br/>30%] --> T[Total /100]
  S2[Experience Relevance<br/>25%] --> T
  S3[Education & Certifications<br/>15%] --> T
  S4[Projects / Portfolio<br/>20%] --> T
  S5[Communication Quality<br/>10%] --> T
  T --> R{Recommendation}
  R -- "≥ 80" --> SH[Strong Hire]
  R -- "65–80" --> SL[Shortlist]
  R -- "50–65" --> CO[Consider]
  R -- "< 50"  --> RJ[Reject]
```

## Human-in-the-loop override flow

```mermaid
sequenceDiagram
  participant H as HR Reviewer
  participant U as Streamlit UI
  participant A as FastAPI
  participant AG as Agent
  participant D as SQLite

  H->>U: Adjust score / change rec
  U->>A: POST /evaluations/{id}/override
  A->>AG: agent.override(...)
  AG->>D: insert into overrides + update evaluations
  D-->>AG: ok
  AG-->>A: { old_score, new_score, ... }
  A-->>U: confirmation
  U-->>H: badge + audit row
```

## Module map

```
ai-hr-agent/
├── parser/        ← JD + resume parsing (regex + LLM)
├── utils/         ← embeddings · text cleaner · bias masking · LLM client
├── scoring/       ← matcher · rubric · explainability
├── reports/       ← JSON / HTML / PDF renderers
├── database/      ← SQLite layer (jobs, candidates, evaluations, overrides)
├── api/           ← FastAPI surface
├── frontend/      ← Streamlit dashboard + Plotly charts + theme
└── agent.py       ← orchestrator façade
```
