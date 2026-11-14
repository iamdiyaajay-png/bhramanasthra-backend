---
name: automation-recommender
description: Reverse-engineered automation recommender adapted for Antigravity and Gemini 3.8 Flash High. Analyzes codebase structure, dependencies, and NASA workflows to recommend tailored MCP servers, Antigravity skills, lifecycle hooks, rules, and subagents.
---

# Antigravity Automation Recommender

Reverse-engineered from official agent setup workflows, tailored specifically for Antigravity, Gemini 3.8 Flash High, and hackathon projects.

## Overview

Analyzes project dependencies and architecture to recommend the highest-leverage agent automations across 5 categories:

1. **MCP Servers**: Live documentation, database connectors (Supabase, SQLite), browser automation (Playwright), GitHub.
2. **Workspace Skills**: Multi-step procedures (e.g. `taste-skill`, `21st-ui`, `security-audit`, `web-design-guidelines`).
3. **Workspace Rules (`GEMINI.md` / `AGENTS.md`)**: Enforced architectural constraints, coding standards, backend auth rules.
4. **Subagents**: Specialized parallel delegates (Research, Browser, Image Generation).
5. **Lifecycle Hooks (`hooks.json`)**: Automatic linting, format-on-save, or pre-commit checks.

## Analysis Protocol

### 1. Codebase Inspection
- Examine `package.json`, `pyproject.toml`, or configuration files for frameworks (React, Vite, Express, FastAPI).
- Detect database and cloud providers (Firebase, Supabase, PostgreSQL).
- Identify NASA dataset formats (GeoJSON, HDF5, NetCDF, CSV).

### 2. Tailored Recommendation Grid

| Technology / Need | Recommended Antigravity Automation | Category |
|---|---|---|
| NASA Earth/Space Datasets | `headroom` skill for token compression | Skill |
| React / Tailwind UI | `taste-skill` + `21st-ui` + `awesome-design-md` | Skills |
| UI Quality & Accessibility | `web-design-guidelines` audit | Skill |
| Backend & API Security | `security-audit` pre-ship review | Skill |
| Automated Browser Verification | `playwright-cli` or `browser` subagent | Skill / Subagent |
| Team Multi-Workstream Memory | `project-brain` persistent tracking | Skill |
| Visual Assets / NASA Diagrams | `image-generator` subagent | Subagent |

## Output Format
When invoked:
1. Summarize detected project profile.
2. Recommend the top 1-2 automations per category with actionable installation or usage instructions.
3. Invite the user to request deeper recommendations in any specific area.

