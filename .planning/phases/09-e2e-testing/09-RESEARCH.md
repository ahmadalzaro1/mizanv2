# Phase 9 Research — E2E Testing with Playwright

**Researched:** 2026-03-02
**Phase:** 09-e2e-testing
**Status:** Ready to plan

---

## 1. What This Phase Does

Phase 9 installs Playwright and writes automated end-to-end tests covering the full three-persona
demo path: login → dashboard → Observatory (Rania) → Bias Auditor (Lina) → Moderator Training
(Khaled). No new features. Tests validate that everything built in Phases 1–8 keeps working.

---

## 2. Current Frontend Structure

All code lives in `mizan/frontend/`.

### Routes (from `src/App.tsx`)
| Route | Component | Protected |
|-------|-----------|-----------|
| `/login` | `Login` | No |
| `/` | `Dashboard` | Yes |
| `/observatory` | `ObservatoryPage` | Yes |
| `/audit` | `BiasAuditorPage` | Yes |
| `/train` | `TrainingPage` | Yes |
| `/train/sessions/:sessionId` | `TrainingSessionPage` | Yes |
| `/train/sessions/:sessionId/summary` | `SessionSummary` | Yes |
| `*` | Redirect to `/` | — |

All protected routes are wrapped in `ProtectedRoute`, which redirects to `/login` when
`user` from `AuthContext` is null (after the `isLoading` flag clears).

### Auth Mechanism (from `src/lib/api.ts` + `src/lib/auth.tsx`)
- Token stored in `localStorage` key: **`mizan_token`**
- Axios request interceptor reads `localStorage.getItem('mizan_token')` and injects
  `Authorization: Bearer <token>` header on every request
- 401 response interceptor clears `mizan_token` and redirects to `/login`
- `AuthProvider` validates token on mount via `GET /auth/me`; sets `isLoading=true` during that
  check, then reveals protected content or redirects

### HTML Document
`index.html` sets `<html lang="ar" dir="rtl">`. This means the RTL direction assertion can be
checked on the `<html>` element (not just `<body>`).

### Custom Tailwind Colors (from `tailwind.config.js`)
- `mizan-navy`: `#1a1a2e`
- `mizan-surface`: `#f9f9f9`
These appear in class names like `bg-mizan-navy`, `text-mizan-navy`. Tests can use them for
visual anchoring but should rely on text content or ARIA roles for assertions.

---

## 3. Backend Endpoints Relevant to Tests

