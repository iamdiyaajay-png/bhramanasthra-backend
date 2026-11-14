---
name: project-brain
description: Persistent project context, memory, multi-workstream tracking, and session handoffs adapted for Gemini 3.8 Flash High. Use to manage the 4-member NASA hackathon project state, load project context, execute shift handoffs, and analyze architectural patterns across previous and upcoming projects.
---

# Project Brain for Gemini 3.8 Flash (High)

Adapted project memory and multi-workstream orchestration system for NASA Hackathon projects.

## Core Structure (`brain/`)

A standardized, token-efficient folder structure that preserves complete project context across AI turns, sessions, and team members:

```text
brain/
├── PROJECT.md                   # Problem statement, scope, target users, non-goals
├── MAP.md                       # Architecture map, repository layout, tech stack, team roster
├── STATUS.md                    # Master milestone tracking, active sprint goals, blockers
├── STATUS_member1_frontend.md   # Member 1 workstream (UI/UX, 3D, components, design taste)
├── STATUS_member2_backend.md    # Member 2 workstream (NASA APIs, server, auth, secure routes)
├── STATUS_member3_science_ml.md # Member 3 workstream (Datasets, ML models, science logic)
├── STATUS_member4_qa_docs.md    # Member 4 workstream (QA, production pages, pitch deck, audit)
├── HANDOFF.md                   # Shift handoff report for the next session/member
├── DECISIONS.md                 # Architectural Decision Records (ADRs) and rationale
├── PREVIOUS_PROJECTS_STUDY.md   # Deep architectural analysis of CGPC, GK Quiz, hangout, TechReady
└── topics/
    ├── operations/RUNBOOK.md    # Verified commands, dev server, build, lint, audit steps
    └── design/PRODUCTION_PAGES_CHECKLIST.md # Checklist of high-value pages often forgotten
```

## 4-Member NASA Hackathon Multi-Workstream Protocol

In this 4-member team, each member owns an independent, coordinated workstream:

1. **Member 1 (Frontend & UI/UX)**:
   - Owns UI layout, Tailwind styles, 21st components, aesthetic taste, responsive design.
   - Updates `brain/STATUS_member1_frontend.md`.
2. **Member 2 (Backend & Security)**:
   - Owns NASA Open API integration, server routing, database queries, and backend authentication.
   - Enforces zero exposed API keys in the frontend.
   - Updates `brain/STATUS_member2_backend.md`.
3. **Member 3 (Science & ML)**:
   - Owns dataset ingestion, scientific algorithms, satellite telemetry processing, ML inference.
   - Updates `brain/STATUS_member3_science_ml.md`.
4. **Member 4 (QA, Integration & Presentation)**:
   - Owns integration testing, Playwright automation, production-grade page verification, documentation, and hackathon presentation.
   - Updates `brain/STATUS_member4_qa_docs.md`.

## Universal Workflows

### 1. Project Startup / Resume
When resuming or entering the project:
1. Read `brain/PROJECT.md` and `brain/MAP.md`.
2. Read `brain/STATUS.md` and active member status file (`STATUS_memberX.md`).
3. If `brain/HANDOFF.md` exists, read it.
4. Report immediate status and top pending action.

### 2. Session Handoff (`HANDOFF.md`)
When wrapping up work or switching tasks:
1. Update active member status file (`STATUS_memberX.md`).
2. Settle architectural decisions into `DECISIONS.md`.
3. Record operational commands into `topics/operations/RUNBOOK.md`.
4. Write a concise shift report in `brain/HANDOFF.md` highlighting:
   - Completed work
   - Immediate next action for the incoming session/member
   - Any blockers or pending decisions
