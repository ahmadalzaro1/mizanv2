# Phase 4 Research — MARBERT Inference API

> Research findings from checkpoint search and technical stack analysis. Consumed by planner.

---

## Model Selection

### Primary: `amitca71/marabert2-levantine-toxic-model-v4`

| Field | Value |
|-------|-------|
| HuggingFace ID | `amitca71/marabert2-levantine-toxic-model-v4` |
| Base model | UBC-NLP/MARBERTv2 |
| Training data | Levantine Arabic toxic dataset (published on HF) |
| Labels | Binary: `normal` (0) / `toxic` (1) |
| F1 Macro | **90.82%** |
| Accuracy | 91.28% |
| Size | ~163M params, ~600-700MB on disk |
| License | Apache 2.0 |
| Mapping | `normal` -> `not_hate`, `toxic` -> `hate` (trivial 1:1) |

**Why chosen**: Best F1 of any public MARBERT hate checkpoint. Levantine dialect focus = closest to Jordanian. Binary output maps directly to our schema.

### Fallback: `Andrazp/multilingual-hate-speech-robacofi`

| Field | Value |
|-------|-------|
| HuggingFace ID | `Andrazp/multilingual-hate-speech-robacofi` |
| Base model | XLM-T (XLM-RoBERTa variant, Twitter-pretrained) |
| Training data | 5 languages including **Arabic** |
| Labels | Binary: `0` (not-offensive) / `1` (offensive) |
| Arabic F1 | **87.04%** |
| Size | ~560M params, ~1.1GB on disk |
| License | MIT |
| Mapping | `0` -> `not_hate`, `1` -> `hate` (trivial 1:1) |

**Why chosen**: Only XLM-R model with published Arabic F1. Twitter-pretrained = good for social media. Handles code-mixed natively.

**Note**: Detects "offensive" (broader) not "hate" (narrower). May over-flag. Acceptable for fallback role.

### Runner-up (not selected): `Hate-speech-CNERG/dehatebert-mono-arabic`

mBERT-based, F1 ~87.8%, 214 downloads/month (highest adoption). Useful as future validation baseline but not XLM-RoBERTa architecture.

---

## Technical Stack

### Dependencies

| Package | Version | Notes |
|---------|---------|-------|
| Python | 3.12 | Native ARM64 build required |
| torch | 2.5+ | MPS support mature at this version |
| transformers | 4.49+ | Use `HF_HOME` not deprecated `TRANSFORMERS_CACHE` |
| accelerate | latest | `device_map="auto"` works with MPS now |

### MPS (Metal Performance Shaders)

- Detection: `torch.backends.mps.is_available()` -> `torch.device("mps")`, else CPU
- **FP16 NOT supported** on MPS — use FP32 (default)
- **Quantization NOT supported** on MPS — skip bitsandbytes/GPTQ
- Set `PYTORCH_ENABLE_MPS_FALLBACK=1` for ops not yet on MPS
- Warmup inference at startup eliminates first-run Metal shader compilation penalty

### Performance (BERT-base, single text, Apple Silicon)

| Device | Short text (~128 tokens) | Max length (512 tokens) |
|--------|--------------------------|-------------------------|
| CPU (M-series) | 20-50 ms | 50-150 ms |
| MPS (M2/M3/M4) | 8-40 ms | 40-80 ms |

**3-second target is trivially achievable.** Even worst-case CPU is ~150ms = 20x headroom.

### FastAPI Integration Pattern

- **Model loading**: Use lifespan context manager (replaces deprecated `@app.on_event`)
- **Endpoint type**: Use `def` (not `async def`) — FastAPI auto-runs in threadpool
- **Thread safety**: PyTorch inference is thread-safe in `model.eval()` + `torch.inference_mode()`
- **Startup warmup**: Run dummy inference during lifespan to pre-compile kernels

### Model Caching

- Default cache: `~/.cache/huggingface/hub/`
- Environment variable: `HF_HOME` (set in `.env` and docker-compose)
- Docker volume: `~/.cache/huggingface:/huggingface` + `HF_HOME=/huggingface`
- Total cache size: MARBERT (~700MB) + XLM-R (~1.1GB) = ~1.8GB

---

## Key Risks

1. **MPS instability on macOS 26**: Known issue (pytorch#167679). CPU fallback is the safety net.
2. **XLM-R memory**: 560M params = ~2.2GB in FP32 memory. If Apple Silicon has <8GB unified memory, skip XLM-R (CONTEXT.md says this is OK).
3. **No OSACT winners released weights**: Best competition models are papers-only. Our chosen checkpoint (F1=90.82%) is competitive regardless.

---

*Created: 2026-03-02*
*Sources: HuggingFace model hub, PyTorch docs, Apple Metal docs, arxiv 2510.18921v1*
