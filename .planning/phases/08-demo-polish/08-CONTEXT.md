# Phase 8 Context — Demo Polish

> Decisions derived from codebase analysis on 2026-03-02.

---

## Phase Boundary

**Goal**: A complete, compelling 5-minute demo path works across all three personas — pitch-ready for the hackathon jury.
**Requirements**: No new requirements — delivers demo integration of all prior phases.
**Depends on**: Phase 7 (Analytics & Research Layer) ✅

**NOT in scope**: New features, admin dashboard, PDF reports, mobile responsive.

---

## Critical Bug Found

**observatory-api.ts and audit-api.ts use wrong token key.**

Both files create standalone axios instances reading `localStorage.getItem('token')` — but the auth system stores tokens under `'mizan_token'`. This means:
- Observatory page will get 401 on every API call
- Bias Auditor page will get 401 on every API call
- CSV download fetch() also uses wrong key

**Fix**: Refactor both to use the shared `api` from `./api.ts` (which correctly reads `mizan_token` and uses `VITE_API_URL`).

The `training-api.ts` is the correct pattern — imports `api` from `./api`.

---

## Polish Items Identified

1. **Login page** — Uses inline styles, not Tailwind. Only page without Tailwind classes.
2. **ProtectedRoute loading** — Inline styles for loading spinner.
3. **Dashboard** — Basic 3-card grid. Could have persona colors + demo flow direction for jury impact.
4. **Layout max-width** — 900px may be tight for D3 charts. Consider widening for Observatory/Audit.
5. **BiasAuditorPage CSV download** — Uses `fetch()` with `localStorage.getItem('token')` (wrong key).

---

## Plan Breakdown

| Plan | Wave | Description |
|------|------|-------------|
| 8.1 | 1 | Fix API client bug + consolidate to shared instance |
| 8.2 | 1 | Login + Dashboard + Layout visual polish |
| 8.3 | 2 | Final build verification |

Wave 1: Bug fix + visual polish (parallel). Wave 2: Verification (depends on Wave 1).

---

*Created: 2026-03-02*
