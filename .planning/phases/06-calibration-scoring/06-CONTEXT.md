# Phase 6 Context — Calibration Scoring

> Decisions derived from codebase analysis on 2026-03-02.
> No discuss-phase needed — single-requirement phase with clear implementation path.

---

## Phase Boundary

**Goal**: Moderators see a live calibration score reflecting their agreement with ground-truth labels, updating after each submission.
**Requirements**: TRAIN-06
**Depends on**: Phase 3 (Training UI) ✅, Phase 5 (AI Explanation Layer) ✅

**NOT in scope**: Admin dashboard calibration views (ADMIN-01), cross-session aggregation, moderator ranking.

---

## Decisions

### 1. Computation Location

**Decision**: Frontend-computed from existing item state. No new backend endpoint needed.

- After each `submitLabel()`, the updated item (with `is_correct`) is merged into `session.items` state
- Calibration score = `correctCount / labeledCount * 100` — computed from items already in memory
- Zero added latency, zero API calls, zero backend changes for the live score
- Backend `_serialize_session()` also updated to always return running `correct_count` (not just on completion) for session list consistency

### 2. UI Placement & Design

**Decision**: Dedicated CalibrationScore component between ProgressBar and TweetCard.

- **Position**: Below ProgressBar, above TweetCard. Visible during entire session
- **Display**: Arabic digits percentage with color-coded background
  - ≥80% → green (bg-green-100 text-green-800) — "ممتاز"
  - ≥60% → amber (bg-amber-100 text-amber-800) — "جيد"
  - <60% → red (bg-red-100 text-red-800) — "يحتاج تحسين"
- **Before first label**: Show "—" with neutral gray background and message "ستظهر نسبة المعايرة بعد أول تصنيف"
- **Format**: "نسبة المعايرة: ٧٠٪" (Arabic label, Arabic digits, Arabic percent sign ٪)
- **Animation**: CSS transition on the score number (transition-all duration-300)
- Matches SessionSummary color thresholds for consistency

### 3. Backend Tweak

**Decision**: Update `_serialize_session()` to always compute running `correct_count`.

- Currently `session.correct_count` is only set in the DB when all items are labeled
- Change serialization to always compute from items: `sum(1 for i in session.items if i.is_correct is True)`
- This makes session list (TrainingPage) show in-progress scores too
- No migration needed — just a serialization logic change

---

## Code Context

### Backend
- `mizan/backend/app/routers/training.py` — `_serialize_session()` line 56: currently returns `session.correct_count` (DB column, null until complete)
- `mizan/backend/app/routers/training.py` — `submit_label()` line 237: sets `session.correct_count` only when `all_labeled`

### Frontend
- `mizan/frontend/src/pages/TrainingSession.tsx` — main session page, already tracks all items in state
- `mizan/frontend/src/components/ProgressBar.tsx` — existing progress component (placement reference)
- `mizan/frontend/src/pages/SessionSummary.tsx` — existing score display (color scheme reference)
- `mizan/frontend/src/lib/types.ts` — `TrainingSession.correct_count` already exists

---

*Created: 2026-03-02*
