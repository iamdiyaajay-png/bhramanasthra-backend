---
name: awesome-design-md
description: Curated collection of DESIGN.md design systems (SpaceX, Stripe, Vercel, Linear, Figma, etc.) for AI coding agents. Use when styling user interfaces, selecting design systems, setting typography/color palettes, or crafting NASA hackathon UI themes.
---

# Awesome DESIGN.md Systems

This skill provides direct access to 70+ production-grade `DESIGN.md` specifications in `./design-md/`.

## When to Use

1. When starting or restyling frontend components, dashboards, landing pages, or visualizations.
2. When the user requests a specific aesthetic (e.g., "Make it look like SpaceX", "Use Linear style", "Apply Stripe/Vercel aesthetic").
3. When establishing color tokens, typography scales, spacing units, and dark mode palettes.

## Available Design Systems

Key curated systems available in `./design-md/<system>/DESIGN.md`:

| Category | Design Systems | Recommended For |
|---|---|---|
| **Space & Aerotech** | `spacex`, `tesla`, `dji`, `bmw-m` | NASA Space Apps, telemetry dashboards, mission control UI |
| **Developer Tools** | `linear.app`, `cursor`, `warp`, `posthog`, `raycast` | Technical tools, clean grids, high information density |
| **Modern SaaS** | `stripe`, `vercel`, `supabase`, `resend`, `framer` | Polished web applications, sleek gradients, accessible components |
| **Creative & Media** | `figma`, `spotify`, `runwayml`, `notion` | Interactive media, data storytelling, dynamic themes |

## How to Apply a System

1. Browse `./design-md/<name>/DESIGN.md` for tokens:
   - Primary, secondary, background, border, surface colors
   - Font family pairings (e.g., Space Grotesk, Inter, JetBrains Mono)
   - Border radius, shadows, glassmorphism, accent glows
2. Copy relevant tokens to your project's `tailwind.config.js`, `index.css`, or root CSS variables.
3. Check `preview.html` or `preview-dark.html` in that folder if available to verify visual output.