Base URL: `http://localhost:8000`

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/auth/login` | POST | None | Returns `{ access_token }` JWT |
| `/auth/me` | GET | Bearer | Returns user object (id, email, full_name, role) |
| `/api/observatory/trends` | GET | Bearer | Monthly hate counts + 8 historical events |
| `/api/audit/results` | GET | Bearer | Cached bias audit run (may 404 if none) |
| `/api/audit/run` | POST | Bearer | Triggers 140s MARBERT batch — SKIP in tests |
| `/api/training/sessions` | POST | Bearer | Creates a new 20-item training session |
| `/api/training/sessions` | GET | Bearer | Lists all sessions for user |
| `/api/training/sessions/:id` | GET | Bearer | Session detail with items |
| `/api/training/sessions/:id/items/:itemId` | PUT | Bearer | Submit a label for one item |
| `/api/classify/health` | GET | None | Model load status |
| `/health` | GET | None | Backend liveness |

**Critical**: The auth route is `/auth/login`, NOT `/api/auth/login`. This has tripped up
previous phases and must be exact in both the `globalSetup` API call and any direct axios tests.

---

## 4. Demo Credentials (from `seed.py`)

| Account | Email | Password | Role |
|---------|-------|----------|------|
| Super Admin | `admin@mizan.local` | `mizan_admin_2026` | `super_admin` |
| Demo Admin | `demo-admin@mizan.local` | `demo_admin_2026` | `admin` |

Both accounts are created by `mizan/backend/scripts/seed.py` (idempotent). The demo admin has
`institution_id` set; the super admin has `institution_id=null`.

For tests, use `demo-admin@mizan.local` as the primary test user. It has a real institution_id,
which means the training session creation (POST `/api/training/sessions`) will work correctly —
sessions are user-scoped and do not collide across runs.

---

## 5. Seed Scripts

Seeds are Python scripts inside `mizan/backend/scripts/` that run inside the Docker container (or
with the backend virtualenv activated). They all use `sys.path.insert(0, "/app")` to find the
`app` package.

| Script | What it seeds | Idempotent? |
|--------|---------------|-------------|
| `scripts/seed.py` | Institution + 2 demo user accounts | Yes |
| `scripts/seed_content.py` | 560 content examples (4 datasets) | Yes (upsert on text hash) |
| `scripts/seed_jhsc.py` | 403,688 JHSC tweets | Yes |

**For `globalSetup`**: The seed scripts cannot be called directly from Node.js because they need
the Python runtime and `app` package. Options:
1. `execSync('docker compose exec -T backend python scripts/seed.py')` — requires Docker Compose
   running
2. `execSync('docker compose exec -T backend python scripts/seed_content.py')` — likewise
3. For local-dev mode: use Python directly via `execSync('python scripts/seed_content.py')` with
   the right working directory and `DATABASE_URL` env var

The `globalSetup` should use `child_process.execSync` with a try/catch. Because seeds are
idempotent, running them on every test run is safe and preferred.

The JHSC seed (403K rows) takes several seconds; seed_content.py (560 rows) is fast. Both must
have run before training tests (which draw from content examples) and Observatory tests (which
query JHSC tweets).

---

## 6. Playwright Setup Requirements

### Installation
Playwright must be added as a dev dependency:

```
npm install --save-dev @playwright/test
npx playwright install chromium
```

### Config File: `mizan/frontend/playwright.config.ts`
Key settings:
- `testDir`: `./e2e`
- `use.baseURL`: defaults to `http://localhost:5173`, overridable via `BASE_URL` env var
- `use.storageState`: path to the saved auth state file (used by all tests except the login UI test)
- `projects`: Chromium only
- `timeout`: 30,000ms default; individual tests needing ML inference override to 60,000ms
- `workers`: 1 (sequential to avoid DB race conditions)
- `reporter`: `html` + console
- `retries`: 0 for development (failures must be investigated, not retried blindly)
- `webServer`: optional — can auto-start Vite dev server during test run
- `globalSetup`: path to the setup file that seeds DB + creates `storageState`
- `outputDir`: test artifacts — screenshots + traces on failure only (`retain-on-failure`)

### TypeScript for Tests
The existing `tsconfig.json` includes only `src/`. Tests in `e2e/` need their own compiler config.
Create `mizan/frontend/tsconfig.e2e.json` that:
- `extends` the root `tsconfig.json`
- Sets `moduleResolution: "node"` (Playwright uses Node resolution, not bundler)
- Includes `e2e/**/*.ts` and `playwright.config.ts`
- Does NOT use `allowImportingTsExtensions` or `noEmit` mode that conflicts with Playwright

Alternatively, reference `@playwright/test` types from the root tsconfig or let Playwright handle
its own type resolution. The simplest approach: add a separate `tsconfig.e2e.json` and point
Playwright config's `tsconfig` option at it.

---

## 7. Auth Strategy Details

### globalSetup — saves auth state
`globalSetup` must:
1. Run seed scripts to ensure DB has test data
2. POST to `http://localhost:8000/auth/login` with `demo-admin@mizan.local` credentials
3. Save the returned JWT to a file that Playwright can read as `storageState`

Playwright's `storageState` format stores cookies + `localStorage`. Since this app uses
`localStorage` for the token (not cookies), the saved state must inject the key
`mizan_token` into `localStorage`. The standard Playwright `storageState` file supports this:

```json
{
  "cookies": [],
  "origins": [
    {
      "origin": "http://localhost:5173",
      "localStorage": [
        { "name": "mizan_token", "value": "<jwt>" }
      ]
    }
  ]
}
```

`globalSetup` should write this JSON directly (using `node:fs`) — simpler and more reliable than
launching a browser context just to set localStorage.

### Login UI test — does NOT use storageState
One dedicated test file exercises the actual login page with no pre-set state:
- Navigate to `http://localhost:5173/login`
- Fill email and password inputs
- Click "تسجيل الدخول" (the submit button)
- Assert redirect to `/` (dashboard)
- Assert `localStorage.mizan_token` is set
- Assert the dashboard heading contains "ميزان"

