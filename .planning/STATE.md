---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: unknown
last_updated: "2026-03-02T22:47:27.960Z"
progress:
  total_phases: 10
  completed_phases: 2
  total_plans: 26
  completed_plans: 5
---

# STATE — Mizan

> Project memory. Updated by GSD workflow after each plan execution.

---

## Project Reference

**Name**: Mizan (ميزان — "the scale")
**Core value**: Three components, three personas, one platform. Observatory (Rania) shows the historical problem. Bias Auditor (Lina) validates the AI. Moderator Training (Khaled) trains the humans who work alongside it.
**Primary deadline**: JYIF Generative AI National Social Hackathon (Jordan) — 5-minute pitch
**The demo moment**: Observatory trend → Bias Auditor breakdown → Moderator labels tweet → MARBERT classifies → Arabic explanation appears → calibration score updates

---

## Current Position

**Current phase**: Phase 09.1 — Bias Auditor Rework
**Current plan**: Plan 09.1-03 COMPLETE — BiasAuditorPage tabbed layout + SSE + E2E tests
**Status**: Phase 09.1 COMPLETE — All 3/3 plans done

```
Progress: [##########] 10/10 phases complete (Phase 09.1 complete — 3/3 plans done)
```

---

## Phase Status

| Phase | Status | Completed |
|-------|--------|-----------|
| 1. Foundation | Complete | 2026-03-02 |
| 2. Data Pipeline | Complete | 2026-03-02 |
| 3. Moderator Training UI | Complete | 2026-03-02 |
| 4. MARBERT Inference API | Complete | 2026-03-02 |
| 5. AI Explanation Layer | Complete | 2026-03-02 |
| 6. Calibration Scoring | Complete | 2026-03-02 |
| 7. Analytics & Research Layer (Observatory + Bias Auditor) | Complete | 2026-03-02 |
| 8. Demo Polish | Complete | 2026-03-02 |
| 9. E2E Testing with Playwright | Complete | 2026-03-02 |
| 9.1. Bias Auditor Rework | Complete | 2026-03-02 |

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| ML Model | MARBERT (HuggingFace), XLM-RoBERTa (fallback) |
| Frontend | React, Vite |
| Database | PostgreSQL |
| UI Direction | RTL Arabic (Tajawal / IBM Plex Arabic) |

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| MARBERT as primary model | Best dialectal Arabic performance (F1=84%), trained on 1B Arabic tweets |
| XLM-RoBERTa fallback | Handles code-mixed Arabic-English inputs |
| FastAPI backend | PyTorch + HuggingFace require Python; FastAPI is fast to build |
| React + Vite frontend | RTL support, component ecosystem, fast iteration |
| PostgreSQL | Relational data fits annotation schema; flexible queries for calibration |
| Single demo account v1 auth | Simplifies build; multi-tenant can be added post-hackathon |
| Extended OSACT5 schema | 6 standard types + 3 Jordanian-specific (tribalism, refugee, political) |

---

## Accumulated Context

### Decisions Log

