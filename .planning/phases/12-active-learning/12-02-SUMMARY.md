---
phase: 12-active-learning
plan: "02"
subsystem: backend-api
tags: [active-learning, training-router, fastapi, sampling-strategy]
dependency_graph:
  requires: [12-01]
  provides: [active-learning-api-surface]
  affects: [training-router, schemas]
tech_stack:
  added: []
  patterns: [strategy-dispatch, backward-compatible-body, route-ordering]
key_files:
  created:
    - mizan/backend/scripts/precompute_confidence.py
  modified:
    - mizan/backend/app/schemas/training.py
    - mizan/backend/app/routers/training.py
decisions:
  - CreateSessionRequest uses str field (not SamplingStrategy enum) for backward compat — invalid values fall back to sequential silently
  - strategies/availability endpoint placed before /{session_id} route to prevent FastAPI path-param capture
  - Body(default_factory=CreateSessionRequest) allows POST with empty body to remain valid
metrics:
  duration_minutes: 8
  completed_date: "2026-03-03"
  tasks_completed: 2
  files_modified: 3
---

# Phase 12 Plan 02: Active Learning Router Wiring Summary

Backend API surface wired: `CreateSessionRequest` schema with strategy dispatch, `GET /api/training/strategies/availability`, strategy field in session responses, and `precompute_confidence.py` one-time script.

## What Was Built

### Task 1: Schema + Router Updates

**`mizan/backend/app/schemas/training.py`**
- Added `CreateSessionRequest(BaseModel)` with `strategy: str = "sequential"` — uses `str` (not the enum) so invalid values can be caught gracefully in the router and silently defaulted to sequential.

**`mizan/backend/app/routers/training.py`**

1. New imports: `Body`, `SamplingStrategy`, `CreateSessionRequest`, `select_examples`
2. `_serialize_session()` — added `"strategy": session.strategy.value if session.strategy else "sequential"` to result dict
3. `create_session()` — replaced `func.random()` query block with:
   - Accept `request: CreateSessionRequest = Body(default_factory=CreateSessionRequest)`
   - Parse strategy with `SamplingStrategy(request.strategy)`, fallback to `sequential` on `ValueError`
   - Call `select_examples(db, current_user.id, strategy)` from active_learning service
   - Pass `strategy=strategy` to `TrainingSession(...)` constructor
4. `GET /api/training/strategies/availability` — new endpoint added **before** `/{session_id}` route:
   - `sequential`: always `True`
   - `uncertainty`: `True` if any `content_examples.ai_confidence IS NOT NULL`
   - `disagreement`: `True` if any `session_items.is_correct IS NOT NULL`

### Task 2: precompute_confidence.py

`mizan/backend/scripts/precompute_confidence.py` — one-time batch script:
- Loads MARBERT via `ModelManager.load_models()`
- Queries all `ContentExample` rows where `ai_confidence IS NULL`
- Calls `manager.classify(ex.text, settings.code_mixed_threshold)` per row
- Stores `result["confidence"]` on the ORM object
- Commits every `BATCH_SIZE=50` rows (memory-safe for 560 examples)
- Idempotent: skips already-scored rows
- Clear docstring with exact `python3 -m scripts.precompute_confidence` run command and required env vars

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `mizan/backend/app/schemas/training.py` — FOUND (CreateSessionRequest importable, verified)
- `mizan/backend/app/routers/training.py` — FOUND (routes verified, availability before session_id)
- `mizan/backend/scripts/precompute_confidence.py` — FOUND (syntax OK, main() present)
- Commits: c131b9d (Task 1), 4f2bbff (Task 2)