### Protected-route redirect test
With no storageState set:
- Navigate directly to `/observatory`
- Assert that Playwright lands on `/login` (ProtectedRoute redirects)

### Logout test
After using storageState:
- Navigate to `/`
- Click "خروج" (logout button in Layout header)
- Assert redirect to `/login`
- Assert `localStorage.mizan_token` is absent

---

## 8. Page-by-Page Test Scenarios

### Dashboard (`/`)
Assertions:
- `dir="rtl"` is set on `<html>` element (the index.html sets it)
- Heading "ميزان" is visible in the header
- Three persona cards are visible: "المرصد", "مدقق التحيز", "التدريب"
- Persona names visible: "رانيا", "لينا", "خالد"
- Clicking "المرصد" card navigates to `/observatory`

### Observatory (`/observatory`) — Rania's section
D3 chart renders via `useRef` + `useEffect` and only after the API call resolves. Need
`waitForSelector` with a generous timeout.

Assertions:
- Summary cards visible: "إجمالي التغريدات", "تغريدات خطاب كراهية", "نسبة خطاب الكراهية"
- D3 container: `div.relative.w-full` has `minHeight: 400` — wait for it to appear
- SVG element inside the container is visible (`waitForSelector('svg')`)
- SVG contains at least one `<path>` element (the area fill path and line stroke path)
- Historical events section visible ("الأحداث التاريخية المرجعية")
- At least one event label is visible in the legend
- Arabic text check: heading contains Arabic script

**D3 timing note**: The chart renders only after `getTrends()` resolves and the component re-
renders. The `useEffect` triggers after mount. Use `page.waitForSelector('svg path')` with
a 15s timeout.

### Bias Auditor (`/audit`) — Lina's section
The page loads and immediately calls `GET /api/audit/results`. This may return a cached result
or may return a 404 (no cached run). The test must handle both states gracefully.

**Strategy**: Assume a cached result exists (the seed or a prior test run has cached it). If no
cache exists, the page shows "اضغط 'بدء التدقيق'" placeholder — which is still valid to assert.

Assertions (cached run scenario):
- Overall metrics section visible: "F1 الإجمالي", "الدقة", "الاسترجاع"
- BiasChart SVG visible with `<rect>` elements (horizontal bars)
- CSV download button visible: "تحميل التقرير (CSV)"
- Weakness alert (if any F1 < 50%) contains Arabic text

Assertions (no cached run scenario — fallback):
- Page loads without error
- "بدء التدقيق" button is visible
- `running` audit is NOT triggered by the test (skip the 140s batch run)

### Training Flow (`/train` → session → summary) — Khaled's section

This is the most complex flow. Label 2–3 items only.

**Step 1: Training landing page** (`/train`)
- Verify "التدريب" heading or "ابدأ التدريب" / "ابدأ جلسة جديدة" button is visible
- Click the start button
- Assert redirect to `/train/sessions/<uuid>`

**Step 2: Session page** (`/train/sessions/:id`)
- Wait for the tweet card to appear (content loaded from API)
- ProgressBar is visible showing "1 / 20" (or similar Arabic digits)
- CalibrationScore shows placeholder text "ستظهر نسبة المعايرة بعد أول تصنيف" (before any label)
- Arabic text in TweetCard is visible (RTL display)

**Label item 1 (not_hate)**:
- Click "ليس كراهية" button (the green not-hate button)
- Click "إرسال" button
- Wait for the extended timeout (ML inference ~250ms, but allow 60s)
- FeedbackReveal appears: "إجابتك" section visible
- "الإجابة الصحيحة" section visible
- AI explanation card appears (blue card — `AIExplanation` component) or fallback
  "النموذج غير جاهز بعد" — either is valid
- CalibrationScore now shows a percentage (no longer placeholder)

**Label item 2 (hate flow)**:
- Click "التالي" to advance
- Click "خطاب كراهية" button
- Category grid appears — click any category (e.g., "عنصرية")
- Click "إرسال"
- Wait for feedback reveal
- CalibrationScore updates (percentage changes)

**Label item 3**:
- Click "التالي" to advance
- Repeat label + submit for one more item
- Assert calibration score still showing

