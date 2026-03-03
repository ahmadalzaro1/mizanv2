# Phase 10: LLM-Powered Explanations - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the template-based Arabic explanation system (Phase 5) with contextual LLM explanations using local Qwen 3.5 8B via Ollama. Explanations are generated for both the training flow (per-tweet after label submission) and the Bias Auditor insight summary. Ollama runs as a Docker service alongside the existing stack. Falls back to existing templates when Ollama is unavailable.

</domain>

<decisions>
## Implementation Decisions

### Prompt & Output Design
- Output length: 2-3 sentences (richer than Phase 5's single sentence)
- LLM receives full context: tweet text, MARBERT label, confidence score, top-3 trigger words, hate category, AND the moderator's own label
- Natural LLM voice in Arabic — no enforced formatting conventions (drop «guillemets», fixed confidence phrases). Let Qwen 3.5 write naturally
- English system prompt instructing the model to respond in Arabic
- When moderator and MARBERT disagree, LLM should acknowledge the tension and explain why the model saw it differently
- Always mention the hate category in Arabic (عنصري, عشائري, etc.) when MARBERT classifies as hate
- Include subtle educational guidance — not prescriptive, but gently pointing out markers that are easy to miss
- Thinking mode enabled — Qwen 3.5 reasons internally before producing the Arabic explanation
- Output is plain Arabic text (not structured JSON). Stored in existing `ai_explanation_text` column
- Explanations are streamed word-by-word to the frontend (SSE)
- Explanation card appears immediately with a spinner/loading indicator; first tokens replace the spinner
- TweetCard keeps the existing attention-weight highlights (amber for hate, green for safe) alongside the LLM explanation
- Cache LLM explanations in DB (session_items.ai_explanation_text) — same column as before

### Ollama Integration
- Model: `qwen3.5:8b` (~5GB)
- Deployment: Docker service in docker-compose.yml (alongside db, backend, frontend)
- Auto-pull on startup: Docker entrypoint runs `ollama pull qwen3.5:8b` before service becomes healthy
- Backend communicates via official `ollama` Python SDK (pip package)
- Port: Internal Docker network only (not exposed to host). Backend reaches `ollama:11434`
- Health check: Extend existing `GET /api/classify/health` with `ollama_ready` and `qwen_model_loaded` fields
- CPU-only Docker config (no GPU passthrough)
- Model data persisted in a named Docker volume (`ollama_data`)
- No memory limits on the Ollama container

### Fallback Behavior
- When Ollama is unavailable: fall back to existing template-based explanation (Phase 5's `generate_explanation`) with a subtle UI indicator distinguishing LLM vs template explanations
- Timeout: Claude's discretion (balance UX and model response time)
- No output quality gate — trust the model's output. Iterate on prompt to fix quality issues
- Env var toggle: `USE_LLM_EXPLANATIONS=true/false` to disable LLM entirely (useful for CI, testing, low-resource machines)

### Scope of Replacement
- Training flow: LLM explanations replace templates in submit_label (training.py)
- Standalone classify endpoint (`POST /api/classify`): unchanged, stays MARBERT-only
- Bias Auditor: `generateInsight()` also uses Qwen 3.5 via the same LLM service (streamed)
- Single module: `llm_explanation.py` handles both training explanations AND bias auditor insights
- Old `explanation.py` merged into `llm_explanation.py` — template functions become the fallback path within the same file

### Streaming Architecture
- New SSE endpoint for training: `GET /api/training/sessions/{id}/items/{item_id}/explanation-stream` — called AFTER label submission completes
- SSE format and frontend client approach: Claude's discretion (likely fetch() + ReadableStream to match Phase 09.1 pattern and support Authorization headers)
- If user navigates away mid-stream: let the stream finish in the background, save full explanation to DB when done
- Bias Auditor insight also streams via SSE (consistent UX across both features)

### Prompt Iteration Workflow
- System prompt storage: Claude's discretion (practical for hackathon project)
- Dev-only test endpoint: `POST /api/dev/test-explanation` — accepts raw text + label, returns LLM explanation without needing a training session
- No explanation source column in DB — subtle UI indicator is sufficient

### Claude's Discretion
- Exact SSE event format (simple token chunks vs Ollama passthrough)
- Frontend SSE client implementation (likely fetch() + ReadableStream per Phase 09.1 pattern)
- Timeout threshold before falling back to templates
- System prompt storage location (Python constant vs config file)
- Exact spinner/loading indicator design in explanation card

</decisions>

<specifics>
## Specific Ideas

- Qwen 3.5 (not 2.5) — user explicitly requested the newer model
- Thinking mode should be enabled for better quality Arabic output
- The streaming word-by-word effect should feel modern/AI-like
- Explanation card shows spinner immediately, then tokens flow in
- Both training AND bias auditor use the LLM — single service module

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `explanation.py` — Template functions (`generate_explanation`, `confidence_phrase`, `format_trigger_words`, `HATE_TYPE_AR`) become the fallback path in the merged `llm_explanation.py`
- `ml_models.py` — `classify_with_explanation()` already extracts attention weights and top tokens. Continue using this for MARBERT classification + trigger word extraction
- `AIExplanation.tsx` — Blue card component for displaying explanation text. Will need streaming support added
- `FeedbackReveal.tsx` — Already integrates AI explanation with cold start fallback. Will need to trigger SSE stream after label submission
- `audit-api.ts` — SSE streaming pattern from Phase 09.1 (fetch + ReadableStream with Authorization header). Reuse for explanation streaming

### Established Patterns
- SSE streaming: Phase 09.1 established fetch() + ReadableStream pattern for authenticated SSE (EventSource can't send Bearer tokens)
- Docker services: db/backend/frontend in docker-compose.yml with named volumes and health checks
- Model loading: Lifespan pattern in `app/main.py` for loading ML models at startup
- Config: `app/core/config.py` Settings class with env var overrides

### Integration Points
- `training.py` submit_label endpoint: triggers MARBERT classification, then calls new LLM service for explanation
- `docker-compose.yml`: add ollama service with volume and health check
- `requirements.txt`: add `ollama` pip package
- `app/main.py`: initialize Ollama connection in lifespan
- `classify/health` endpoint: extend with Ollama status fields
- Bias Auditor `audit.py`: replace `generateInsight()` call with LLM service
- Frontend `training-api.ts`: new function to consume explanation SSE stream

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 10-llm-explanations*
*Context gathered: 2026-03-03*
