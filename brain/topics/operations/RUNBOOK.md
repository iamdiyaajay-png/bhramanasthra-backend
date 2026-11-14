# Operations & Development Runbook

Verified procedures, command references, and development workflows for the 4-member NASA project.

## 1. Environment Setup

```bash
# Verify Node.js and npm
node -v    # v22+
npm -v     # v10+

# Install root dependencies
npm install

# Start full-stack development environment (Frontend + Backend Proxy)
npm run dev
```

## 2. Workstream Development Commands

### Member 1: Frontend Development
```bash
# Start frontend Vite server (sandboxed)
npm run dev:frontend

# Preview production build
npm run preview
```

### Member 2: Backend API & Proxy Gateway
```bash
# Start secure backend proxy server
npm run dev:backend

# Verify zero exposed client keys in frontend bundle
npm run check:secrets
```

### Member 3: Science & Telemetry Pipeline
```bash
# Ingest and validate NASA open datasets
node scripts/ingest-nasa-data.mjs

# Run Headroom dataset compaction benchmarks
node scripts/compact-telemetry.mjs
```

### Member 4: Quality Assurance & Audits
```bash
# Run Playwright UI automation tests
npx playwright test

# Run Web Design Guidelines audit
# Activated on demand: "Audit UI with web design guidelines"

# Run defensive security code audit (Prompt-Gated)
# Activated on demand: "Are you ready for the security audit and code vulnerability review?"
```

## 3. Production Build & Verification

```bash
# Build frontend and backend distribution bundles
npm run build

# Verify build output
npm run test:verify
```

