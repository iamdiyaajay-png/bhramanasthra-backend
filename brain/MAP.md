# Project Architecture & System Map

## 1. System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CLIENT / FRONTEND                               │
│  React 19 / Vite / Tailwind CSS / Lucide / 21st Components / Three.js   │
│                                                                        │
│  [Member 1: UI/UX & Visualization]                                     │
│  ├── Landing & Mission Dashboard                                       │
│  ├── Interactive Earth / Space Visualizer                              │
│  ├── Telemetry Data Tables & Visual Charts                             │
│  └── High-Value Production Pages (404, 500, Skeletons, Team, Tour)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Secure Local Requests (JWT / Auth)
                                    │ ZERO Client Keys Exposed
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    BACKEND API & AUTH LAYER (Node.js / Express)        │
│                                                                        │
│  [Member 2: Backend, Security & API Gateway]                           │
│  ├── /api/auth/*     -> User authentication & session validation       │
│  ├── /api/nasa/*     -> Authenticated NASA API proxy & token broker    │
│  ├── /api/telemetry  -> Data streaming, caching & rate limiting        │
│  └── /api/diagnostics-> NASA API latency, status & uptime health       │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
                    ▼                               ▼
┌──────────────────────────────────┐ ┌───────────────────────────────────┐
│     EXTERNAL NASA SERVICES       │ │     SCIENCE & ML PIPELINE         │
│  • NASA Open APIs (APOD, NeoWs)  │ │  [Member 3: Science & ML Lead]    │
│  • Earthdata / GIBS Satellite    │ │  • Telemetry data processing      │
│  • Planetary Data System (PDS)   │ │  • Headroom context compression   │
│  • Secret Keys safely in .env    │ │  • Anomaly detection models       │
└──────────────────────────────────┘ └───────────────────────────────────┘
```

## 2. 4-Member Team RACI & Skill Roster

| Member | Focus Area | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) | Primary Skills Activated |
|---|---|---|---|---|---|---|
| **Member 1** | Frontend & UI/UX | UI Layout, 3D Canvas, Component Library | Frontend Polish & Mobile Responsiveness | Backend Team on API Contracts | All Members | `taste-skill`, `21st-ui`, `awesome-design-md` |
| **Member 2** | Backend & Security | NASA API Proxy, Backend Auth, Secret Isolation | Zero Exposed Client Keys & API Uptime | Member 3 on Data Schemas | Member 1 & 4 | `security-audit`, `automation-recommender` |
| **Member 3** | Science & ML | NASA Telemetry Parsing, ML Inference, Compaction | Scientific Data Accuracy & Logic | Member 2 on Ingestion Pipelines | Member 1 & 4 | `headroom`, `project-brain` |
| **Member 4** | QA, Docs & Pitch | Playwright E2E Tests, Production Pages, Audit | Hackathon Submission & Demo Flow | All Members on Features | Project Owner | `playwright-cli`, `web-design-guidelines`, `gstack` |

## 3. Directory Layout

```text
nasa/
├── .agents/
│   └── skills/                      # 14 installed skills
├── brain/                           # Persistent project brain
│   ├── PROJECT.md                   # Mission & scope
│   ├── MAP.md                       # System map & RACI roster
│   ├── STATUS.md                    # Master sprint status
│   ├── STATUS_member1_frontend.md   # Member 1 workstream
│   ├── STATUS_member2_backend.md    # Member 2 workstream
│   ├── STATUS_member3_science_ml.md # Member 3 workstream
│   ├── STATUS_member4_qa_docs.md    # Member 4 workstream
│   ├── HANDOFF.md                   # Shift handoff report
│   ├── DECISIONS.md                 # Architectural Decision Records
│   ├── PREVIOUS_PROJECTS_STUDY.md   # Deep analysis of CGPC, GK Quiz, hangout, TechReady
│   └── topics/
│       ├── operations/RUNBOOK.md    # Verified commands & operational procedures
│       └── design/PRODUCTION_PAGES_CHECKLIST.md # High-value production pages guide
├── GEMINI.md                        # Master workspace instructions & cheat sheet rules
└── AGENTS.md                        # Agent behavioral guidelines & security policies
```

