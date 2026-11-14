---
name: council-planner
description: Unified strategic planning, deliberation, and execution architecture combining gstack (role personas), ruflo (hierarchical swarm planning), and council (multi-perspective filtering), with Gemini 3.8 Flash High synthesizing, finalizing design, and producing the authoritative implementation plan.
---

# Unified Council Planner for Gemini 3.8 Flash (High)

A tripartite planning and deliberation architecture combining:
1. **gstack**: Startup role personas (CEO review, Engineering review, QA, CSO/Security)
2. **ruflo**: Multi-agent swarm orchestration and task graph decomposition
3. **claude-council**: Multi-perspective dialectic filtering and stress-testing
4. **Gemini 3.8 Flash High**: Supreme Synthesizer, System Architect, Final Design & Implementation Authority

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PLANNING PHASE (gstack + ruflo)                          │
│    • gstack Personas: /plan-ceo-review, /plan-eng-review    │
│    • Ruflo Swarm Task Decomposition: 4-Member Workstreams   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. FILTERING PHASE (Council Deliberation)                   │
│    • The Contrarian: Identifies hidden failure points       │
│    • The First-Principles Thinker: Strips to fundamentals   │
│    • The Pragmatic Builder: Evaluates hackathon deadline    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. FINAL SYNTHESIS & EXECUTION (Gemini 3.8 Flash High)      │
│    • Resolves divergences and selects optimal path          │
│    • Finalizes technical architecture & design specs        │
│    • Emits Authoritative Step-by-Step Implementation Plan   │
└─────────────────────────────────────────────────────────────┘
```

## Workflow Execution

### Step 1: Planning with gstack + Ruflo
When approaching a complex feature, system design, or hackathon milestone:
- **CEO/Product Perspective (`gstack`)**: What is the hackathon pitch? What makes this stand out to NASA judges? What is in scope and what is explicitly excluded?
- **Engineering Manager Perspective (`gstack`)**: What is the data flow? Are backend APIs authenticated? Are there any exposed secrets? What is the performance profile?
- **Ruflo Swarm Graph**: Divide the plan across the 4 team members:
  - Member 1: Frontend & UI
  - Member 2: Backend API & Auth
  - Member 3: Science & ML
  - Member 4: QA, Docs & High-Value Pages

### Step 2: Multi-Perspective Council Filtering
Filter the proposed options through diverse analytical lenses:
1. **The Contrarian**: What could break during a live 3-minute hackathon demo? Where are we over-complicating?
2. **The First-Principles Thinker**: Do we really need a complex database, or is an in-memory/cached NASA API pipeline sufficient?
3. **The Pragmatic Builder**: Can this be built and tested within the remaining hackathon hours?

### Step 3: Gemini 3.8 Flash High Synthesis & Final Implementation Plan
Gemini 3.8 Flash High resolves all debates, makes final design determinations, and establishes:
1. **System Design Specification**: Component contracts, state models, and NASA API endpoints.
2. **Security & Auth Mandate**: Strict backend authentication, zero exposed keys in frontend.
3. **Step-by-Step Execution Plan**: Discrete, verifiable tasks assigned to workstreams.
4. **Verification Gate**: Clear test steps using Playwright and web design guidelines.