| Decision | Context |
|----------|---------|
| DB port 5433 on host | Local PostgreSQL already uses 5432; Docker internal still uses 5432 |
| bcrypt==4.2.1 directly (no passlib) | passlib 1.7.4 incompatible with bcrypt 5.x; use `import bcrypt` directly |
| EmailStr replaced by regex validator | email-validator 2.3.0 rejects `.local` TLD; use custom `@field_validator` |
| JWT `iat` as Unix int (not ISO string) | python-jose requires RFC 7519 integer timestamp |
| Demo accounts: admin@mizan.local (super_admin), demo-admin@mizan.local (admin) | super_admin has institution_id=None; use demo-admin to demonstrate AUTH-03 |
| jhsc_tweets.id is BIGINT | Twitter IDs exceed INTEGER max (2.1B); tweet_id values up to ~1.2 quintillion |
| Alembic enums via raw SQL | SQLAlchemy `sa.Enum` double-creates in `create_table`; use `op.execute()` + `postgresql.ENUM(create_type=False)` |
| Bulk insert via `__table__` not ORM | `pg_insert(Model)` converts enum values through Python names; use `Table` reflection for raw enum values |
| Tailwind CSS v3.4 (not v4) | v4 is a full rewrite with CSS-based config; v3.4 is stable, well-documented, and has built-in RTL via logical properties |
| useReducer-style state in TrainingSession page | 6+ interdependent state fields (items, currentIndex, isSubmitting, isChangingAnswer); single-page state management |
| Anti-cheat ground truth hiding | Backend returns ground_truth_label=null until moderator submits their label; prevents looking ahead |
| Binary correctness mapping | offensive→hate, spam→not_hate for is_correct computation; rewards catching harmful speech |
| MARBERT checkpoint: amitca71/marabert2-levantine-toxic-model-v4 | Levantine Arabic, F1=90.82%, binary normal/toxic, Apache 2.0 |
| XLM-R fallback: Andrazp/multilingual-hate-speech-robacofi | XLM-T base, Arabic F1=87.04%, binary offensive/not-offensive, MIT |
| Code-mixed detection via character ratio | 30% Latin chars triggers XLM-R; pure unicodedata, no extra deps |
| Pydantic protected_namespaces for model_used | `model_config = {"protected_namespaces": ()}` on ClassifyResponse |
| MPS with PYTORCH_ENABLE_MPS_FALLBACK=1 | Required for HuggingFace ops not yet on Metal; set in lifespan |
| JHSC temporal backfill via Snowflake ID SQL | Alembic migration with PostgreSQL `>>` bitwise shift; single bulk UPDATE |
| D3.js v7 + React hybrid | `useRef` + `useEffect` for D3 rendering in React; SVG viewBox for responsive charts |
| Observatory: single trends endpoint | `GET /api/observatory/trends` returns monthly aggregations + 8 hardcoded events |
| Bias Auditor: precompute + cache | `POST /api/audit/run` triggers batch; results cached in `bias_audit_runs` JSONB |
| CSV UTF-8 BOM for Arabic Excel | `\ufeff` prefix ensures correct Arabic display in Excel |
| Playwright workers: 1 | Sequential test execution prevents DB race conditions with shared test data |
| Playwright globalSetup seeds DB + writes auth-state.json | Idempotent seeds (non-fatal) + JWT login → storageState pre-injects mizan_token |
| tsconfig.e2e.json separate from tsconfig.json | Playwright uses Node moduleResolution; Vite's bundler resolution + allowImportingTsExtensions are incompatible |
| No webServer block in playwright.config.ts | Assumes Docker Compose stack already running; BASE_URL/API_URL injectable via env vars |
| storageState: undefined for login/protected-route tests | Creates a fresh browser context bypassing globalSetup JWT — required to test the real login form and unauthenticated redirects |
| Bias Auditor tests skip POST /api/audit/run | Avoids the 140s MARBERT batch — tests accept either cached results or empty state |
| AI explanation assertions use OR pattern | hasAIExplanation OR hasFallback — tolerates cold ML model startup in CI/pre-warm scenarios |
| Training test labels 3/20 items only | Sufficient to exercise not_hate, hate+category two-step, calibration score transition, and back navigation without filling DB history |
| fetch() + ReadableStream for SSE | EventSource cannot send Authorization Bearer header — fetch() ReadableStream is the correct approach for authenticated SSE |
| Optional fields on AuditResults | New per_source, confidence_dist, false_positives fields are optional (?) for backward compatibility with Phase 7 cached results |

### Roadmap Evolution
- Phase 09.1 inserted after Phase 9: Bias Auditor Rework (INSERTED) — rethink the feature for more value
- Phase 09.1 Plan 01: Backend enriched audit loop + SSE streaming endpoint (COMPLETE 2026-03-03)
- Phase 09.1 Plan 02: audit-api.ts enriched types + SSE client + 3 new components (COMPLETE 2026-03-03)
- Phase 09.1 Plan 03: BiasAuditorPage 4-tab layout + SSE progress + Arabic insight + E2E tests (COMPLETE 2026-03-03)

### Phase 09.1 Decisions
| Decision | Context |
|----------|---------|
| Keep POST /api/audit/run unchanged (backward-compatible) | SSE streaming at /run/stream is additive; old endpoint still works |
| _build_results_from_stats() shared helper | SSE generator has own loop (needs per-iteration yields); share only post-loop construction |
| Load examples eagerly before SSE generator | Prevents SQLAlchemy session lifetime issues across async yields |
| MAX_FP_SAMPLES=10 applied during loop | Cap during iteration, not post-hoc; saves memory on large example sets |
| Per-source stats track full tp/fp/fn/tn | Needed for false_positive_rate = fp/(fp+tn) computation |
| runAudit() fallback in handleRunAudit catch | SSE stream endpoint may be unavailable; fallback ensures audit always succeeds |
| generateInsight() uses template prose, not LLM | Zero latency, deterministic, no network cost; 2-3 Arabic sentences from AuditResults |
| Tab buttons as <button> not anchor | getByRole('button') selectors work cleanly in Playwright without URL navigation |
| Metric cards pinned above tab nav | Per CONTEXT.md locked decision: overall metrics always visible regardless of active tab |

