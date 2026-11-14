---
name: security-audit
description: Defensive source code security audit, vulnerability analysis, and secret leak prevention inspired by Strix and Ruflo Security. Audits code for OWASP vulnerabilities, verifies backend authentication, guarantees zero exposed API keys in the frontend, and fixes errors. Only run at project conclusion after explicitly confirming with the user.
---

# Code Security & Vulnerability Audit

Defensive security auditing, vulnerability scanning, and error remediation protocol.

## Mandatory Pre-Execution Gate

> [!IMPORTANT]
> **User Confirmation Required**:
> Never execute an automated security audit or penetration verification unprompted.
> Always ask the user first:
> **"Are you ready for the security audit and code vulnerability review?"**
> Only proceed once the user explicitly confirms readiness.

## Core Security Rules

### 1. Mandatory Backend Authentication
- All protected resources, user mutations, data submissions, and mission data updates must be authenticated in the backend.
- The backend authentication method decided by the team (e.g., Firebase Auth, Supabase JWT, custom session middleware, API tokens) must be verified on every private endpoint.
- Never rely on client-side state alone to restrict access.

### 2. Zero Exposed Secrets in Frontend
- Frontend code (`src/`, `public/`, client JS/JSX/TSX, HTML) must **NEVER** contain exposed private API keys, NASA API private credentials, service account tokens, or database passwords.
- All external NASA or AI APIs requiring secret tokens must be brokered through a backend proxy server or serverless route handler.
- Client bundles must only receive public environment variables or ephemeral session tokens.

## Audit Workflow

When the user confirms they are ready:

### Phase 1: Secret & Credential Scan
1. Scan all frontend source files for hardcoded secrets:
   - Search for patterns: `API_KEY`, `SECRET`, `PASSWORD`, `BEARER`, `TOKEN`, `PRIVATE_KEY`
   - Check `.env` handling: ensure `.env` is listed in `.gitignore`
2. Verify that client-side network calls target local backend endpoints (`/api/...`) rather than calling external authenticated APIs directly with hardcoded credentials.

### Phase 2: OWASP Top 10 & Codebase Vulnerability Analysis
1. **Broken Access Control**: Verify middleware on sensitive routes.
2. **Injection Flaws**: Check SQL queries, MongoDB queries, command executions, and dynamic eval statements.
3. **Cross-Site Scripting (XSS)**: Ensure unescaped HTML injection (`dangerouslySetInnerHTML`, `innerHTML`) is sanitized or eliminated.
4. **CORS & Headers**: Check that CORS configuration is restricted and security headers (CSP, HSTS, X-Frame-Options) are configured.

### Phase 3: Error Remediation
1. For every finding discovered, explain the root cause and line number.
2. Automatically apply the fix to the source code to eliminate the vulnerability.
3. Re-verify the codebase to confirm resolution.

