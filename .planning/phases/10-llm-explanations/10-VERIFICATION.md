---
phase: 10-llm-explanations
verified: 2026-03-03T19:00:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
gaps: []
human_verification:
  - test: "Open a training session, label an item, and watch the explanation card"
    expected: "Spinner appears immediately after submit, then Arabic tokens stream in word-by-word. Header shows '(ذكاء اصطناعي)' or '(قالب)' once complete."
    why_human: "Streaming UI rendering requires live Ollama connection — cannot verify token-by-token animation programmatically"
  - test: "Navigate away mid-stream and return to the same item"
    expected: "Previously streamed text appears immediately from DB cache (no re-stream). '(قالب)' indicator shown for cached."
    why_human: "Requires a live session with Ollama responding to observe the navigation/cache behavior"
  - test: "Set USE_LLM_EXPLANATIONS=false, label a training item"
    expected: "Template explanation appears as a single token with '(قالب)' indicator — no streaming delay"
    why_human: "Env-var toggle requires backend restart; end-to-end behavior observable only in a running environment"
  - test: "Open BiasAuditorPage after running an audit"
    expected: "Overview tab shows spinner with 'جارٍ التحليل...' then Arabic insight builds progressively, then completes"
    why_human: "Streaming UI observable only with Ollama running; token-by-token rendering requires live observation"
  - test: "Run with Ollama stopped (or USE_LLM_EXPLANATIONS=false)"
    expected: "BiasAuditorPage overview tab falls back to the frontend generateInsight() template string — no error shown"
    why_human: "Requires deliberately stopping Ollama to trigger the catch fallback path"
---

# Phase 10: LLM Explanations Verification Report

