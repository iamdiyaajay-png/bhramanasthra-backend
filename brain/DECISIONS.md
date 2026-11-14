# Architectural Decision Records (ADRs)

## ADR-001: Supreme Synthesizer Model — Gemini 3.8 Flash (High)
- **Status**: Decided
- **Context**: The user requires planning via `gstack` + `ruflo`, multi-perspective filtering via `council`, and final design and implementation plan powered by Gemini.
- **Decision**: Designate Gemini 3.8 Flash High as the supreme architecture engine. All proposals from gstack role personas and council debate are synthesized by Gemini, which makes the final architectural call, produces the definitive implementation plan, and oversees execution.

## ADR-002: 4-Member Multi-Workstream Project Architecture
- **Status**: Decided
- **Context**: 4 team members are collaborating on distinct technical topics in a fast-paced hackathon setting.
- **Decision**: Adopt Project Brain's multi-workstream pattern:
  - Member 1: Frontend & UI/UX (`STATUS_member1_frontend.md`)
  - Member 2: Backend API Gateway & Security (`STATUS_member2_backend.md`)
  - Member 3: Science & ML Telemetry (`STATUS_member3_science_ml.md`)
  - Member 4: QA, Docs & Presentation (`STATUS_member4_qa_docs.md`)

## ADR-003: Mandatory Backend Authentication & Zero Client Secrets
- **Status**: Decided
- **Context**: Hackathon projects frequently leak NASA API tokens or Firebase/Supabase service keys in client bundles, causing security vulnerabilities.
- **Decision**: Absolute zero-tolerance policy for exposed client keys. All external NASA API requests requiring authentication MUST be routed through the backend proxy. All private routes require backend authentication verification.

## ADR-004: Token & Telemetry Optimization via Headroom
- **Status**: Decided
- **Context**: NASA earth and space telemetry datasets can contain thousands of data points that inflate prompt sizes and slow down model execution.
- **Decision**: Utilize Headroom compaction algorithms to statistically preserve dataset boundaries, extremes, and error traces while pruning repetitive rows.

## ADR-005: Audit & Security Verification Protocol
- **Status**: Decided
- **Context**: Penetration testing and code auditing must be safe, authorized, and non-destructive.
- **Decision**: The security audit skill will strictly run defensively against the project's own codebase, and ONLY after presenting the confirmation question: *"Are you ready for the security audit and code vulnerability review?"*.

