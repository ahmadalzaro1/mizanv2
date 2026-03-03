---
phase: 12-active-learning
plan: "01"
subsystem: backend
tags: [active-learning, alembic, migration, sampling-strategy, service]
dependency_graph:
  requires: [f8a9b0c1d2e3]
  provides: [g9h0i1j2k3l4, active_learning.py]
  affects: [mizan/backend/app/models/training.py, mizan/backend/app/models/content_example.py]
tech_stack:
  added: []
  patterns: [op.execute CREATE TYPE + postgresql.ENUM(create_type=False), pure service module pattern]
key_files:
  created:
    - mizan/backend/alembic/versions/g9h0i1j2k3l4_phase12_active_learning.py
    - mizan/backend/app/services/active_learning.py
  modified:
    - mizan/backend/app/models/training.py
    - mizan/backend/app/models/content_example.py
decisions:
  - "SamplingStrategy enum added to training.py alongside SessionStatus/ModeratorLabel for colocation"
  - "ai_confidence on content_examples (not session_items) enables pre-computed uncertainty scores at the corpus level"
  - "Disagreement fallback to uncertainty sampling when no labeled history exists prevents empty result sets"
metrics:
  duration_minutes: 5
  completed_date: "2026-03-03"
  tasks_completed: 2
  files_changed: 4
---

# Phase 12 Plan 01: Active Learning Foundation Summary

Alembic migration + SamplingStrategy enum + three-strategy active learning service module powering intelligent example selection for moderator training sessions.

## What Was Built

### Task 1: Alembic Migration + Model Updates

**Migration `g9h0i1j2k3l4`** adds two columns:
- `training_sessions.strategy` — `samplingstrategy` enum, `NOT NULL`, server default `sequential`
- `content_examples.ai_confidence` — `double precision`, nullable (populated by future precompute script)

**`training.py` model changes:**
- New `SamplingStrategy(str, enum.Enum)` class with three members: `sequential`, `uncertainty`, `disagreement`
- New `strategy` column on `TrainingSession` using `Enum(SamplingStrategy, name="samplingstrategy", create_constraint=False)`

**`content_example.py` model changes:**
- Added `Float` to SQLAlchemy imports
- New `ai_confidence = Column(Float, nullable=True)` field on `ContentExample`

### Task 2: active_learning.py Service Module

Pure service module at `mizan/backend/app/services/active_learning.py` with four public functions:

| Function | Strategy | Logic |
|---|---|---|
| `select_examples_sequential` | sequential | Random order, excludes user's seen examples |
| `select_examples_uncertainty` | uncertainty | Closest to confidence=0.5, NULL ai_confidence excluded |
| `select_examples_disagreement` | disagreement | Highest error rate across all moderators, fallback to uncertainty |
| `select_examples` | dispatcher | Routes to correct function by `SamplingStrategy` enum value |

All functions share a `_excluded_ids_subquery()` helper that prevents re-showing examples a user has already labeled.

## Verification Results

- `alembic upgrade head` applied `f8a9b0c1d2e3 -> g9h0i1j2k3l4` without error
- `content_examples.ai_confidence` confirmed as `double precision` in `information_schema.columns`
- `training_sessions.strategy` confirmed as `USER-DEFINED` (samplingstrategy enum)
- All four service functions import cleanly with `DATABASE_URL` set
- `SamplingStrategy` enum: `['sequential', 'uncertainty', 'disagreement']`

## Commits

- `922074a` — feat(12-01): Alembic migration + SamplingStrategy enum on model
- `8a73af3` — feat(12-01): create active_learning.py service with three strategy functions

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/alembic/versions/g9h0i1j2k3l4_phase12_active_learning.py` — FOUND
- `/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/app/services/active_learning.py` — FOUND
- `/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/app/models/training.py` — FOUND (contains SamplingStrategy)
- `/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/app/models/content_example.py` — FOUND (contains ai_confidence)
- Commits 922074a and 8a73af3 — FOUND
