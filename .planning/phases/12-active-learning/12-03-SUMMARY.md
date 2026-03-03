---
phase: 12-active-learning
plan: "03"
subsystem: frontend
tags: [active-learning, strategy-picker, training-ui, typescript]
dependency_graph:
  requires: [12-01, 12-02]
  provides: [strategy-picker-ui, strategy-badge, strategy-chip]
  affects: [TrainingPage, TrainingSession, SessionHistoryList, SessionSummary]
tech_stack:
  added: []
  patterns: [radio-card-picker, availability-aware-disabled, strategy-badge]
key_files:
  created: []
  modified:
    - mizan/frontend/src/lib/types.ts
    - mizan/frontend/src/lib/training-api.ts
    - mizan/frontend/src/pages/TrainingPage.tsx
    - mizan/frontend/src/pages/TrainingSession.tsx
    - mizan/frontend/src/components/SessionHistoryList.tsx
    - mizan/frontend/src/pages/SessionSummary.tsx
decisions:
  - "STRATEGY_LABELS co-located in types.ts (not training-api.ts) so SessionHistoryList and TrainingSession can import without circular dep"
  - "strategyPicker JSX extracted as variable (not component) to share across empty-state and history-state branches"
  - "SamplingStrategy cast used in SessionHistoryList chip to satisfy TypeScript narrowing on optional field"
metrics:
  duration_minutes: 5
  completed_date: "2026-03-03"
  tasks_completed: 2
  tasks_total: 3
  files_modified: 6
---

# Phase 12 Plan 03: Active Learning Frontend UI Summary

**One-liner:** Three-card Arabic strategy picker with availability-aware disabled state, session badge, and history chips wired to the Phase 12 backend.

## What Was Built

- **types.ts**: `SamplingStrategy` type (`'sequential' | 'uncertainty' | 'disagreement'`), `STRATEGY_LABELS` constant with Arabic names, `strategy: SamplingStrategy` field on `TrainingSession` interface.
- **training-api.ts**: `StrategyAvailability` interface, `createSession(strategy?)` updated to accept strategy parameter and POST it in body, `getStrategyAvailability()` function calling `GET /api/training/strategies/availability`.
- **TrainingPage.tsx**: Full rewrite — `STRATEGIES` config array, availability fetched in parallel with `listSessions()`, three radio cards above "ابدأ التدريب" button in both empty-state and history-state. Sequential pre-selected (green), uncertainty/disagreement disabled with Arabic messages when unavailable.
- **TrainingSession.tsx**: Strategy badge (amber for uncertainty, red for disagreement) rendered above `ProgressBar`. Hidden for sequential sessions.
- **SessionHistoryList.tsx**: Strategy chip next to status badge for non-sequential sessions only.
- **SessionSummary.tsx**: `createSession('sequential')` explicit — intent clear, bypass strategy picker.

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

- [x] `mizan/frontend/src/lib/types.ts` — modified
- [x] `mizan/frontend/src/lib/training-api.ts` — modified
- [x] `mizan/frontend/src/pages/TrainingPage.tsx` — modified
- [x] `mizan/frontend/src/pages/TrainingSession.tsx` — modified
- [x] `mizan/frontend/src/components/SessionHistoryList.tsx` — modified
- [x] `mizan/frontend/src/pages/SessionSummary.tsx` — modified
- [x] Task 1 commit: e250a1f
- [x] Task 2 commit: b6f5486
- [x] `npx tsc --noEmit` — zero errors
- [x] `npm run build` — 682 modules, 355KB JS, success

## Self-Check: PASSED