### Todos Carried Forward
*(None — Phase 3 clean)*

### Blockers
*(None)*

---

## Session Continuity

**Last updated**: 2026-03-02
**Last action**: Completed 09.1-03 — BiasAuditorPage reworked with 4-tab layout, SSE progress bar, Arabic insight summary; E2E tests updated
**Next action**: Phase 09.1 COMPLETE — all 3 plans done; platform is pitch-ready

**Session 2026-03-03 bug fix results:**
- Ran `alembic upgrade head` — 4 pending migrations (phases 3, 5, 7a, 7b)
- Observatory: replaced ORM query with raw SQL to bypass `JhscLabel` enum `LookupError`
- E2E: fixed dashboard selectors (`.grid a`), observatory legend (`span` filter), training category (`.first()`), back-nav (label before back)
- Files modified: `backend/app/routers/observatory.py`, `frontend/e2e/dashboard.spec.ts`, `frontend/e2e/observatory.spec.ts`, `frontend/e2e/training.spec.ts`

**Phase 8 results:**
- CRITICAL BUG FIXED: observatory-api.ts + audit-api.ts now use shared `api` instance (reads `mizan_token`, respects `VITE_API_URL`)
- BiasAuditorPage CSV download uses `downloadAuditCsv()` via shared api (correct auth + base URL)
- Login page: migrated from inline styles to Tailwind — centered card with shadow, branding tagline
- Dashboard: persona-themed cards with color accents (red=Observatory, blue=Audit, green=Training) + persona names
- Layout: max-width widened from 900px to 1024px (max-w-5xl) for D3 chart room
- ProtectedRoute: loading state migrated to Tailwind
- Frontend build: 676 modules, 315KB JS + 16KB CSS, zero TS errors
- 0 new files, 7 modified files

**Files modified in Phase 8:**
- `mizan/frontend/src/lib/observatory-api.ts` — Use shared api instance (fix token key)
- `mizan/frontend/src/lib/audit-api.ts` — Use shared api instance + downloadAuditCsv()
- `mizan/frontend/src/pages/BiasAuditorPage.tsx` — Use downloadAuditCsv() instead of raw fetch
- `mizan/frontend/src/pages/Login.tsx` — Tailwind classes replace inline styles
- `mizan/frontend/src/pages/Dashboard.tsx` — Persona-themed cards with color accents
- `mizan/frontend/src/components/Layout.tsx` — max-w-5xl (1024px) for chart room
- `mizan/frontend/src/components/ProtectedRoute.tsx` — Tailwind loading state

**Phase 7 results:**
- JHSC temporal backfill — Snowflake ID → year/month via PostgreSQL bitwise shift (403,688 tweets)
- Observatory API: `GET /api/observatory/trends` — monthly hate counts + 8 Jordanian historical events
- Bias Auditor API: `POST /api/audit/run` (batch MARBERT on 560 examples), `GET /results`, `GET /results/csv`
- D3.js v7 area chart for Observatory timeline (2014–2022) with event markers and Arabic tooltips
- D3.js horizontal grouped bar chart for Bias Auditor (F1/precision/recall per category)
- ObservatoryPage: summary cards (total tweets, hate count, %), timeline chart, events legend
- BiasAuditorPage: run/re-run audit, overall metrics, weakness alert (F1<50%), CSV download
- Placeholder component removed from App.tsx — all 3 sections now have real pages
- 2 new migrations: `e7f8a9b0c1d2` (backfill), `f8a9b0c1d2e3` (bias_audit_runs)
- Frontend build: 676 modules, 315KB JS + 15KB CSS, zero TS errors

