# NASA Hackathon Workspace Directives (Gemini 3.8 Flash High)

## 1. 4-Member Team Architecture & RACI
This project is an advanced NASA Space Apps Hackathon platform divided into 4 specialized workstreams:
- **Member 1 (Frontend & Interaction Lead)**: UI/UX, Tailwind CSS v4, 3D space visualizer, 21st components, aesthetic taste (`taste-skill`, `21st-ui`, `awesome-design-md`). Updates `brain/STATUS_member1_frontend.md`.
- **Member 2 (Backend & Security Lead)**: NASA API gateway, server proxy, rate limiting, and backend authentication (`security-audit`, `automation-recommender`). Updates `brain/STATUS_member2_backend.md`.
- **Member 3 (Science & ML Lead)**: NASA scientific datasets, telemetry modeling, and Headroom context compaction (`headroom`, `project-brain`). Updates `brain/STATUS_member3_science_ml.md`.
- **Member 4 (QA, Operations & Pitch Lead)**: Playwright tests, web design guidelines audit, 11 production-grade pages, and hackathon presentation (`playwright-cli`, `web-design-guidelines`, `gstack`, `task-observer`). Updates `brain/STATUS_member4_qa_docs.md`.

---

## 2. Planning, Council & Decision Authority
- **Planning Triad**: Use `gstack` role reviews (CEO, Eng, QA, Security) and `ruflo` swarm task graphs for initial planning.
- **Council Filtering**: Filter proposed alternatives through dialectic council perspectives (Contrarian, First-Principles, Pragmatic Builder).
- **Gemini Supreme Authority**: Gemini 3.8 Flash High serves as the Supreme System Architect and Decision-Maker. Gemini evaluates council debates, resolves trade-offs, finalizes the complete technical design, and outputs the authoritative step-by-step implementation plan.

---

## 3. Mandatory Security & Authentication Directives
1. **Strict Backend Authentication**:
   - All mutations, user data, and protected endpoints must be authenticated on the backend.
   - Never rely exclusively on client-side state for access control.
2. **Zero Exposed Frontend Keys**:
   - Client bundles (HTML, JS, JSX, TSX) must **NEVER** contain exposed private API keys, NASA API private credentials, service account tokens, or database passwords.
   - All external APIs requiring private keys must be proxied through the backend server.
3. **Pre-Audit Permission Gate**:
   - Never run automated security audits or penetration checks without first asking the user:
     **"Are you ready for the security audit and code vulnerability review?"**
   - Run defensive source code auditing, static vulnerability analysis, and OWASP Top 10 checks only after receiving explicit user confirmation, then automatically fix all detected flaws.

---

## 4. Claude Prompt Cheat Sheet Quick Reference
When the user invokes any of the following cheat sheet codes anywhere in their prompt, execute the corresponding directive:

| Code / Trigger | Directive & Behavior |
|---|---|
| `SCAFFOLD` / `scaffold this first` | Show clear skeleton/architecture before writing complete code. |
| `PERSONA` / `you are a [role]` | Adopt the specified expert persona with deep technical authority. |
| `GHOST` / `/ghost` | Eliminate all robotic AI boilerplate, fillers, and generic conversational fluff. |
| `REDTEAM` / `/redteam` | Rigorously challenge the plan, uncover attack vectors, and identify vulnerabilities. |
| `PREMORTEM` / `/premortem` | Assume the hackathon demo failed; identify the root causes that led to failure. |
| `STEP BACK` / `step back` | Pause, reframe the high-level objective, and view from first principles. |
| `RANK` / `rank these` | Provide an unambiguous prioritized list based on impact and urgency. |
| `RACI` / `make this a RACI` | Map tasks across the 4 team members: Responsible, Accountable, Consulted, Informed. |
| `SOP` / `turn into an SOP` | Convert procedure into a repeatable, step-by-step standard operating procedure. |
| `NEXT ACTION` / `next action?` | Output exactly ONE clear, immediate next action to take right now. |
| `ONE-PAGER` / `one-pager` | Produce a concise, executive summary tailored for hackathon judges and leadership. |
| `TL;DR` / `tl;dr` | Deliver the core conclusion in the very first sentence. |
| `DIFF` / `diff this` | Output an explicit comparison highlighting what changed between versions. |
| `CONSTRAINTS` / `given ₹X, Y days`| Ground the plan strictly within the specified budget, time, and resource limits. |
| `VS` / `X vs Y` | Compare alternatives side-by-side and force a definitive, justified selection. |
| `TIGHTEN` / `tighten this` | Strip adjectives, compress sentences, and maximize information density. |
| `DEVIL'S ADVOCATE` / `devil's advocate`| Aggressively challenge the prevailing assumption and argue the counter-case. |
| `CLIENT VOICE` / `read as the client` | Evaluate the user experience and copy from the perspective of NASA judges. |
| `ELI5` / `eli5` | Explain complex orbital mechanics or ML algorithms using simple analogies. |
| `SKEPTIC` / `/skeptic` | Interrogate the underlying premise of the question before attempting an answer. |
| `NO YAP` / `/noyap` | Immediate code or bullet points only. Zero conversational introductory text. |
| `5 WHYS` / `5 whys` | Drill down through 5 successive layers of causality to find root origin. |
| `FLIP IT` / `flip it` | Invert the solution space and explore the exact opposite approach. |
| `PROVE IT` / `prove it` | Demand concrete metrics, benchmarks, formulas, or empirical verification. |
| `WORST CASE` / `worst case?` | Rapid risk assessment outlining catastrophic failure modes and fallbacks. |

---

## 5. Web Design Guidelines & Production Pages
- **Web Design Guidelines**: Upon request ("audit UI", "review UX"), audit against `./.agents/skills/web-design-guidelines/command.md` using terse `file:line` format.
- **Production Pages**: Ensure all 11 production pages/states from `brain/topics/design/PRODUCTION_PAGES_CHECKLIST.md` (404, 500 error boundary, empty states, loading skeletons, team credits, onboarding tour, status diagnostics, offline banner, feedback modal) are implemented.

