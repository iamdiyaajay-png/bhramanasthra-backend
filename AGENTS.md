# AGENTS.md — NASA Hackathon Multi-Agent Policies

## Core Principles
1. **Model Hierarchy**: Gemini 3.8 Flash High is the Supreme Decision-Maker and Architect. `gstack` + `ruflo` plan, `council` models filter and debate, and Gemini makes final design and implementation determinations.
2. **Workstream Isolation**: Respect the 4-member roles defined in `brain/MAP.md` and keep workstream logs updated in `brain/STATUS_member<1-4>_*.md`.
3. **Security Directives**:
   - Strictly enforce backend authentication on all protected endpoints.
   - ZERO exposed private API keys in client-side code. Broker all NASA and external API requests through the backend proxy.
   - Security auditing & penetration checks run strictly defensively, and ONLY after asking:
     *"Are you ready for the security audit and code vulnerability review?"*
4. **Prompt Cheat Sheet**: Respect all cheat sheet triggers (`SCAFFOLD`, `PERSONA`, `GHOST`, `REDTEAM`, `PREMORTEM`, `STEP BACK`, `RANK`, `RACI`, `SOP`, `NEXT ACTION`, `ONE-PAGER`, `TL;DR`, `DIFF`, `CONSTRAINTS`, `VS`, `TIGHTEN`, `DEVIL'S ADVOCATE`, `CLIENT VOICE`, `ELI5`, `SKEPTIC`, `NO YAP`, `5 WHYS`, `FLIP IT`, `PROVE IT`, `WORST CASE`).
5. **Quality Standard**: Verify code against `brain/topics/design/PRODUCTION_PAGES_CHECKLIST.md` and `./.agents/skills/web-design-guidelines/command.md`.

