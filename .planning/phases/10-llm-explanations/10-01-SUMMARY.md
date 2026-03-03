---
phase: 10-llm-explanations
plan: 01
subsystem: infra
tags: [ollama, docker, docker-compose, fastapi, qwen3.5]

# Dependency graph
requires:
  - phase: 04-marbert-inference-api
    provides: classify router and HealthResponse schema this plan extends
provides:
  - Ollama Docker service with auto-pull entrypoint for qwen3.5:9b
  - Backend config settings: use_llm_explanations, ollama_host, ollama_model
  - Extended GET /api/classify/health with ollama_ready + qwen_model_loaded fields
  - ollama>=0.4.0 SDK in requirements.txt
affects: [10-llm-explanations-02, 10-llm-explanations-03]

# Tech tracking
tech-stack:
  added: [ollama/ollama:latest Docker image, ollama Python SDK >=0.4.0]
  patterns:
    - pull-first Docker entrypoint (wget health-poll, pull, re-launch foreground)
    - graceful Ollama reachability check (try/except in async health endpoint)
    - USE_LLM_EXPLANATIONS toggle for CI/low-resource environments

key-files:
  created:
    - mizan/docker-entrypoint-ollama.sh
  modified:
    - mizan/docker-compose.yml
    - mizan/backend/requirements.txt
    - mizan/backend/app/core/config.py
    - mizan/backend/app/schemas/classify.py
    - mizan/backend/app/routers/classify.py

key-decisions:
  - "qwen3.5:9b (not 8b) — no 8b variant exists on Ollama hub; 9b is 6.6GB Q4_K_M"
  - "wget not curl in entrypoint — curl absent from ollama/ollama Docker image"
  - "start_period: 300s healthcheck — first-run model pull takes several minutes"
  - "Ollama port NOT exposed to host — internal Docker network only (no ports: mapping)"
  - "classify_health converted to async def — required for AsyncClient.list() await"
  - "Graceful failure on Ollama unreachable — health returns with ollama_ready=False, no 500"

patterns-established:
  - "pull-first entrypoint: start server in background, health-poll, pull model, re-launch"
  - "USE_LLM_EXPLANATIONS env toggle: centralises LLM on/off across all Phase 10 code"

requirements-completed: [AI-02]

# Metrics
duration: 2min
completed: 2026-03-03
---

# Phase 10 Plan 01: LLM Infrastructure — Ollama Docker + Config Summary

**Ollama Docker service with pull-first qwen3.5:9b entrypoint, backend USE_LLM_EXPLANATIONS config toggle, and extended /health endpoint surfacing Ollama readiness**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-03T16:54:48Z
- **Completed:** 2026-03-03T16:56:19Z
- **Tasks:** 2
- **Files modified:** 6 (1 created, 5 modified)

## Accomplishments
- Ollama Docker service defined in docker-compose.yml with ollama/ollama:latest, named volume `ollama_data`, and 300s start_period to accommodate first-run model pull
- Pull-first shell entrypoint (`docker-entrypoint-ollama.sh`) starts server in background, health-polls via wget until ready, pulls qwen3.5:9b, then re-launches in foreground
- Backend Settings class extended with `use_llm_explanations`, `ollama_host`, and `ollama_model` — all env-var-driven with safe defaults
- `GET /api/classify/health` converted to async and now checks Ollama AsyncClient.list(), surfacing `ollama_ready` and `qwen_model_loaded` without ever raising 500 on failure

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Ollama Docker service with pull-first entrypoint** - `22c45c6` (feat)
2. **Task 2: Extend backend config and health endpoint for Ollama** - `220c63d` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `mizan/docker-entrypoint-ollama.sh` - Pull-first shell entrypoint: polls for ollama readiness, pulls qwen3.5:9b, re-launches in foreground
- `mizan/docker-compose.yml` - Added ollama service + ollama_data volume + backend depends_on ollama + OLLAMA_HOST/USE_LLM_EXPLANATIONS env vars
- `mizan/backend/requirements.txt` - Added `ollama>=0.4.0`
- `mizan/backend/app/core/config.py` - Added use_llm_explanations, ollama_host, ollama_model to Settings
- `mizan/backend/app/schemas/classify.py` - Added ollama_ready and qwen_model_loaded fields to HealthResponse (default False)
- `mizan/backend/app/routers/classify.py` - classify_health converted to async, checks Ollama availability gracefully

## Decisions Made
- qwen3.5:9b chosen (not 8b) — no 8b variant exists on Ollama hub; 9b is the 6.6GB Q4_K_M build
- wget used for health-poll in entrypoint — curl is absent from the ollama/ollama Docker image
- `start_period: 300s` in healthcheck — accommodates first-run model pull which can take several minutes
- Ollama port NOT exposed to host — communication stays on internal Docker network only
- `classify_health` converted from sync `def` to `async def` — required for `await client.list()`
- Graceful failure pattern: if Ollama unreachable, health returns `ollama_ready=False` instead of 500

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None — no external service configuration required. Ollama model pull happens automatically on first `docker compose up`.

## Next Phase Readiness
- Ollama infrastructure layer complete — Plan 02 can implement `llm_explanation.py` service module using `settings.ollama_host` and `settings.ollama_model`
- Health endpoint surfaces Ollama readiness so frontend/devtools can detect model availability before streaming
- `USE_LLM_EXPLANATIONS=false` toggle available for CI and low-resource environments

## Self-Check: PASSED

All files verified present on disk. Both task commits (22c45c6, 220c63d) confirmed in git log.

---
*Phase: 10-llm-explanations*
*Completed: 2026-03-03*