**Phase Goal:** Replace template-based Arabic explanations with contextual LLM explanations using local Qwen 3.5 via Ollama — producing richer, more natural Arabic reasoning for each classification.
**Verified:** 2026-03-03T19:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Ollama Docker service starts and auto-pulls qwen3.5:9b model on first run | VERIFIED | `docker-compose.yml` lines 19-33: ollama service with `ollama/ollama:latest`, `ollama_data` volume, `OLLAMA_MODEL: qwen3.5:9b` env var, `start_period: 300s` healthcheck. `docker-entrypoint-ollama.sh` polls via wget, pulls `$MODEL`, re-launches foreground. |
| 2 | New `llm_explanation.py` service generates Arabic explanations via local Qwen 3.5 | VERIFIED | `mizan/backend/app/services/llm_explanation.py` exists (273 lines): `generate_stream()` and `generate_insight_stream()` async generators call `AsyncClient(host=settings.ollama_host).chat(model=settings.ollama_model, stream=True, think=True)`. Old `explanation.py` confirmed deleted. |
| 3 | Classify and training endpoints return LLM-generated explanations instead of templates | VERIFIED | `submit_label` in `training.py` sets `ai_label`, `ai_confidence`, `ai_trigger_words` but explicitly leaves `ai_explanation_text = None` (Phase 10 comment at line 213). The new `GET /api/training/sessions/{id}/items/{item_id}/explanation-stream` SSE endpoint (lines 243-339) streams LLM tokens via `generate_stream()` and saves accumulated text to DB. |
| 4 | If Ollama is unavailable, the system falls back to existing template-based explanations gracefully | VERIFIED | `generate_stream()` wraps the Ollama call in `try/except Exception` and yields `generate_explanation(...)` on failure. `classify_health()` wraps Ollama check in `try/except` and returns `ollama_ready=False` (not 500). BiasAuditorPage `fetchInsight()` has a `catch` block that calls `generateInsight(results)` template. `USE_LLM_EXPLANATIONS=false` short-circuits directly to template before any Ollama call. |
| 5 | Explanation quality: contextual, referencing specific words/phrases from the input text | VERIFIED (structural) | `TRAINING_SYSTEM_PROMPT` explicitly instructs: "Include subtle educational guidance — point out linguistic markers or context clues." `_build_training_prompt()` passes the tweet text, AI classification, confidence %, trigger words, hate category, and moderator label to Qwen. `think=True` enables internal reasoning before output. Actual output quality requires human testing with live Ollama. |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `mizan/docker-compose.yml` | Ollama service + ollama_data volume | VERIFIED | Ollama service defined (lines 19-33), `ollama_data` in top-level volumes (line 77), backend `depends_on: ollama: condition: service_healthy`, `OLLAMA_HOST` and `USE_LLM_EXPLANATIONS` in backend env |
| `mizan/docker-entrypoint-ollama.sh` | Pull-first entrypoint script | VERIFIED | 31-line shell script: starts `ollama serve` in background, polls `http://localhost:11434/api/tags` via wget, pulls `$MODEL`, kills background process, `exec ollama serve` in foreground |
| `mizan/backend/requirements.txt` | `ollama>=0.4.0` added | VERIFIED | Line 18: `ollama>=0.4.0` present |
| `mizan/backend/app/core/config.py` | LLM settings added | VERIFIED | Lines 23-25: `use_llm_explanations`, `ollama_host`, `ollama_model` all env-var driven with safe defaults |
| `mizan/backend/app/schemas/classify.py` | Extended HealthResponse | VERIFIED | Lines 31-32: `ollama_ready: bool = False` and `qwen_model_loaded: bool = False` with Phase 10 comment |
| `mizan/backend/app/routers/classify.py` | Async health endpoint with Ollama check | VERIFIED | `classify_health` is `async def` (line 38), checks `AsyncClient.list()` inside `try/except`, returns `HealthResponse(**status, ollama_ready=..., qwen_model_loaded=...)` |
| `mizan/backend/app/services/llm_explanation.py` | Unified LLM + template service (NEW) | VERIFIED | 273 lines: `HATE_TYPE_AR` dict, `TRAINING_SYSTEM_PROMPT`, `INSIGHT_SYSTEM_PROMPT`, `confidence_phrase()`, `format_trigger_words()`, `generate_explanation()`, `_build_training_prompt()`, `_build_insight_prompt()`, `generate_stream()`, `generate_insight_stream()` — all present and substantive |
| `mizan/backend/app/services/explanation.py` | DELETED | VERIFIED | File does not exist. No remaining imports of `app.services.explanation` anywhere in codebase. |
| `mizan/backend/app/routers/training.py` | SSE explanation endpoint + modified submit_label | VERIFIED | `submit_label` leaves `ai_explanation_text = None` (line 226 comment). `stream_explanation` SSE endpoint at line 243: checks cache, extracts data before generator (DetachedInstanceError prevention), streams tokens, saves to DB via direct SQL update |
| `mizan/backend/app/routers/audit.py` | Insight SSE endpoint | VERIFIED | `stream_insight` at line 495: fetches latest `BiasAuditRun`, streams via `generate_insight_stream()`, proper SSE format with `done` and `error` events |
| `mizan/backend/app/routers/dev.py` | Dev test endpoint (NEW) | VERIFIED | 52 lines: `POST /api/dev/test-explanation` streams explanation without training session, calls `generate_stream()` with request fields |
| `mizan/backend/app/main.py` | Dev router registered | VERIFIED | Line 7 imports `dev`; line 51: `app.include_router(dev.router)` |
| `mizan/frontend/src/lib/training-api.ts` | `streamExplanation()` function | VERIFIED | Lines 31-80: `streamExplanation()` uses `fetch()+ReadableStream`, handles `token`/`cached`/`fallback`/`done` events, calls `onToken` and `onDone` callbacks |
| `mizan/frontend/src/lib/audit-api.ts` | `streamInsight()` function | VERIFIED | Lines 154-200: `streamInsight()` uses fetch+ReadableStream, accumulates tokens, throws on error, returns full text |
| `mizan/frontend/src/components/AIExplanation.tsx` | Streaming-aware component | VERIFIED | Props: `explanationText: string \| null`, `isStreaming?: boolean`, `isLLM?: boolean`. Shows spinner when `isStreaming && !explanationText`, pulsing cursor during stream, "(ذكاء اصطناعي)" / "(قالب)" indicator |
| `mizan/frontend/src/components/FeedbackReveal.tsx` | Streaming props added | VERIFIED | Props: `streamedExplanation?: string \| null`, `isStreaming?: boolean`, `isLLMExplanation?: boolean`. Renders `streamedExplanation ?? aiExplanationText`, passes all to `AIExplanation` |
| `mizan/frontend/src/pages/TrainingSession.tsx` | Streaming state wired | VERIFIED | `streamedExplanation`, `isExplanationStreaming`, `isLLMExplanation` state + `streamedRef` useRef. Triggers `streamExplanation()` after `submitLabel` resolves. Resets in `handlePrevious()` and `handleNext()`. |
| `mizan/frontend/src/pages/BiasAuditorPage.tsx` | LLM insight streaming | VERIFIED | `insightText`, `isInsightStreaming` state. `fetchInsight()` with template fallback in catch. `useEffect([auditRun?.id])` triggers on load/re-run. Overview tab renders spinner → progressive text → complete insight. `generateInsight()` preserved as fallback. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `docker-compose.yml` ollama service | backend `depends_on` | `service_healthy` condition | VERIFIED | Line 55-56: `ollama: condition: service_healthy` |
| `config.py OLLAMA_HOST` | `llm_explanation.py AsyncClient` | `settings.ollama_host` | VERIFIED | `generate_stream()` line 219: `AsyncClient(host=settings.ollama_host)` |
| `config.py USE_LLM_EXPLANATIONS` | LLM vs template gate | `settings.use_llm_explanations` | VERIFIED | Both `generate_stream()` and `generate_insight_stream()` check `if not settings.use_llm_explanations` before Ollama call |
| `llm_explanation.generate_stream()` | `training.py` SSE endpoint | `from app.services.llm_explanation import generate_stream` | VERIFIED | `training.py` line 297: deferred import, `async for token in generate_stream(...)` at line 303 |
| `llm_explanation.generate_insight_stream()` | `audit.py` insight SSE endpoint | `from app.services.llm_explanation import generate_insight_stream` | VERIFIED | `audit.py` line 516: deferred import, `async for token in generate_insight_stream(...)` at line 520 |
| `training-api.ts streamExplanation()` | Backend SSE endpoint | `fetch(.../explanation-stream)` | VERIFIED | `training-api.ts` line 41: constructs URL with sessionId/itemId, GET request with Authorization header |
| `audit-api.ts streamInsight()` | Backend SSE endpoint | `fetch(.../insight-stream)` | VERIFIED | `audit-api.ts` line 160: `fetch(\`${baseUrl}/api/audit/results/insight-stream\`)` with Authorization header |
| `FeedbackReveal` | `AIExplanation` | `streamedExplanation ?? aiExplanationText` prop | VERIFIED | `FeedbackReveal.tsx` line 101: `explanationText={streamedExplanation ?? aiExplanationText}` |
| `TrainingSession.tsx` | `streamExplanation()` | triggered in `.then()` after `submitLabel` | VERIFIED | `TrainingSession.tsx` line 106: `streamExplanation(session!.id, updatedItem.id, ...)` inside `submitLabel().then()` |
| `BiasAuditorPage` | `streamInsight()` | `useEffect([auditRun?.id])` | VERIFIED | `BiasAuditorPage.tsx` line 113-118: `useEffect` watches `auditRun?.id`, calls `fetchInsight()` which calls `streamInsight()` |

