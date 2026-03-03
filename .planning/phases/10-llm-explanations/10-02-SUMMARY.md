---
phase: 10-llm-explanations
plan: 02
subsystem: backend-services
tags: [llm, ollama, sse, streaming, fastapi, arabic, explanation]

# Dependency graph
requires:
  - phase: 10-llm-explanations
    plan: 01
    provides: ollama docker service, USE_LLM_EXPLANATIONS config, ollama_host/ollama_model settings
  - phase: 05-ai-explanation-layer
    provides: original explanation.py template functions (merged in)
provides:
  - llm_explanation.py unified service module (LLM + template fallback)
  - GET /api/training/sessions/{id}/items/{item_id}/explanation-stream SSE endpoint
  - GET /api/audit/results/insight-stream SSE endpoint
  - POST /api/dev/test-explanation streaming dev endpoint
affects: [10-llm-explanations-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Unified service module: template fallback functions co-located with LLM streaming generators"
    - "Pre-extract SQLAlchemy data before async generator (prevent DetachedInstanceError)"
    - "Cached explanation check before LLM call (avoid redundant Ollama requests)"
    - "think=True on Ollama chat — internal Qwen reasoning; only chunk.message.content yielded"
    - "Direct SQL update (update(SessionItem).where(...).values(...)) inside async generator"

key-files:
  created:
    - mizan/backend/app/services/llm_explanation.py
    - mizan/backend/app/routers/dev.py
  modified:
    - mizan/backend/app/routers/training.py
    - mizan/backend/app/routers/audit.py
    - mizan/backend/app/main.py
  deleted:
    - mizan/backend/app/services/explanation.py

key-decisions:
  - "llm_explanation.py is the single source of truth for all explanations — template functions are the fallback path, not a separate module"
  - "submit_label leaves ai_explanation_text=None — SSE endpoint generates it asynchronously after label submit completes"
  - "generate_stream() fallback yields entire template as one token — callers handle both streaming and single-token uniformly"
  - "Data extracted before async generators — prevents SQLAlchemy DetachedInstanceError across async yield boundaries"
  - "Cached explanation returned as single token event — frontend treats both streaming and cached responses identically"

requirements-completed: [AI-02 (enhanced)]

# Metrics
duration: 3min
completed: 2026-03-03
---

# Phase 10 Plan 02: LLM Explanation Service + SSE Endpoints Summary

**Unified llm_explanation.py merging Phase 5 template functions with Qwen 3.5 streaming via Ollama AsyncClient, wired into training, audit, and dev SSE endpoints**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-03T08:19:32Z
- **Completed:** 2026-03-03T08:22:26Z
- **Tasks:** 2
- **Files modified:** 5 (2 created, 3 modified, 1 deleted)

## Accomplishments

- Created `llm_explanation.py` — the unified explanation service that merges Phase 5 template functions (HATE_TYPE_AR, confidence_phrase, format_trigger_words, generate_explanation) with new Qwen 3.5 streaming generators (generate_stream, generate_insight_stream)
- Deleted old `explanation.py` — all its functions are absorbed into llm_explanation.py as the fallback path
- Added TRAINING_SYSTEM_PROMPT and INSIGHT_SYSTEM_PROMPT Arabic-language system prompts with strict output rules
- `generate_stream()` async generator: streams Qwen tokens with think=True, only yields chunk.message.content (skips internal reasoning), falls back to template on Ollama failure or USE_LLM_EXPLANATIONS=false
- `generate_insight_stream()` async generator: same pattern for bias audit insights
- `submit_label` in training.py updated: still runs MARBERT classification (ai_label, ai_confidence, ai_trigger_words) but leaves ai_explanation_text=None for async SSE generation
- Added `GET /api/training/sessions/{id}/items/{item_id}/explanation-stream` SSE endpoint — streams explanation tokens, saves to DB, returns cached if already generated
- Added `GET /api/audit/results/insight-stream` SSE endpoint — streams Arabic insight for latest bias audit run
- Created `dev.py` router with `POST /api/dev/test-explanation` for prompt testing without a training session
- Registered dev router in main.py

## Task Commits

Each task was committed atomically:

1. **Task 1: Create llm_explanation.py service and delete explanation.py** - `f4f239a` (feat)
2. **Task 2: Add SSE endpoints for training explanation + bias insight + dev test** - `c071fca` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `mizan/backend/app/services/llm_explanation.py` (NEW) - Unified LLM + template service: HATE_TYPE_AR, confidence_phrase, format_trigger_words, generate_explanation, generate_stream, generate_insight_stream, system prompts, prompt builders
- `mizan/backend/app/routers/dev.py` (NEW) - Dev-only router with POST /api/dev/test-explanation streaming endpoint
- `mizan/backend/app/routers/training.py` (MODIFIED) - submit_label updated to skip inline explanation; added explanation-stream SSE endpoint
- `mizan/backend/app/routers/audit.py` (MODIFIED) - Added /results/insight-stream SSE endpoint
- `mizan/backend/app/main.py` (MODIFIED) - Registered dev router
- `mizan/backend/app/services/explanation.py` (DELETED) - Template functions moved to llm_explanation.py

## Decisions Made

- **llm_explanation.py is the single explanation module** — template functions become the fallback path co-located with LLM generators, not a separate file
- **submit_label leaves ai_explanation_text=None** — SSE endpoint generates it asynchronously; this decouples the synchronous label submission from the potentially slow LLM call
- **generate_stream() yields entire template as one token on fallback** — callers accumulate tokens uniformly; works whether streaming from LLM or receiving a single template string
- **Data extracted before async generators** — All SQLAlchemy ORM fields read synchronously before the generator function closes over them, preventing DetachedInstanceError when yielding across async boundaries
- **Cached explanation check** — If ai_explanation_text already in DB, return it as a single cached:true token event; avoids redundant LLM calls on refresh/reconnect

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. The plan verification check initially appeared to fail on route path assertions (missing prefix `/api/training/`) but the routes were correctly registered — the assertion string in the plan omitted the router prefix. Fixed in the verification command only.

## Self-Check: PASSED

All files verified:
- `mizan/backend/app/services/llm_explanation.py` EXISTS
- `mizan/backend/app/services/explanation.py` DELETED (confirmed)
- `mizan/backend/app/routers/dev.py` EXISTS
- Both task commits (f4f239a, c071fca) confirmed in git log

---
*Phase: 10-llm-explanations*
*Completed: 2026-03-03*
