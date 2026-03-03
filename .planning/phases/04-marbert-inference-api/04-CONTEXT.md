# Phase 4 Context — MARBERT Inference API

> Decisions from discuss-phase session. Downstream agents: use these as constraints, not suggestions.

---

## Phase Boundary

**Goal**: The backend can classify any Arabic text using MARBERT and return a result fast enough for a live demo.

**Requirements**: AI-01, AI-03, AI-04

**Success Criteria**:
1. POST Arabic text → hate/not-hate prediction + confidence (0–1)
2. Response within 3 seconds for single text
3. Code-mixed Arabic-English → XLM-RoBERTa fallback with valid classification

**NOT in scope**: Explanation layer (Phase 5), calibration scoring (Phase 6), bias auditor evaluation (Phase 7). This phase delivers the classify endpoint only.

---

## Decisions

### 1. Model Readiness Strategy

| Decision | Detail |
|----------|--------|
| **Approach** | Pre-fine-tuned checkpoints from HuggingFace for BOTH models |
| **MARBERT** | Find a hate-speech-fine-tuned MARBERT checkpoint (e.g., trained on OSACT, HSAB, or similar Arabic hate corpora) |
| **XLM-RoBERTa** | Find a hate-speech-fine-tuned XLM-RoBERTa checkpoint for multilingual/code-mixed input |
| **Label mapping** | Acceptable — map checkpoint output labels to our schema (hate/not_hate). Pick best accuracy regardless of native label names |
| **Fine-tuning** | NOT doing our own fine-tuning. Use pre-trained checkpoints as-is |
| **Zero-shot** | NOT using zero-shot pipelines. Pre-fine-tuned models are far more accurate |

**Researcher action**: Search HuggingFace for best available Arabic hate speech MARBERT and XLM-RoBERTa checkpoints. Evaluate by: F1 score, training data overlap with our datasets, label schema compatibility.

### 2. Code-Mixed Detection

| Decision | Detail |
|----------|--------|
| **Method** | Character script ratio (Arabic vs Latin characters) |
| **Threshold** | 30% Latin characters triggers XLM-RoBERTa fallback |
| **Implementation** | Simple function — count Unicode Arabic block chars vs Latin block chars, compute ratio |
| **No extra deps** | No language detection library needed. Pure Unicode character analysis |

**Logic**:
```
latin_ratio = count(Latin chars) / count(all alphabetic chars)
if latin_ratio >= 0.30 → route to XLM-RoBERTa
else → route to MARBERT
```

### 3. Demo Laptop Constraints

| Decision | Detail |
|----------|--------|
| **Target hardware** | MacBook with Apple Silicon (M1/M2/M3) |
| **GPU acceleration** | Use MPS (Metal Performance Shaders) if available, fall back to CPU |
| **Model loading** | Download on first server startup, cache in Docker volume / local directory |
| **Memory priority** | MARBERT is primary. If memory is tight, load MARBERT only and skip XLM-RoBERTa |
| **Lazy vs eager** | Eager load at startup — models must be warm before first request |
| **Health endpoint** | `GET /api/classify/health` — returns loaded models, memory usage, warm-up status |

**NOT doing**: Baking models into Docker image (too large). NOT using ONNX/quantization (adds complexity for hackathon).

### 4. API Response Shape

| Decision | Detail |
|----------|--------|
| **Endpoint** | `POST /api/classify` |
| **Input** | Single text string (no batch mode) |
| **Auth** | Required (JWT, same as existing endpoints) |
| **Response format** | Rich — includes label, confidence, both probabilities, model_used, processing_time_ms |

**Response schema**:
```json
{
  "label": "hate",
  "confidence": 0.87,
  "probabilities": {
    "hate": 0.87,
    "not_hate": 0.13
  },
  "model_used": "marbert",
  "processing_time_ms": 342
}
```

**Request schema**:
```json
{
  "text": "Arabic text to classify"
}
```

**Error cases**:
- Empty text → 422 validation error
- Model not loaded → 503 with message
- Classification timeout → 504

---

## Code Context (Existing Integration Points)

| File | Relevance |
|------|-----------|
| `mizan/backend/app/main.py` | Register new `classify` router here |
| `mizan/backend/app/routers/training.py` | Phase 5 will call classify from label submission flow |
| `mizan/backend/app/models/content_example.py` | `ContentLabel` enum (hate/offensive/not_hate/spam) — classify API maps to binary hate/not_hate |
| `mizan/backend/app/core/deps.py` | `get_current_user` dependency for auth |
| `mizan/backend/requirements.txt` | Needs: torch, transformers, accelerate (no ML deps yet) |
| `docker-compose.yml` | May need model cache volume mount |

**New files expected**:
- `mizan/backend/app/routers/classify.py` — API endpoint
- `mizan/backend/app/services/ml_models.py` — Model loading, inference, language detection
- `mizan/backend/app/schemas/classify.py` — Pydantic request/response schemas

---

## Deferred Ideas

*(None captured — discussion stayed within phase boundary)*

---

*Created: 2026-03-02*
*Source: discuss-phase session, Phase 4*
