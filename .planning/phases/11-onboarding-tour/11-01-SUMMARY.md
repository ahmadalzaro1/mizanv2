---
phase: 11-onboarding-tour
plan: "01"
subsystem: frontend-onboarding
tags: [driver.js, onboarding, context, react, typescript, css]
dependency_graph:
  requires: []
  provides: [TourProvider, useTour, isTourSeen, driver-css]
  affects: [mizan/frontend/src/App.tsx, mizan/frontend/src/main.tsx, mizan/frontend/src/index.css]
tech_stack:
  added: [driver.js ^1.4.0]
  patterns: [React Context API, useCallback + useRef for driver instance lifecycle, localStorage tour-seen persistence]
key_files:
  created:
    - mizan/frontend/src/components/OnboardingTour.tsx
  modified:
    - mizan/frontend/package.json
    - mizan/frontend/package-lock.json
    - mizan/frontend/src/main.tsx
    - mizan/frontend/src/index.css
    - mizan/frontend/src/App.tsx
decisions:
  - driver.js ^1.4.0 chosen for zero-dependency RTL-compatible guided tour with built-in TypeScript declarations
  - onDestroyed fires on all exit paths (complete + skip + dismiss) so mizan_tour_seen set correctly
  - tourSeen as useState (not live localStorage read) enables reactive pulse-animation removal on tour completion
  - driverRef.current?.destroy() before each drive() prevents double-click re-trigger bug
  - TourProvider placed inside BrowserRouter but outside Routes for Layout + Dashboard access
  - driver.css imported after index.css to prevent Tailwind preflight from overriding driver button styles
metrics:
  duration_minutes: 1
  completed_date: "2026-03-03"
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 4
---

# Phase 11 Plan 01: Onboarding Tour Infrastructure Summary

**One-liner:** driver.js TourProvider context with 6-step Arabic persona tour, localStorage persistence, and mizan-navy themed popovers wired into App.tsx.

---

## What Was Built

Tour infrastructure for the Mizan onboarding experience:

1. **`OnboardingTour.tsx`** — React context module with:
   - `TourProvider`: Creates a driver.js instance with 6 Arabic tour steps targeting persona-specific elements (`#tour-logo`, `#tour-nav`, `#tour-card-observatory`, `#tour-card-audit`, `#tour-card-training`)
   - `useTour()`: Hook returning `{ startTour, tourSeen }` — callable from Layout (help button, Plan 02) and Dashboard (auto-trigger, Plan 02)
   - `isTourSeen()`: Utility reading `mizan_tour_seen` from localStorage (used for initial state and direct checks)
   - `tourSeen` state variable updated reactively via `onDestroyed` — enables Layout to re-render and remove pulse animation when tour completes

2. **`main.tsx`** — Added `import 'driver.js/dist/driver.css'` after `index.css` (critical order: Tailwind preflight first, then driver styles on top)

3. **`index.css`** — Added `.driver-popover.mizan-tour-popover` CSS block:
   - Tajawal font on all popover text (popovers live outside React DOM, so Tailwind classes cannot reach them)
   - `direction: rtl` for correct Arabic text alignment
   - `#1a1a2e` (mizan-navy) for title color and button background
   - Gray-500 progress text for subtle "1 / 6" counter

4. **`App.tsx`** — Wrapped `<Routes>` with `<TourProvider>` inside `BrowserRouter` + `AuthProvider`:
   - Both Layout (renders in every authenticated route) and Dashboard can now call `useTour()`

---

## Tour Steps

| Step | Target | Title | Persona |
|------|--------|-------|---------|
| 1 | (welcome — no element) | مرحباً بك في ميزان! | — |
| 2 | `#tour-logo` | منصة ميزان | — |
| 3 | `#tour-nav` | الأقسام الثلاثة | — |
| 4 | `#tour-card-observatory` | المرصد — رانيا | رانيا |
| 5 | `#tour-card-audit` | مدقق التحيز — لينا | لينا |
| 6 | `#tour-card-training` | التدريب — خالد | خالد |

Button text: "التالي ←" / "→ السابق" / "ابدأ التدريب" (final CTA sends user to Training).

---

## Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Install driver.js and create TourProvider + useTour hook | e71e122 | package.json, package-lock.json, OnboardingTour.tsx |
| 2 | Import driver CSS, add popover styles, wrap App with TourProvider | b59ccfc | main.tsx, index.css, App.tsx |

---

## Verification Results

1. driver.js ^1.4.0 listed in package.json dependencies — PASS
2. `npx tsc --noEmit` — zero TypeScript errors — PASS
3. `npm run build` — 682 modules, 352KB JS, zero errors — PASS
4. OnboardingTour.tsx exports: TourProvider, useTour, isTourSeen — PASS
5. main.tsx import order: index.css -> driver.css -> App — PASS
6. index.css contains 6 occurrences of `.mizan-tour-popover` selector — PASS
7. App.tsx has `<TourProvider>` wrapping `<Routes>` — PASS

---

## Deviations from Plan

None — plan executed exactly as written.

---

## Self-Check: PASSED

Files verified:
- FOUND: mizan/frontend/src/components/OnboardingTour.tsx
- FOUND: mizan/frontend/src/main.tsx (driver.css import added)
- FOUND: mizan/frontend/src/index.css (mizan-tour-popover block added)
- FOUND: mizan/frontend/src/App.tsx (TourProvider wrapping Routes)

Commits verified:
- FOUND: e71e122 — feat(11-01): install driver.js and create TourProvider + useTour hook
- FOUND: b59ccfc — feat(11-01): import driver CSS, add popover styles, wrap App with TourProvider
