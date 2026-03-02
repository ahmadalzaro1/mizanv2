# Phase 9: E2E Testing with Playwright - Context

**Gathered:** 2026-03-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Automated E2E tests covering the three-persona demo flow — login, dashboard, observatory, bias auditor, and training session — catching regressions before the hackathon pitch. No new features, no refactoring. Tests validate what exists.

</domain>

<decisions>
## Implementation Decisions

### Test data & environment
- Tests support both modes: local dev servers (default) and Docker Compose (CI). Playwright config switches via `BASE_URL` env var
- Real ML models used for classify/training inference (~250ms per call)
- Bias audit run test SKIPPED — audit UI tested only with pre-cached results (avoids 140s MARBERT batch)
- Existing seed scripts (`seed_content.py` + `seed_jhsc.py`) run in Playwright `globalSetup` to populate 560 examples + 403K JHSC tweets
- Existing demo accounts used: `admin@mizan.local` and `demo-admin@mizan.local` — no test user creation

### Test scope & assertions
- Training flow depth: label 2-3 items only (start session → label → verify feedback → verify calibration score updates). Proves the loop without 20x repetition
- D3.js chart assertions: verify SVG container is visible and contains `<path>` or `<rect>` elements. No visual regression screenshots
- Auth flow covers: login with valid creds, protected route redirect for unauthenticated user, logout clears session
- Arabic/RTL: assert `dir="rtl"` on body/container + verify at least one Arabic string visible on each tested page

### Playwright project setup
- Tests live in `mizan/frontend/e2e/` alongside the frontend code
- Playwright config (`playwright.config.ts`) in `mizan/frontend/`
- TypeScript for all test files and helpers (matches frontend codebase)
- Chromium only — sufficient for hackathon demo (pitch will be on Chrome)
- Timeout: 30s default, 60s extended timeout for training label submission (ML inference latency)

### Auth & session isolation
- Hybrid auth: one dedicated test exercises the login UI flow. All other tests use API-obtained token via Playwright `storageState`
- `globalSetup` calls `POST /auth/login` → saves auth state file → tests reuse it
- Sequential execution (1 worker) — no parallel race conditions on shared DB
- No cleanup between runs — tests are additive. Seed scripts are idempotent. Training sessions are user-scoped so don't collide
- Artifacts: screenshots + trace captured on failure only (Playwright `retain-on-failure`)

### Claude's Discretion
- Exact test file organization within `e2e/` (by page vs by feature)
- Page Object Model usage (if any)
- Helper utility design (login helper, navigation helper)
- Exact Playwright assertions and locator strategies
- `globalSetup` implementation details (seed script invocation method)
- tsconfig.json configuration for test files

</decisions>

<specifics>
## Specific Ideas

- Tests should mirror the hackathon demo path: Observatory (Rania) → Bias Auditor (Lina) → Training (Khaled)
- The token key bug found in Phase 8 (observatory-api.ts + audit-api.ts using wrong localStorage key) is exactly the kind of regression these tests should catch
- Frontend uses `localStorage.mizan_token` for auth — tests should verify this key specifically
- Backend API base: `http://localhost:8000`, Frontend: `http://localhost:5173`
- Auth endpoint is `/auth/login` (NOT `/api/auth/login`)
- D3 charts render inside `useRef` + `useEffect` — may need `waitForSelector` on SVG elements

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mizan/backend/scripts/seed_content.py` — Seeds 560 content examples (idempotent)
- `mizan/backend/scripts/seed_jhsc.py` — Seeds 403K JHSC tweets (idempotent)
- `mizan/frontend/src/lib/api.ts` — Axios instance with baseURL and token interceptor (test reference)
- `mizan/frontend/src/lib/auth.tsx` — AuthProvider with login/logout (test reference for flow)

### Established Patterns
- All protected pages wrapped in `ProtectedRoute` → redirects to `/login` if no token
- API client reads `localStorage.mizan_token` and sets `Authorization: Bearer <token>`
- 401 response interceptor clears token and redirects to `/login`
- Training sessions: POST creates session with 20 random items, PUT submits labels one at a time

### Integration Points
- Frontend routes: `/login`, `/`, `/observatory`, `/audit`, `/train`, `/train/sessions/:id`, `/train/sessions/:id/summary`
- Backend routes: `/auth/login`, `/auth/me`, `/api/training/sessions`, `/api/observatory/trends`, `/api/audit/results`, `/api/classify`
- Docker Compose: db (5433), backend (8000), frontend (5173)
- No existing test infrastructure — Playwright is greenfield

</code_context>

<deferred>
## Deferred Ideas

- CI/CD pipeline integration (GitHub Actions) — separate phase if needed
- Cross-browser testing (Firefox, WebKit) — add later if RTL issues surface
- API-level integration tests (pytest + httpx) — complementary but separate scope
- Performance/load testing — not in scope for E2E
- Visual regression testing with Playwright screenshots — decided against for now

</deferred>

---

*Phase: 09-e2e-testing*
*Context gathered: 2026-03-02*