**Navigation back**:
- Click "السابق" — verify currentIndex decrements (previous item's tweet text is shown)

**End of test**: Do NOT complete all 20 items (slow + leaves DB sessions that fill up training
history). Navigate away or let test end.

### Session Summary (optional smoke test)
If a completed session exists in the DB from a prior run, navigate directly to its summary URL
and verify the score card renders. This is lower priority and can be a separate test.

---

## 9. RTL Assertion Strategy

The CONTEXT.md decision: assert `dir="rtl"` on body/container and verify at least one Arabic
string visible.

**How to assert `dir` attribute**:
```typescript
// Check html element has rtl direction
const html = await page.$('html')
expect(await html?.getAttribute('dir')).toBe('rtl')
```

The `<html dir="rtl">` is set in `index.html` at the document level, so this is reliable
without any dynamic JS setting it.

**Arabic text presence**: Check for a heading that is known to contain Arabic. For example on
dashboard, `page.locator('h2')` should contain "مرحباً" (with user name) or the page title
heading "ميزان".

---

## 10. File Organisation Within `e2e/`

The CONTEXT.md leaves this to Claude's discretion. Recommended structure:

```
mizan/frontend/e2e/
├── fixtures/
│   └── auth-state.json         # Written by globalSetup; .gitignore this file
├── helpers/
│   ├── login.ts                # Utility: login via UI (for the login test)
│   └── seed.ts                 # Utility: invoke seed scripts via execSync
├── global-setup.ts             # Playwright globalSetup: seeds DB + writes auth-state.json
├── auth.spec.ts                # Login UI test + protected route redirect + logout
├── dashboard.spec.ts           # Dashboard cards, navigation, RTL check
├── observatory.spec.ts         # Observatory page, D3 SVG assertions
├── bias-auditor.spec.ts        # Bias Auditor page, metrics or empty state
└── training.spec.ts            # Full training flow: start → label 3 → calibration update
```

Page Object Model (POM) is NOT required — the app is simple enough that inline locators are
clear. If a helper is needed for common locators (like getting the tweet card or label buttons),
extract a thin helper function rather than a full POM class.

---

## 11. Locator Strategy

Playwright locator priority for this codebase:
1. **Text content** (most reliable for Arabic): `page.getByText('تسجيل الدخول')`,
   `page.getByRole('button', { name: 'إرسال' })`
2. **Role-based**: `page.getByRole('heading', { name: 'ميزان' })`,
   `page.getByRole('link', { name: 'المرصد' })`
3. **CSS selector** for D3 elements: `page.locator('svg path')`, `page.locator('svg rect')`
4. **Avoid**: `data-testid` (not present in current codebase — adding them would require modifying
   production components, which is out of scope)

**Key Arabic button text** (with fallback Unicode escapes for safety):
- Submit button: `إرسال`
- Login button: `تسجيل الدخول`
- Hate label: `خطاب كراهية`
- Not-hate label: `ليس كراهية`
- Next button: `التالي`
- Previous button: `السابق`
- Logout: `خروج`
- Start training: `ابدأ التدريب` or `ابدأ جلسة جديدة` (depends on whether sessions exist)

---

## 12. Timing and Async Concerns

| Scenario | Expected delay | Recommended wait |
|----------|---------------|-----------------|
| Page navigation | <500ms | `page.waitForURL()` |
| Protected route redirect | <1s | `page.waitForURL('/login')` |
| Auth me check on mount | <200ms local | `page.waitForSelector(...)` |
| Observatory API + D3 render | 1–3s | `waitForSelector('svg path', { timeout: 15000 })` |
| Audit results API | <500ms | default timeout |
| Training session create | <500ms | `waitForURL('/train/sessions/...')` |
| Label submit + ML inference | ~250ms (MPS) | 60s timeout on that test |
| Label submit feedback reveal | after inference | `waitForSelector('text=إجابتك')` |

---

## 13. Known Edge Cases and Gotchas

### 1. CalibrationScore placeholder vs. active state
Before labeling item 1: CalibrationScore shows "ستظهر نسبة المعايرة بعد أول تصنيف"
After labeling item 1: shows `نسبة المعايرة: XX٪`. Test must wait for the score to appear
after submit, not assert it immediately.

### 2. Two-step labeling for hate items
Clicking "خطاب كراهية" alone does NOT enable "إرسال". A category must also be selected.
The "إرسال" button stays disabled (`disabled:opacity-40`) until both are chosen.

### 3. Anti-cheat ground truth hiding
`ground_truth_label` is null in the API response until the moderator submits a label.
After submit, the backend returns the updated item with ground truth. FeedbackReveal relies
on this — the test should NOT try to read ground truth before submitting.

### 4. Training session starts at item 1 (position 0)
On first load of a new session, `currentIndex = 0` and no items are labeled.
`getSession()` sets `firstUnlabeled = 0`, so no index skip happens.

### 5. ML model cold start
If the backend has just started and models haven't fully loaded, `classify_with_explanation()`
returns the fallback "النموذج غير جاهز بعد". Tests should accept either the AI explanation
card OR the fallback text — not fail if fallback is shown.

### 6. Audit page 404 on first load
`GET /api/audit/results` returns 404 if no audit has been run. The frontend catches this and
shows the empty state. Tests should handle both the 404 path (empty state assertion) and the
cached path (metrics assertion).

### 7. D3 requires clientWidth > 0
`TimelineChart` and `BiasChart` check `containerRef.current.clientWidth`. In headless browser
mode, elements must be visible and have layout dimensions. Chromium with default viewport
(1280x720) should provide this. If the SVG does not render, ensure the page has fully painted
before asserting.

### 8. `mizan_token` key casing matters
The token key is exactly `mizan_token` (lowercase, underscore). The Phase 8 bug was caused by
using the wrong key name. The `storageState` JSON in `globalSetup` must use this exact key.

### 9. Seed scripts require Python + the backend environment
`globalSetup` must know the working directory and environment for the seed scripts. For Docker
Compose runs: `docker compose exec -T backend python scripts/seed.py`. For local runs: the
backend virtualenv must be activated. The plan should document both.

---

## 14. Files to Create

| File | Notes |
|------|-------|
| `mizan/frontend/playwright.config.ts` | Main Playwright config |
| `mizan/frontend/tsconfig.e2e.json` | TS config for test files |
| `mizan/frontend/e2e/global-setup.ts` | DB seed + auth state |
| `mizan/frontend/e2e/fixtures/auth-state.json` | Git-ignored; written at runtime |
| `mizan/frontend/e2e/auth.spec.ts` | Login UI + redirect + logout |
| `mizan/frontend/e2e/dashboard.spec.ts` | Dashboard cards + RTL |
| `mizan/frontend/e2e/observatory.spec.ts` | Observatory D3 chart |
| `mizan/frontend/e2e/bias-auditor.spec.ts` | Bias Auditor page |
| `mizan/frontend/e2e/training.spec.ts` | Training 3-item labeling flow |

Files to modify:
| File | Change |
|------|--------|
| `mizan/frontend/package.json` | Add `@playwright/test` dev dep + `test:e2e` script |
| `mizan/frontend/tsconfig.json` | Add `tsconfig.e2e.json` reference (or just keep separate) |
| `.gitignore` (project root) | Add `mizan/frontend/e2e/fixtures/auth-state.json` and `mizan/frontend/playwright-report/` |

---

## 15. Plan Split Recommendation

Phase 9 maps cleanly to 2 plans:

**Plan 09-01 — Infrastructure Setup**
- Install `@playwright/test` + Chromium browser
- `playwright.config.ts` with all settings
- `tsconfig.e2e.json`
- `global-setup.ts` (seed + auth state)
- `package.json` test script
- `.gitignore` additions
- Smoke test: verify Playwright can launch and reach `/login`

**Plan 09-02 — Test Suite Implementation**
- `auth.spec.ts` — login UI + redirect + logout
- `dashboard.spec.ts` — cards + RTL
- `observatory.spec.ts` — D3 SVG assertions
- `bias-auditor.spec.ts` — metrics or empty state
- `training.spec.ts` — 3-item labeling flow with calibration score check

---

## 16. Open Questions for Planning

None — all decisions are captured in `09-CONTEXT.md`. The plan can proceed without further
user input.

---

*Research complete. Ready for `/gsd:plan-phase 9`.*
