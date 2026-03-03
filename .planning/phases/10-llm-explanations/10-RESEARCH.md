# Phase 10: LLM-Powered Explanations - Research

**Researched:** 2026-03-03
**Domain:** Ollama local LLM integration, SSE streaming, Docker Compose service orchestration
**Confidence:** HIGH (Ollama SDK verified via Context7 + official docs; model tag verified via ollama.com/library)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Prompt & Output Design**
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

**Ollama Integration**
- Model: `qwen3.5:9b` (~6.6GB) — **CRITICAL: user said "qwen3.5 8b" but no 8b exists; closest tag is `qwen3.5:9b`**
- Deployment: Docker service in docker-compose.yml (alongside db, backend, frontend)
- Auto-pull on startup: Docker entrypoint runs `ollama pull qwen3.5:9b` before service becomes healthy
- Backend communicates via official `ollama` Python SDK (pip package)
- Port: Internal Docker network only (not exposed to host). Backend reaches `ollama:11434`
- Health check: Extend existing `GET /api/classify/health` with `ollama_ready` and `qwen_model_loaded` fields
- CPU-only Docker config (no GPU passthrough)
- Model data persisted in a named Docker volume (`ollama_data`)
- No memory limits on the Ollama container

**Fallback Behavior**
- When Ollama is unavailable: fall back to existing template-based explanation (Phase 5's `generate_explanation`) with a subtle UI indicator distinguishing LLM vs template explanations
- Timeout: Claude's discretion (balance UX and model response time)
- No output quality gate — trust the model's output. Iterate on prompt to fix quality issues
- Env var toggle: `USE_LLM_EXPLANATIONS=true/false` to disable LLM entirely (useful for CI, testing, low-resource machines)

**Scope of Replacement**
- Training flow: LLM explanations replace templates in submit_label (training.py)
- Standalone classify endpoint (`POST /api/classify`): unchanged, stays MARBERT-only
- Bias Auditor: `generateInsight()` also uses Qwen 3.5 via the same LLM service (streamed)
- Single module: `llm_explanation.py` handles both training explanations AND bias auditor insights
- Old `explanation.py` merged into `llm_explanation.py` — template functions become the fallback path within the same file

**Streaming Architecture**
- New SSE endpoint for training: `GET /api/training/sessions/{id}/items/{item_id}/explanation-stream` — called AFTER label submission completes
- SSE format and frontend client approach: Claude's discretion (likely fetch() + ReadableStream to match Phase 09.1 pattern and support Authorization headers)
- If user navigates away mid-stream: let the stream finish in the background, save full explanation to DB when done
- Bias Auditor insight also streams via SSE (consistent UX across both features)

**Prompt Iteration Workflow**
- System prompt storage: Claude's discretion (practical for hackathon project)
- Dev-only test endpoint: `POST /api/dev/test-explanation` — accepts raw text + label, returns LLM explanation without needing a training session
- No explanation source column in DB — subtle UI indicator is sufficient

### Claude's Discretion
- Exact SSE event format (simple token chunks vs Ollama passthrough)
- Frontend SSE client implementation (likely fetch() + ReadableStream per Phase 09.1 pattern)
- Timeout threshold before falling back to templates
- System prompt storage location (Python constant vs config file)
- Exact spinner/loading indicator design in explanation card

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AI-02 (enhanced) | System generates an Arabic-language natural language explanation of the model's decision — upgraded from attention-template to LLM-generated contextual explanation via Qwen 3.5 | Ollama Python SDK streaming + FastAPI StreamingResponse pattern directly enables this; `think=True` flag on `ollama.AsyncClient.chat()` provides internal reasoning; fallback to `generate_explanation()` from `explanation.py` when Ollama is unavailable |
</phase_requirements>

---

## Summary

Phase 10 replaces the Phase 5 template-based Arabic explanation system with contextual, streamed LLM explanations generated by Qwen 3.5 running locally via Ollama. The core technical challenge is three-fold: (1) running Ollama as a Docker service that auto-pulls the ~6.6GB model on first start, (2) integrating the `ollama` Python SDK's `AsyncClient` with FastAPI's `StreamingResponse` to stream token-by-token explanations via SSE, and (3) updating the frontend to consume the SSE stream mid-render into the existing `AIExplanation` card.

The Phase 09.1 `audit.py` SSE pattern is the primary template for both the backend async generator and the frontend `fetch() + ReadableStream` consumer in `audit-api.ts`. No new SSE infrastructure concepts are introduced — this phase reuses the exact same SSE mechanics, adapted for per-token streaming instead of per-example progress events. The critical difference is that Ollama streams content chunks (not progress integers), so the SSE `data:` payloads are token strings rather than JSON progress objects.

A confirmed risk: the Ollama Docker image does not ship with `curl`, so Docker healthchecks using `CMD curl` will fail. The correct healthcheck uses `CMD-SHELL` with a `wget` alternative or the Python SDK's connection test. The model tag `qwen3.5:8b` does not exist on Ollama — the closest is `qwen3.5:9b` (Q4_K_M, 6.6GB). This must be verified with the user before finalizing the plan.

**Primary recommendation:** Use `ollama.AsyncClient(host="http://ollama:11434")` with `stream=True, think=True` inside a FastAPI `async def` generator, yielding `data: {token}\n\n` SSE events, wrapped in `StreamingResponse`. Replicate the entrypoint pattern of: start ollama in background → wait for ready → pull model → kill background → exec foreground server.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `ollama` (pip) | latest (≥0.4.x) | Python SDK for Ollama API — chat, streaming, async | Official SDK from Ollama team; supports `AsyncClient`, `stream=True`, `think=True` param verified via Context7 |
| `ollama/ollama` (Docker image) | latest | Container running Ollama server on port 11434 | Official image; CPU-only by default, no GPU passthrough needed |
| FastAPI `StreamingResponse` | already in stack | Wrap async generator for SSE | Already used in Phase 09.1 `audit.py` for SSE streaming |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Python `asyncio` | stdlib | `run_in_executor` for sync Ollama SDK if needed | Only if using sync `Client` in async context — prefer `AsyncClient` directly |
| Docker named volume `ollama_data` | n/a | Persist downloaded model across container restarts | Without this, the 6.6GB model re-downloads on every `docker compose up` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `ollama` Python SDK | `httpx` direct to Ollama REST API | SDK is simpler, handles streaming, has `think` param support; direct API works too but more boilerplate |
| `qwen3.5:9b` | `qwen3.5:4b` (2.6GB) or `qwen3:8b` | Smaller = faster cold start and lower RAM; `qwen3.5:9b` is the 9b-parameter model closest to user's intent; `qwen3:8b` (separate model) is also available if quality is similar |
| Custom Docker entrypoint | Sidecar "model-puller" container | Entrypoint in single container is simpler for this project; sidecar is cleaner but adds complexity |

**Installation:**
```bash
# Backend
pip install ollama

# requirements.txt addition
ollama>=0.4.0
```

---

## Architecture Patterns

### Recommended File Structure
```
mizan/backend/
├── app/
│   ├── services/
│   │   ├── llm_explanation.py     # NEW: merged LLM + template fallback
│   │   └── explanation.py         # REMOVED: functions absorbed into llm_explanation.py
│   ├── routers/
│   │   ├── training.py            # MODIFIED: submit_label triggers LLM async, adds SSE endpoint
│   │   └── dev.py                 # NEW: POST /api/dev/test-explanation (dev-only)
│   └── core/
│       └── config.py              # MODIFIED: USE_LLM_EXPLANATIONS, OLLAMA_HOST settings
├── docker-compose.yml             # MODIFIED: add ollama service + ollama_data volume
├── docker-entrypoint-ollama.sh    # NEW: pull-first entrypoint for ollama container
└── requirements.txt               # MODIFIED: add ollama>=0.4.0

mizan/frontend/src/
├── lib/
│   └── training-api.ts            # MODIFIED: add streamExplanation() SSE consumer
└── components/
    └── AIExplanation.tsx          # MODIFIED: accept streaming state (isStreaming, partial text)
```

### Pattern 1: Ollama Docker Service with Pull-First Entrypoint

**What:** Custom bash entrypoint that starts ollama in background, waits for it, pulls the model, then restarts it in foreground.
**When to use:** Whenever a model must be available before the container is considered healthy.

```yaml
# docker-compose.yml addition
services:
  ollama:
    image: ollama/ollama:latest
    restart: unless-stopped
    volumes:
      - ollama_data:/root/.ollama
      - ./docker-entrypoint-ollama.sh:/entrypoint.sh
    entrypoint: ["/bin/sh", "/entrypoint.sh"]
    environment:
      OLLAMA_MODEL: qwen3.5:9b
    healthcheck:
      # curl is NOT in ollama image — use /api/tags via wget or python
      test: ["CMD-SHELL", "wget -qO- http://localhost:11434/api/tags || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 300s   # model pull can take several minutes on first start

  backend:
    depends_on:
      ollama:
        condition: service_healthy
      db:
        condition: service_healthy

volumes:
  ollama_data:
```

```bash
# docker-entrypoint-ollama.sh (pull-first pattern)
#!/bin/sh
set -e

MODEL=${OLLAMA_MODEL:-qwen3.5:9b}

# Start ollama server in background on temp port
ollama serve &
SERVER_PID=$!

# Wait for ollama to be ready (up to 60s)
MAX_RETRIES=30
SLEEP_TIME=2
i=0
until wget -qO- http://localhost:11434/api/tags > /dev/null 2>&1; do
  i=$((i + 1))
  if [ $i -ge $MAX_RETRIES ]; then
    echo "Ollama did not start in time"
    exit 1
  fi
  sleep $SLEEP_TIME
done

# Pull model (no-op if already cached in volume)
ollama pull "$MODEL"

# Kill background server
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true

# Launch production server in foreground
exec ollama serve
```

**Source:** Verified pattern from [DoltHub Pull-First Ollama post](https://www.dolthub.com/blog/2025-03-19-a-pull-first-ollama-docker-image/) + Context7 Ollama docs

### Pattern 2: Ollama AsyncClient Streaming with think=True

**What:** Use `AsyncClient` for async compatibility with FastAPI. Set `stream=True` and `think=True`. Only yield `chunk.message.content` tokens to the SSE stream — skip `chunk.message.thinking` (internal reasoning, not shown to user).
**When to use:** In every FastAPI `async def` route that streams LLM output.

```python
# Source: Context7 /llmstxt/ollama_llms-full_txt
import asyncio
from ollama import AsyncClient

async def stream_explanation_tokens(prompt_messages: list[dict], host: str):
    """Yield content tokens from Qwen3.5 with thinking enabled."""
    client = AsyncClient(host=host)
    async for chunk in await client.chat(
        model="qwen3.5:9b",
        messages=prompt_messages,
        stream=True,
        think=True,      # enables internal reasoning; content is still Arabic text
    ):
        # thinking chunks arrive before content — skip them entirely
        if chunk.message.content:
            yield chunk.message.content
```

### Pattern 3: FastAPI SSE Endpoint for Token Streaming

**What:** Wrap the async Ollama token generator in `StreamingResponse`. Each token is a `data: {token}\n\n` SSE event. A final `data: {"done": true}\n\n` signals completion. The backend saves the full accumulated explanation to DB after the stream completes.
**When to use:** For the training `explanation-stream` endpoint and the Bias Auditor insight endpoint.

```python
# training.py addition
from fastapi.responses import StreamingResponse
import json

@router.get("/sessions/{session_id}/items/{item_id}/explanation-stream")
async def stream_explanation(
    session_id: UUID,
    item_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    # ... fetch item, verify ownership ...

    async def event_generator():
        full_text = ""
        try:
            async for token in llm_explanation.generate_stream(
                tweet_text=item.content_example.text,
                ai_label=item.ai_label,
                ai_confidence=item.ai_confidence,
                ai_top_tokens=item.ai_trigger_words,
                hate_type=item.content_example.hate_type,
                moderator_label=item.moderator_label.value,
            ):
                full_text += token
                yield f"data: {json.dumps({'token': token})}\n\n"

            # Save accumulated text to DB
            item.ai_explanation_text = full_text
            db.commit()

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            # Fall back to template explanation
            fallback = generate_explanation(...)
            item.ai_explanation_text = fallback
            db.commit()
            yield f"data: {json.dumps({'token': fallback, 'fallback': True})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
```

### Pattern 4: Frontend SSE Consumer (fetch + ReadableStream)

**What:** Reuse the `audit-api.ts` SSE pattern. `EventSource` cannot send `Authorization` headers — use `fetch()` + `ReadableStream`. Accumulate tokens into state string; replace spinner when first token arrives.
**When to use:** In `training-api.ts` for the explanation stream; adapted similarly for the Bias Auditor insight stream.

```typescript
// training-api.ts addition (mirrors runAuditStream in audit-api.ts)
export async function streamExplanation(
  sessionId: string,
  itemId: string,
  onToken: (token: string) => void,
): Promise<void> {
  const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
  const token = localStorage.getItem('mizan_token')

  const response = await fetch(
    `${baseUrl}/api/training/sessions/${sessionId}/items/${itemId}/explanation-stream`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )

  if (!response.ok) throw new Error(`Explanation stream failed: ${response.status}`)

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.token) onToken(data.token)
          if (data.done) return
        } catch {
          // ignore partial JSON
        }
      }
    }
  }
}
```

### Pattern 5: AIExplanation Component with Streaming State

**What:** The `AIExplanation` component needs two new states: `isStreaming` (show spinner) and `streamedText` (accumulate tokens). When `isStreaming` is true and `streamedText` is empty, show the spinner. Once tokens arrive, replace spinner with progressively accumulated text.
**When to use:** Called from `FeedbackReveal` after `submit_label` completes.

```typescript
// AIExplanation.tsx — streaming-aware version
interface AIExplanationProps {
  explanationText: string | null  // null = not yet available
  isStreaming?: boolean           // true = show spinner/loading
  isLLM?: boolean                 // true = LLM, false = template (for subtle indicator)
}

export default function AIExplanation({ explanationText, isStreaming, isLLM }: AIExplanationProps) {
  return (
    <div dir="rtl" className="rounded-lg border border-blue-200 bg-blue-50 p-4 font-tajawal">
      <div className="mb-2 flex items-center gap-2">
        {/* header */}
        <h3 className="text-sm font-bold text-blue-800">تفسير النموذج</h3>
        {isLLM !== undefined && (
          <span className="text-xs text-blue-400">{isLLM ? '(ذكاء اصطناعي)' : '(قالب)'}</span>
        )}
      </div>
      {isStreaming && !explanationText ? (
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
          <span className="text-sm text-blue-500">جارٍ التفسير...</span>
        </div>
      ) : (
        <p className="text-base leading-relaxed text-blue-900">{explanationText}</p>
      )}
    </div>
  )
}
```

### Pattern 6: LLM Service Module Structure

**What:** `llm_explanation.py` merges the old `explanation.py` template functions as the fallback path. Exposes two public interfaces: `generate_sync()` (sync, for non-streaming use) and `generate_stream()` (async generator, for SSE endpoints).

```python
# app/services/llm_explanation.py

SYSTEM_PROMPT = """You are an Arabic-language AI assistant helping content moderators..."""

HATE_TYPE_AR: dict[str, str] = { ... }  # from old explanation.py

# --- Fallback (template) functions --- (moved from explanation.py)
def generate_explanation(ai_label, confidence, top_tokens, hate_type=None) -> str: ...
def confidence_phrase(confidence) -> str: ...
def format_trigger_words(top_tokens) -> str: ...

# --- LLM path ---
def _build_prompt(tweet_text, ai_label, confidence, top_tokens, hate_type, moderator_label) -> list[dict]:
    """Build message list for Ollama chat."""
    ...

async def generate_stream(
    tweet_text: str,
    ai_label: str,
    ai_confidence: float,
    ai_top_tokens: list[dict],
    hate_type: str | None,
    moderator_label: str,
) -> AsyncIterator[str]:
    """Yield Arabic explanation tokens from Qwen 3.5. Falls back to template on failure."""
    from app.core.config import settings
    if not settings.use_llm_explanations:
        # yield the template as a single "token" so callers work uniformly
        yield generate_explanation(ai_label, ai_confidence, ai_top_tokens, hate_type)
        return
    try:
        client = AsyncClient(host=settings.ollama_host)
        async for token in ...:
            yield token
    except Exception:
        yield generate_explanation(ai_label, ai_confidence, ai_top_tokens, hate_type)
```

### Anti-Patterns to Avoid

- **Using `EventSource` for authenticated SSE:** `EventSource` does not support custom headers. Always use `fetch() + ReadableStream` with `Authorization: Bearer {token}` — this is already established in Phase 09.1.
- **Blocking the event loop with sync Ollama calls:** The sync `ollama.Client` will block FastAPI's async loop. Always use `AsyncClient` in `async def` routes, or use `asyncio.get_event_loop().run_in_executor(None, ...)` as a last resort.
- **Storing thinking output in the DB:** The `chunk.message.thinking` field contains internal reasoning (sometimes hundreds of tokens). Only accumulate `chunk.message.content` for DB storage.
- **Using `curl` in Docker healthchecks:** `curl` is not in the `ollama/ollama` Docker image. Use `wget` instead: `wget -qO- http://localhost:11434/api/tags`.
- **Setting `service_healthy` depends without `start_period`:** The Ollama container takes 2-10+ minutes on first start to pull the 6.6GB model. Set `start_period: 300s` in the healthcheck or the backend container will fail its dependency check.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Token streaming from Ollama | Custom HTTP chunked reader | `ollama.AsyncClient(..., stream=True)` | SDK handles connection management, chunk parsing, and `think` field separation |
| SSE client with auth headers | EventSource + token hack | `fetch() + ReadableStream` (Phase 09.1 pattern already in `audit-api.ts`) | EventSource has no header support; existing pattern works and is already battle-tested |
| Model availability check | Polling loop in Python | Extend `GET /api/classify/health` with `ollama_ready` + `qwen_model_loaded` | Single health endpoint already exists; adding fields is simpler than a new route |
| Docker healthcheck without curl | Custom binary or polling container | `wget -qO- http://localhost:11434/api/tags` | wget is present in the ollama image; curl is not |

**Key insight:** The Phase 09.1 SSE infrastructure (backend `StreamingResponse` + frontend `fetch/ReadableStream`) is the exact model for Phase 10. The only change is payload shape: progress integers become token strings.

---

## Common Pitfalls

### Pitfall 1: Wrong Model Tag — qwen3.5:8b Does Not Exist

**What goes wrong:** Specifying `qwen3.5:8b` in `ollama pull` fails with "manifest unknown". The entrypoint script fails, the container never becomes healthy, the backend dependency check fails, and the stack does not start.
**Why it happens:** The user specified "Qwen 3.5 8B" but Ollama's library uses `qwen3.5:9b` for the 9-billion-parameter variant (Q4_K_M, 6.6GB). The model that *is* 8 billion parameters exactly is `qwen3:8b` (different model family — Qwen3 not Qwen3.5).
**How to avoid:** Use `qwen3.5:9b` in all configs. Confirm with `ollama list` after pull or check `GET /api/tags` on the Ollama service.
**Warning signs:** `docker compose logs ollama` shows "manifest unknown" or "pull model manifest: 404".

**Recommendation for planner:** Flag this to the user. The CONTEXT.md says "qwen3.5:8b" — the correct tag is `qwen3.5:9b`. Use `qwen3.5:9b` in all plans.

### Pitfall 2: Docker Healthcheck curl Not Found

**What goes wrong:** `healthcheck: test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]` silently fails because `curl` is not installed in `ollama/ollama` image. Container never transitions to `healthy`.
**Why it happens:** The Ollama Docker image is minimal and does not include curl (confirmed via [GitHub issue #9781](https://github.com/ollama/ollama/issues/9781)).
**How to avoid:** Use `wget` instead: `test: ["CMD-SHELL", "wget -qO- http://localhost:11434/api/tags || exit 1"]`.
**Warning signs:** `docker inspect <container> | grep Health` shows `starting` forever even after model pull completes.

### Pitfall 3: Blocking Event Loop with Sync Ollama Client

**What goes wrong:** Using `from ollama import chat` (sync) inside an `async def` FastAPI route freezes the entire server during LLM generation (which takes 10-60+ seconds on CPU). All other requests queue up.
**Why it happens:** FastAPI's ASGI event loop is single-threaded. Sync blocking calls prevent other coroutines from running.
**How to avoid:** Use `from ollama import AsyncClient` and `async for chunk in await client.chat(stream=True)`. If sync SDK is used in legacy code, wrap with `await asyncio.get_event_loop().run_in_executor(None, ...)`.
**Warning signs:** Backend becomes unresponsive during LLM generation; all other API calls time out.

### Pitfall 4: DB Session Lifetime Across Async Yields

**What goes wrong:** Holding a SQLAlchemy `Session` open across `yield` points in an async generator causes session expiry or DetachedInstanceError, especially when the generator takes minutes to complete.
**Why it happens:** SQLAlchemy sessions are not designed to persist across async context switches in long-running generators. Phase 09.1 solved this by loading all examples eagerly before the generator starts.
**How to avoid:** Fetch all required data (item, content_example, existing explanation) before the `event_generator()` is defined and before the first `yield`. Write back to DB only after the stream is complete (after the last `yield`). Use a fresh DB session for the DB write if needed.
**Warning signs:** `DetachedInstanceError` or `sqlalchemy.exc.InvalidRequestError` in logs during or after streaming.

### Pitfall 5: start_period Too Short for First-Run Model Pull

**What goes wrong:** Backend container starts before Ollama finishes pulling the 6.6GB model, `depends_on: condition: service_healthy` is satisfied before the model is actually loaded, and Ollama returns 404 for the model on first inference request.
**Why it happens:** `start_period` defaults to 0s; the healthcheck `/api/tags` returns 200 as soon as Ollama server starts, but before the model pull completes.
**How to avoid:** The entrypoint script should only exec the foreground server AFTER `ollama pull` completes. The healthcheck then passes only after the foreground server is running (which means the model is ready). Set `start_period: 300s` as a safety margin for slow download environments.
**Warning signs:** `GET /api/classify/health` returns `ollama_ready: true` but `qwen_model_loaded: false` immediately after `docker compose up`.

### Pitfall 6: Thinking Tokens Leaked to Frontend

**What goes wrong:** `chunk.message.thinking` tokens (Qwen's internal chain-of-thought, sometimes very long) are accidentally yielded to the SSE stream alongside `chunk.message.content`. Frontend displays reasoning traces instead of the clean Arabic explanation.
**Why it happens:** When `think=True`, the `chunk.message` has two fields: `thinking` (CoT) and `content` (final answer). If the generator yields everything, both appear.
**How to avoid:** In the async generator, only `yield chunk.message.content` when `chunk.message.content` is truthy. Ignore `chunk.message.thinking` entirely.
**Warning signs:** Arabic explanation card shows very long text with raw reasoning artifacts ("Let me think about this..." in English before the Arabic answer).

### Pitfall 7: FeedbackReveal Streaming Lifecycle

**What goes wrong:** The `FeedbackReveal` component triggers the explanation stream on mount (after label submission). If the user immediately presses "Next" before the stream finishes, the SSE stream is abandoned but the background save (backend writes to DB) still works. However, the next time the item is viewed, the DB-saved explanation should be shown — but `currentItem.ai_explanation_text` may not have updated in React state.
**Why it happens:** The `TrainingSession` component holds session state locally. After the stream saves to DB, the local React state still has the old `ai_explanation_text: null`.
**How to avoid:** After streaming completes (on the `done` event), call `getSession()` to refresh the item from API — OR optimistically update the item in local state with the accumulated text as the final `done` event arrives.

---

## Code Examples

Verified patterns from official sources:

### Ollama AsyncClient — Streaming with think=True
```python
# Source: Context7 /llmstxt/ollama_llms-full_txt
import asyncio
from ollama import AsyncClient

async def chat():
    message = {'role': 'user', 'content': 'Why is the sky blue?'}
    async for part in await AsyncClient().chat(
        model='qwen3',
        messages=[message],
        stream=True,
        think=True,
    ):
        if part.message.thinking:
            pass  # Skip thinking; do not yield to SSE
        elif part.message.content:
            print(part.message.content, end='', flush=True)
```

### Ollama SDK — Custom Host
```python
# Source: Context7 /llmstxt/ollama_llms-full_txt
from ollama import Client

client = Client(
    host='http://ollama:11434',  # Docker service name
)
```

### Docker Healthcheck without curl
```yaml
# Source: Verified via GitHub issue #9781 + official Docker docs
healthcheck:
  test: ["CMD-SHELL", "wget -qO- http://localhost:11434/api/tags || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 10
  start_period: 300s
```

### Existing SSE Pattern (Phase 09.1 — authoritative reference)
```python
# Source: mizan/backend/app/routers/audit.py — established project pattern
async def event_generator():
    try:
        for i, item in enumerate(items):
            result = await loop.run_in_executor(None, lambda: ...)
            yield f"data: {json.dumps({'progress': ...})}\n\n"
        yield f"data: {json.dumps({'done': True, ...})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

return StreamingResponse(
    event_generator(),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
)
```

### Existing Frontend SSE Pattern (Phase 09.1 — authoritative reference)
```typescript
// Source: mizan/frontend/src/lib/audit-api.ts — established project pattern
const response = await fetch(`${baseUrl}/api/audit/run/stream`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
})
const reader = response.body!.getReader()
const decoder = new TextDecoder()
let buffer = ''
while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
        if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))
            if (data.done) { result = ...; }
            else if (data.progress !== undefined) { onProgress(data); }
        }
    }
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 5 template: single sentence, fixed phrases | Phase 10 LLM: 2-3 contextual sentences, natural voice | Phase 10 | Richer explanations that reference specific tweet content; mentions moderator's own label |
| No Ollama in stack | Ollama as Docker service with named volume | Phase 10 | Adds ~6.6GB first-run download, ~4-8GB RAM usage during inference (CPU-only) |
| `explanation.py` standalone module | `llm_explanation.py` merged (LLM primary + template fallback) | Phase 10 | Single file; `explanation.py` is deleted, not kept as a parallel module |
| Explanation generated synchronously in `submit_label` | Explanation generated asynchronously via SSE stream after label submit | Phase 10 | submit_label returns immediately; explanation card shows spinner then fills in |

**Deprecated/outdated after Phase 10:**
- `explanation.py`: Deleted. Functions moved to `llm_explanation.py` as the fallback path.
- Phase 5's `generate_explanation()` import in `training.py`: Replaced with `llm_explanation.generate_stream()`.
- Synchronous explanation generation in `submit_label`: `submit_label` no longer generates the explanation; it leaves `ai_explanation_text = None` and the frontend calls the new SSE endpoint.

---

## Open Questions

1. **Model tag confirmation: qwen3.5:8b vs qwen3.5:9b**
   - What we know: `qwen3.5:8b` does not exist on Ollama library. The closest tag is `qwen3.5:9b` (9.65B params, 6.6GB Q4_K_M).
   - What's unclear: Whether the user intended `qwen3.5:9b` or actually meant `qwen3:8b` (a different model family, Qwen3 not Qwen3.5).
   - Recommendation: Plan with `qwen3.5:9b`. Add a note in the plan for the user to confirm.

2. **Timeout before fallback**
   - What we know: CPU-only Qwen3.5 9B can take 30-120 seconds for a 2-3 sentence response.
   - What's unclear: What timeout is acceptable in the training UX? Streaming means the user sees tokens arriving, so latency feels lower.
   - Recommendation: Set a 120-second timeout on the `AsyncClient.chat()` call. If timeout fires, yield the template explanation as a single token event with `fallback: true`.

3. **Bias Auditor LLM insight: SSE endpoint or inline**
   - What we know: CONTEXT.md says "Bias Auditor insight also streams via SSE". The current `generateInsight()` is a synchronous frontend function in `BiasAuditorPage.tsx`.
   - What's unclear: Whether the Bias Auditor insight should be a new backend endpoint (`POST /api/audit/insight-stream`) or computed in-browser from the existing AuditResults.
   - Recommendation: New backend SSE endpoint `GET /api/audit/results/insight-stream`. The backend has the full audit results and can construct the LLM prompt server-side with the complete metrics context.

4. **DB session write safety during streaming**
   - What we know: Phase 09.1 solved a similar problem by loading examples eagerly before the generator.
   - What's unclear: Whether writing `item.ai_explanation_text` at the end of a long-running async generator (after ~60-120s) causes SQLAlchemy session issues.
   - Recommendation: In the explanation SSE endpoint, load the item outside the generator, accumulate the text inside, and use `db.execute(update(SessionItem).where(...).values(...))` at the end for a direct SQL update that doesn't depend on session state.

5. **`USE_LLM_EXPLANATIONS` env var behavior in E2E tests**
   - What we know: E2E tests currently accept either a real AI explanation OR the cold-start fallback (OR pattern in Playwright). With Phase 10, the SSE stream adds latency and a new fallback path.
   - What's unclear: Whether E2E tests should set `USE_LLM_EXPLANATIONS=false` to keep tests deterministic, or whether tests should tolerate the streaming state.
   - Recommendation: Set `USE_LLM_EXPLANATIONS=false` in the test environment. The existing OR pattern in `training.spec.ts` (hasAIExplanation OR hasFallback) continues to work without modification.

---

## Validation Architecture

> `workflow.nyquist_validation` not found in `.planning/config.json` — key absent, section included for completeness per standard template but no mandatory Nyquist validation detected.

No `nyquist_validation` key in config. Standard testing approach: manual verification via `docker compose up` + smoke tests in training flow.

### Test Infrastructure
| Property | Value |
|----------|-------|
| Framework | Playwright (E2E), no backend unit tests currently |
| Config file | `mizan/frontend/e2e/` — spec files per feature |
| Quick run command | `cd mizan/frontend && npx playwright test training.spec.ts` |
| Full suite command | `cd mizan/frontend && npx playwright test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Notes |
|--------|----------|-----------|-------|
| AI-02 (enhanced) | SSE stream delivers Arabic explanation tokens to UI | E2E manual | Existing `training.spec.ts` OR pattern (hasAIExplanation \|\| hasFallback) covers this; with `USE_LLM_EXPLANATIONS=false` in CI, template path executes |
| AI-02 (enhanced) | Fallback works when Ollama unavailable | Manual smoke | Set `USE_LLM_EXPLANATIONS=false` or stop ollama service; verify template explanation appears |
| AI-02 (enhanced) | `GET /api/classify/health` returns `ollama_ready` field | Manual | `curl http://localhost:8000/api/classify/health` after `docker compose up` |

### Wave 0 Gaps
- No new test files needed — existing `training.spec.ts` E2E test covers the visible explanation card outcome with the OR pattern already in place. Update `USE_LLM_EXPLANATIONS` env var in test setup if needed.

---

## Sources

### Primary (HIGH confidence)
- Context7 `/llmstxt/ollama_llms-full_txt` — Python SDK AsyncClient, streaming, `think=True` parameter, host configuration, `think` field vs `content` field separation
- [ollama.com/library/qwen3.5:9b](https://ollama.com/library/qwen3.5:9b) — Model tag confirmation, 6.6GB size, Q4_K_M quantization
- [ollama.com/library/qwen3.5](https://ollama.com/library/qwen3.5) — Confirmed absence of `qwen3.5:8b`; available tags: 0.8b, 2b, 4b, **9b** (latest), 27b, 35b, 122b
- Existing codebase `mizan/backend/app/routers/audit.py` — Phase 09.1 SSE pattern (authoritative in-project reference)
- Existing codebase `mizan/frontend/src/lib/audit-api.ts` — Phase 09.1 frontend SSE consumer pattern

### Secondary (MEDIUM confidence)
- [DoltHub Blog: Pull-First Ollama Docker Image](https://www.dolthub.com/blog/2025-03-19-a-pull-first-ollama-docker-image/) — Entrypoint pattern: start background → wait → pull → kill → exec foreground
- [GitHub issue #9781 ollama/ollama](https://github.com/ollama/ollama/issues/9781) — Confirmed `curl` missing from ollama Docker image; `wget` is available
- [hub.docker.com/r/ollama/ollama](https://hub.docker.com/r/ollama/ollama) — Official image, named volume at `/root/.ollama`

### Tertiary (LOW confidence)
- WebSearch results for FastAPI + Ollama SSE patterns — general pattern confirmed by official sources; specific code not independently verified from a single authoritative URL

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Ollama Python SDK verified via Context7 official docs; model tag verified via ollama.com/library directly
- Architecture: HIGH — SSE patterns copied from existing Phase 09.1 codebase; Ollama streaming API confirmed via Context7
- Pitfalls: HIGH — curl absence confirmed via official GitHub issue; model tag absence confirmed via official library page; event loop blocking is standard FastAPI async knowledge
- Docker entrypoint: MEDIUM — pattern verified from DoltHub blog (credible but not official Ollama docs)

**Research date:** 2026-03-03
**Valid until:** 2026-04-03 (Ollama SDK is fast-moving; check for breaking changes if planning is delayed >2 weeks)