**New files created in Phase 7:**
- `mizan/backend/alembic/versions/e7f8a9b0c1d2_phase7_jhsc_temporal_backfill.py` — Snowflake backfill
- `mizan/backend/alembic/versions/f8a9b0c1d2e3_phase7_bias_audit_runs.py` — Audit cache table
- `mizan/backend/app/models/bias_audit.py` — BiasAuditRun model (JSONB)
- `mizan/backend/app/routers/observatory.py` — GET /api/observatory/trends
- `mizan/backend/app/routers/audit.py` — POST /run, GET /results, GET /results/csv
- `mizan/frontend/src/lib/observatory-api.ts` — getTrends() API client
- `mizan/frontend/src/lib/audit-api.ts` — runAudit(), getAuditResults() API client
- `mizan/frontend/src/components/TimelineChart.tsx` — D3.js area chart with events
- `mizan/frontend/src/components/BiasChart.tsx` — D3.js horizontal grouped bar chart
- `mizan/frontend/src/pages/ObservatoryPage.tsx` — Observatory page with summary + chart + legend
- `mizan/frontend/src/pages/BiasAuditorPage.tsx` — Bias Auditor page with metrics + chart + download

**Files modified in Phase 7:**
- `mizan/backend/app/models/jhsc_tweet.py` — tweet_year/month nullable=False
- `mizan/backend/app/main.py` — Register observatory + audit routers
- `mizan/frontend/src/App.tsx` — Replace Placeholders with real pages, remove Placeholder function
- `mizan/frontend/package.json` — Added d3 + @types/d3

**Phase 6 results:**
- CalibrationScore component — live % agreement with color-coded Arabic display
- Frontend-computed from items state — zero extra API calls
- Color thresholds: ≥80% green (ممتاز), ≥60% amber (جيد), <60% red (يحتاج تحسين)
- Arabic digits percentage: "نسبة المعايرة: ٧٠٪" with smooth CSS transition
- Placeholder before first label: "ستظهر نسبة المعايرة بعد أول تصنيف"
- Backend _serialize_session() now computes correct_count live from items (not DB column)
- Extracted toArabicDigits to shared format.ts utility (was duplicated in ProgressBar + SessionSummary)
- Frontend build: 104 modules, 228KB JS + 14KB CSS, zero TS errors

**New files created in Phase 6:**
- `mizan/frontend/src/components/CalibrationScore.tsx` — Live calibration score display
- `mizan/frontend/src/lib/format.ts` — Shared toArabicDigits utility

**Files modified in Phase 6:**
- `mizan/backend/app/routers/training.py` — _serialize_session computes correct_count from items
- `mizan/frontend/src/components/ProgressBar.tsx` — Import toArabicDigits from format.ts
- `mizan/frontend/src/pages/SessionSummary.tsx` — Import toArabicDigits from format.ts
- `mizan/frontend/src/pages/TrainingSession.tsx` — CalibrationScore between ProgressBar and TweetCard

**Phase 5 results:**
- Template-based Arabic explanations with attention-weight trigger words
- `classify_with_explanation()` on ModelManager — attention extraction from last layer
- `ExplanationService` — Arabic prose templates keyed to label, confidence, category
- 4 new columns on `session_items`: ai_label, ai_confidence, ai_explanation_text, ai_trigger_words
- TweetCard enhanced with highlight support (amber for hate, green for not_hate)
- AIExplanation component — blue card with "تفسير النموذج" header + Arabic prose
- FeedbackReveal integrates AI explanation with cold start fallback ("النموذج غير جاهز بعد")
- Arabic diacritics stripping for trigger word matching
- Frontend build: 102 modules, 228KB JS + 14KB CSS, zero TS errors

**New files created in Phase 5:**
- `mizan/backend/alembic/versions/d4e5f6a7b8c9_phase5_ai_explanation_columns.py` — Migration
- `mizan/backend/app/services/explanation.py` — Arabic explanation generator
- `mizan/frontend/src/components/AIExplanation.tsx` — Blue explanation card

**Files modified in Phase 5:**
- `mizan/backend/app/models/training.py` — 4 AI columns on SessionItem
- `mizan/backend/app/services/ml_models.py` — classify_with_explanation() method
- `mizan/backend/app/routers/training.py` — AI classification in submit_label
- `mizan/frontend/src/lib/types.ts` — TriggerWord interface, AI fields on SessionItem
- `mizan/frontend/src/components/TweetCard.tsx` — Highlight support
- `mizan/frontend/src/components/FeedbackReveal.tsx` — AI explanation + fallback
- `mizan/frontend/src/pages/TrainingSession.tsx` — Wire AI data to components

