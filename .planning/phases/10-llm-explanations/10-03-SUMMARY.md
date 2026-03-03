---
phase: 10-llm-explanations
plan: 03
subsystem: frontend-streaming
tags: [sse, streaming, react, typescript, arabic, explanation, audit]

# Dependency graph
requires:
  - phase: 10-llm-explanations
    plan: 02
    provides: GET /api/training/sessions/{id}/items/{item_id}/explanation-stream SSE, GET /api/audit/results/insight-stream SSE
provides:
  - streamExplanation() SSE consumer in training-api.ts
  - streamInsight() SSE consumer in audit-api.ts
  - Streaming-aware AIExplanation component (nullable text, spinner, cursor, LLM indicator)
  - FeedbackReveal with streamedExplanation/isStreaming/isLLMExplanation props
  - TrainingSession wired to trigger and display streamed explanations post-label
  - BiasAuditorPage overview tab streaming LLM insight with template fallback
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "fetch()+ReadableStream for authenticated SSE — EventSource cannot send Authorization header"
    - "useRef to track accumulated stream text (avoids stale closure in onDone callback)"
    - "streamedExplanation ?? aiExplanationText fallback chain — prefer live stream over cached DB value"
    - "generateInsight() preserved as catch fallback when SSE stream fails"

key-files:
  created: []
  modified:
    - mizan/frontend/src/lib/training-api.ts
    - mizan/frontend/src/lib/audit-api.ts
    - mizan/frontend/src/components/AIExplanation.tsx
    - mizan/frontend/src/components/FeedbackReveal.tsx
    - mizan/frontend/src/pages/TrainingSession.tsx
    - mizan/frontend/src/pages/BiasAuditorPage.tsx

key-decisions:
  - "streamedRef alongside streamedExplanation state — ref prevents stale closure when onDone updates DB cache in setSession callback"
  - "explanationText: string | null in AIExplanation — nullable to support spinner-before-text streaming UX"
  - "isLLM indicator deferred from cached events — cached:true token sets isLLM=false (not re-generated), streaming non-fallback tokens set isLLM=true"
  - "generateInsight() not deleted — catch block in fetchInsight() falls back to template string if SSE fails"

requirements-completed: [AI-02 (enhanced)]

# Metrics
duration: ~3min
completed: 2026-03-03
---

# Phase 10 Plan 03: Frontend SSE Streaming Explanation UI Summary

**fetch()+ReadableStream SSE consumers wired into AIExplanation, FeedbackReveal, TrainingSession, and BiasAuditorPage — training items stream explanation tokens post-label, Bias Auditor overview streams LLM insight on load**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-03T08:25:09Z
- **Completed:** 2026-03-03T08:27:43Z
- **Tasks:** 2
- **Files modified:** 6 (0 created, 6 modified)

## Accomplishments

- Added `streamExplanation()` to `training-api.ts` — GET SSE consumer using fetch+ReadableStream pattern; handles `token`, `cached`, `fallback`, and `done` events
- Added `streamInsight()` to `audit-api.ts` — GET SSE consumer; accumulates tokens, throws on error event, falls back to `generateInsight()` on catch
- Rewrote `AIExplanation.tsx` — `explanationText: string | null` (was `string`); new `isStreaming` prop shows spinner before first token and pulsing cursor during stream; new `isLLM` prop renders "(ذكاء اصطناعي)" or "(قالب)" indicator
- Updated `FeedbackReveal.tsx` — added `streamedExplanation`, `isStreaming`, `isLLMExplanation` optional props; renders streamed explanation preferring it over cached `ai_explanation_text`; fallback to "النموذج غير جاهز بعد" when all three sources are absent
- Updated `TrainingSession.tsx` — added `streamedExplanation` state + `streamedRef` for stale-closure safety; triggers `streamExplanation()` immediately after `submitLabel()` resolves; resets streaming state in `handlePrevious()` and `handleNext()`; updates item `ai_explanation_text` in local state on stream completion so revisiting shows cached text without re-streaming
- Updated `BiasAuditorPage.tsx` — added `insightText` and `isInsightStreaming` state; `fetchInsight()` streams LLM insight with template fallback; `useEffect` on `auditRun?.id` triggers insight fetch when results load or after re-run; overview tab renders spinner → progressive text → complete insight

## Task Commits

Each task was committed atomically:

1. **Task 1: Add SSE consumers and make AIExplanation + FeedbackReveal streaming-aware** - `bd23833` (feat)
2. **Task 2: Replace BiasAuditorPage template insight with LLM streaming insight** - `21aa829` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `mizan/frontend/src/lib/training-api.ts` (MODIFIED) - Added `streamExplanation()` SSE consumer
- `mizan/frontend/src/lib/audit-api.ts` (MODIFIED) - Added `streamInsight()` SSE consumer
- `mizan/frontend/src/components/AIExplanation.tsx` (MODIFIED) - Streaming-aware: nullable text, spinner, cursor, LLM/template indicator
- `mizan/frontend/src/components/FeedbackReveal.tsx` (MODIFIED) - Added streaming props, renders streamed over cached explanation
- `mizan/frontend/src/pages/TrainingSession.tsx` (MODIFIED) - Wired streaming state: trigger after submit, reset on navigation, useRef for onDone closure
- `mizan/frontend/src/pages/BiasAuditorPage.tsx` (MODIFIED) - LLM streaming insight with template fallback in overview tab

## Decisions Made

- **useRef alongside useState for accumulated stream** — `streamedRef.current` is updated synchronously in every token callback, preventing the stale closure problem when `onDone` reads the final accumulated text to update `session.items`
- **explanationText becomes nullable** — Allows the spinner state when `isStreaming=true` but no tokens have arrived yet; the parent passes `null` explicitly rather than an empty string to distinguish "loading" from "empty"
- **cached:true token sets isLLM=false** — A cached explanation was generated by the LLM in a prior session, but is served instantly as a single token; marking it `(قالب)` avoids misleading the user into thinking it's a live LLM call
- **generateInsight() preserved in BiasAuditorPage** — The `catch` block in `fetchInsight()` uses it as the fallback string when the SSE endpoint is unreachable; removing it would silently break the fallback path

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

All commits confirmed in git log:
- `bd23833` — feat(10-03): add streaming explanation SSE client and streaming-aware UI components
- `21aa829` — feat(10-03): replace BiasAuditorPage template insight with LLM streaming insight

All files verified:
- `mizan/frontend/src/lib/training-api.ts` exports `streamExplanation` CONFIRMED
- `mizan/frontend/src/lib/audit-api.ts` exports `streamInsight` CONFIRMED
- `mizan/frontend/src/components/AIExplanation.tsx` accepts `explanationText: string | null`, `isStreaming`, `isLLM` CONFIRMED
- `mizan/frontend/src/components/FeedbackReveal.tsx` accepts `streamedExplanation`, `isStreaming`, `isLLMExplanation` CONFIRMED
- Frontend build: 679 modules, zero TypeScript errors CONFIRMED

---
*Phase: 10-llm-explanations*
*Completed: 2026-03-03*