---

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| AI-02 (enhanced) | 10-01, 10-02, 10-03 | System generates Arabic-language NL explanation (attention-based OR LLM-generated) | SATISFIED (enhanced) | Phase 5 provided template/attention baseline. Phase 10 replaces it with Qwen 3.5 LLM streaming with graceful template fallback. All three plans declare `AI-02 (enhanced)`. The "(enhanced)" qualifier correctly scopes this as an upgrade to existing functionality, not a net-new requirement. REQUIREMENTS.md maps `AI-02` to Phase 5 (baseline); Phase 10 extends without breaking. |

**Note on AI-02 traceability:** `REQUIREMENTS.md` maps AI-02 to Phase 5, not Phase 10. All three Phase 10 plans declare `AI-02 (enhanced)` — this is the correct scoping. The baseline (template explanation) was delivered in Phase 5; Phase 10 upgrades the mechanism to LLM streaming. No orphaned requirements were found for Phase 10.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `docker-entrypoint-ollama.sh` | — | No GPU passthrough in docker-compose | Info | CPU-only Ollama per CONTEXT.md decision; acceptable for demo/hackathon |
| `mizan/backend/app/main.py` | 51 | `dev.router` registered unconditionally | Warning | Dev test endpoint (`POST /api/dev/test-explanation`) is exposed in production Docker Compose. No auth guard. Should be disabled or behind a flag in production. For hackathon demo this is acceptable. |
| No placeholder/stub patterns found | — | — | — | All implementations are substantive |