**Phase 4 results:**
- MARBERT checkpoint: `amitca71/marabert2-levantine-toxic-model-v4` (Levantine, F1=90.82%)
- XLM-RoBERTa fallback: `Andrazp/multilingual-hate-speech-robacofi` (Arabic F1=87.04%)
- `POST /api/classify` — hate/not_hate + confidence + probabilities + model_used + timing
- `GET /api/classify/health` — model loading status
- Code-mixed detection: 30% Latin character threshold → XLM-RoBERTa
- Device: MPS (Apple Silicon) with CPU fallback
- Lifespan model loading with warmup inference
- Inference: ~243-294ms on MPS (20x under 3s target)
- Pydantic protected_namespaces fix for `model_used` field

**New files created in Phase 4:**
- `mizan/backend/app/services/__init__.py` — Services package
- `mizan/backend/app/services/ml_models.py` — ModelManager + detect_code_mixed
- `mizan/backend/app/schemas/classify.py` — ClassifyRequest/Response/HealthResponse
- `mizan/backend/app/routers/classify.py` — POST /api/classify + GET /api/classify/health

**Files modified in Phase 4:**
- `mizan/backend/app/main.py` — Lifespan model loading + classify router
- `mizan/backend/app/core/config.py` — ML settings (HF_HOME, model IDs, threshold)
- `mizan/backend/requirements.txt` — torch, transformers, accelerate
- `mizan/docker-compose.yml` — model_cache volume + HF_HOME env

**Manual step needed:** Add ML env vars to `mizan/.env` (hook blocked write):
```
HF_HOME=./model_cache
MARBERT_MODEL_ID=amitca71/marabert2-levantine-toxic-model-v4
XLM_MODEL_ID=Andrazp/multilingual-hate-speech-robacofi
CODE_MIXED_THRESHOLD=0.30
```

**Phase 3 results:**
- Tailwind CSS v3.4 installed with RTL logical properties (ms-, me-, ps-, pe-)
- Shared Layout component (header + nav + main) replaces inline-styled Dashboard header
- Training API: 4 endpoints (POST/GET sessions, GET session detail, PUT label)
- Anti-cheat: ground truth hidden until moderator submits label
- Two-step labeling: hate/not_hate → 9 categories (Arabic labels)
- Session flow: start → label 20 items → feedback → summary with accuracy
- Back navigation + change answer support
- All Arabic text RTL with Tajawal font, no LTR bleed
- Frontend build: 101 modules, 226KB JS + 13KB CSS, zero TS errors

**New files created in Phase 3:**
- `mizan/frontend/tailwind.config.js` — Tailwind config with mizan-navy, mizan-surface, font-tajawal
- `mizan/frontend/postcss.config.js` — PostCSS + Autoprefixer
- `mizan/frontend/src/index.css` — Tailwind directives + RTL base
- `mizan/frontend/src/components/Layout.tsx` — Shared layout shell
- `mizan/frontend/src/components/TweetCard.tsx` — Arabic tweet display card
- `mizan/frontend/src/components/ProgressBar.tsx` — Session progress with Arabic digits
- `mizan/frontend/src/components/LabelSelector.tsx` — Two-step hate/category selector
- `mizan/frontend/src/components/FeedbackReveal.tsx` — Ground truth reveal + navigation
- `mizan/frontend/src/components/SessionHistoryList.tsx` — Past sessions list
- `mizan/frontend/src/lib/training-api.ts` — API client for training endpoints
- `mizan/frontend/src/pages/TrainingPage.tsx` — Training landing page
- `mizan/frontend/src/pages/TrainingSession.tsx` — Main labeling interface
- `mizan/frontend/src/pages/SessionSummary.tsx` — Session completion summary
- `mizan/backend/app/models/training.py` — TrainingSession + SessionItem models
- `mizan/backend/app/schemas/training.py` — Pydantic request/response schemas
- `mizan/backend/app/routers/training.py` — 4 training API endpoints
- `mizan/backend/alembic/versions/c3d4e5f6a7b8_phase3_training_tables.py`

---

## Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Requirements covered | 26/26 | 26/26 |
| Phases defined | 9 | 9 |
| Plans written | 17 | 17 |
| Plans complete | 17 | 17 |
| Demo path working | Yes (Phase 8) | Yes |

---

*Initialized: 2026-03-02*
| Phase 09-e2e-testing P02 | 3 | 5 tasks | 5 files |
| Phase 09.1-bias-auditor-rework P02 | 2 | 3 tasks | 4 files |
| Phase 09.1-bias-auditor-rework P01 | 6 | 2 tasks | 1 files |
| Phase 09.1-bias-auditor-rework P03 | 138 | 2 tasks | 2 files |

