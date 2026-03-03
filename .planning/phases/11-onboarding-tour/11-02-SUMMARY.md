---
phase: 11-onboarding-tour
plan: 02
subsystem: frontend-onboarding
tags: [driver.js, onboarding-tour, help-button, e2e-tests, rtl, accessibility]
dependency_graph:
  requires: [11-01]
  provides: [UI-04]
  affects: [Layout, Dashboard, E2E test suite]
tech_stack:
  added: []
  patterns: [driver.js step targeting via #id selectors, animate-pulse for first-time UX, useEffect auto-trigger with 500ms delay]
key_files:
  created:
    - mizan/frontend/e2e/onboarding.spec.ts
  modified:
    - mizan/frontend/src/components/Layout.tsx
    - mizan/frontend/src/pages/Dashboard.tsx
decisions:
  - id: id-selectors-not-data-testid
    summary: Use id attributes (not data-testid) on tour targets — Driver.js CSS selectors require standard IDs for stable step targeting
  - id: pulse-via-tourSeen-state
    summary: animate-pulse controlled by tourSeen React state (not localStorage read) so pulse disappears reactively on tour completion without page reload
  - id: auto-trigger-cleanup
    summary: useEffect returns clearTimeout cleanup to prevent startTour firing if Dashboard unmounts before 500ms delay elapses
key_decisions:
  - Use id attributes on tour targets (not data-testid) — Driver.js uses CSS selectors
  - animate-pulse driven by tourSeen React state for reactive removal after tour completes
  - 500ms auto-trigger with cleanup prevents race conditions on fast navigation
metrics:
  duration: 197s
  completed_date: 2026-03-03
  tasks: 2
  files_created: 1
  files_modified: 2
requirements_satisfied: [UI-04]
---

# Phase 11 Plan 02: Onboarding Tour Wiring Summary

**One-liner:** Help button wired into Layout header with pulse animation, Dashboard tour IDs + 500ms auto-trigger, and 10-test Playwright suite for full UI-04 coverage.

---

## What Was Built

### Task 1: Layout + Dashboard Wiring

**Layout.tsx** (`mizan/frontend/src/components/Layout.tsx`):
- Imported `useTour` from `./OnboardingTour`
- Added `const { startTour, tourSeen } = useTour()` in component body
- Added `id="tour-logo"` to header logo `<Link>` element
- Added `id="tour-nav"` to `<nav>` element
- Inserted help button `(?)` between user name span and logout button:
  - `onClick={startTour}` — triggers driver.js tour
  - `title="جولة تعريفية"` and `aria-label="جولة تعريفية"` — accessibility + tooltip
  - `animate-pulse` class applied conditionally when `!tourSeen` (first-time users only)
  - Styled as outlined white circle matching header aesthetics

**Dashboard.tsx** (`mizan/frontend/src/pages/Dashboard.tsx`):
- Added imports: `useEffect`, `useTour`, `isTourSeen`
- Added `id` field to all 3 persona cards: `tour-card-observatory`, `tour-card-audit`, `tour-card-training`
- Added auto-trigger `useEffect`: calls `startTour()` after 500ms when `isTourSeen()` returns false
- `clearTimeout` cleanup prevents timer firing on rapid navigation away

### Task 2: E2E Test Suite

**onboarding.spec.ts** (`mizan/frontend/e2e/onboarding.spec.ts`):

4 test groups, 10 tests total:

| Group | Tests |
|-------|-------|
| Help Button | Visible on dashboard, observatory, training pages |
| Tour Launch via Help Button | Arabic content, step navigation (all 6 persona names), tour close after completion |
| First-Time Auto-Trigger | Auto-triggers without flag, does NOT trigger with flag set |
| Tour Persistence | Sets localStorage after auto-trigger+dismiss, sets localStorage after manual launch+dismiss |

---

## Verification Results

| Check | Result |
|-------|--------|
| `npx tsc --noEmit` (main) | Zero errors |
| `npx tsc -p tsconfig.e2e.json --noEmit` | Zero errors |
| `npm run build` | 682 modules, 352KB JS + 22KB CSS |
| Help button in Layout | Confirmed |
| Tour IDs on Dashboard cards | Confirmed |
| Auto-trigger useEffect | Confirmed |
| E2E test file created | 10 tests across 4 groups |

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Plan 11-01 infrastructure was partially in place**

- **Found during:** Task 1 start
- **Issue:** Plan 11-02 `depends_on: [11-01]` but no `11-01-SUMMARY.md` existed. However, `OnboardingTour.tsx`, `main.tsx` (driver.css import), `index.css` (CSS overrides), and `App.tsx` (TourProvider) were already present — Plan 11-01 work had been done but not committed/summarized.
- **Fix:** Confirmed all 11-01 artifacts were correct before proceeding with 11-02 tasks. No infrastructure changes needed.
- **Files modified:** None (infrastructure was already in place)

---

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Task 1: Layout + Dashboard wiring | cc395fc | Layout.tsx, Dashboard.tsx |
| Task 2: E2E test suite | d11c6a3 | e2e/onboarding.spec.ts |

---

## Self-Check: PASSED

- [x] `mizan/frontend/src/components/Layout.tsx` — exists, has help button with id=tour-logo + id=tour-nav
- [x] `mizan/frontend/src/pages/Dashboard.tsx` — exists, has id=tour-card-* + auto-trigger useEffect
- [x] `mizan/frontend/e2e/onboarding.spec.ts` — exists, 10 tests across 4 groups
- [x] Commit cc395fc — exists (Layout + Dashboard)
- [x] Commit d11c6a3 — exists (E2E tests)