---

### Human Verification Required

#### 1. Training Flow — Token-by-Token Streaming

**Test:** Open a training session, navigate to an unlabeled item, submit a label. Observe the AI Explanation card.
**Expected:** Spinner appears immediately after submit with "جارٍ التفسير...", then Arabic tokens appear progressively. Header shows "(ذكاء اصطناعي)" once complete.
**Why human:** Token-by-token animation and Ollama connectivity require a live environment.

#### 2. Navigation Cache Behavior

**Test:** Mid-stream, navigate to a previous item, then return to the streaming item.
**Expected:** Navigation resets streaming state (spinner gone). The returned item shows the previously accumulated text from `ai_explanation_text` in local state. No re-stream triggered.
**Why human:** Requires live Ollama connection and observing React state transitions across navigation.

#### 3. Template Fallback Mode (USE_LLM_EXPLANATIONS=false)

**Test:** Set `USE_LLM_EXPLANATIONS=false` in backend env, restart backend, label a training item.
**Expected:** Explanation appears instantly as a single "(قالب)"-labeled Arabic sentence (template). No spinner delay.
**Why human:** Requires env-var toggle and backend restart; end-to-end behavior observable only in a running environment.

#### 4. BiasAuditorPage — LLM Insight Streaming

**Test:** Navigate to the Bias Auditor page after a completed audit run. Observe the overview tab.
**Expected:** Blue insight card shows spinner with "جارٍ التحليل...", then Arabic text builds progressively, then stops with complete 2-3 sentence insight.
**Why human:** Streaming UI observable only with Ollama running; token-by-token rendering requires live observation.

#### 5. BiasAuditor Fallback When Ollama Unavailable

**Test:** Stop Ollama (or set `USE_LLM_EXPLANATIONS=false`), navigate to BiasAuditorPage with existing audit results.
**Expected:** Overview tab shows the frontend `generateInsight()` template string immediately (no spinner, no error message).
**Why human:** Requires deliberately stopping Ollama to trigger the catch block fallback path.

---

### Gaps Summary

No gaps found. All 5 observable truths are verified against the actual codebase. All artifacts exist and are substantive (not stubs). All key links are wired. TypeScript compiles with zero errors. All 6 task commits are present in git log.

The one advisory item — the `dev.router` being exposed unconditionally — is a design decision documented in CONTEXT.md and is appropriate for a hackathon demo context.

---

## Commit Verification

All 6 task commits confirmed in git log:
- `22c45c6` — feat(10-01): add Ollama Docker service with pull-first entrypoint
- `220c63d` — feat(10-01): extend backend config and health endpoint for Ollama
- `f4f239a` — feat(10-02): create llm_explanation.py service and delete explanation.py
- `c071fca` — feat(10-02): add SSE endpoints for training explanation, audit insight, and dev test
- `bd23833` — feat(10-03): add streaming explanation SSE client and streaming-aware UI components
- `21aa829` — feat(10-03): replace BiasAuditorPage template insight with LLM streaming insight

---

_Verified: 2026-03-03T19:00:00Z_
_Verifier: Claude (gsd-verifier)_
