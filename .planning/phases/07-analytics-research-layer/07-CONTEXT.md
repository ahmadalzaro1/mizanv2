# Phase 7 Context — Analytics & Research Layer

> Decisions derived from codebase analysis and research on 2026-03-02.

---

## Phase Boundary

**Goal**: The Observatory shows 8 years of Jordanian hate speech trends. The Bias Auditor shows where MARBERT fails by category. Both are accessible to researchers and policy users.
**Requirements**: OBS-02, OBS-03, BIAS-01, BIAS-02, BIAS-03
**Depends on**: Phase 2 (Data Pipeline) ✅, Phase 4 (MARBERT Inference API) ✅

**NOT in scope**: PDF report generation (CSV sufficient for BIAS-03), admin dashboard views, real-time model retraining.

---

## Decisions

### 1. JHSC Temporal Backfill

**Decision**: Alembic migration with raw SQL to extract year/month from Twitter Snowflake IDs.

- 403,688 tweets with NULL `tweet_year`/`tweet_month`
- Snowflake formula: `timestamp_ms = (tweet_id >> 22) + 1288834974657`
- PostgreSQL `>>` operator handles bitwise shift natively
- Single bulk UPDATE — no Python loop needed, fast execution
- Add NOT NULL constraint after backfill to prevent future NULLs

### 2. Observatory API Design

**Decision**: Single endpoint returning monthly aggregations + historical events.

- `GET /api/observatory/trends` — returns `{monthly: [...], events: [...]}`
- Monthly: `SELECT tweet_year, tweet_month, label, COUNT(*) GROUP BY 1,2,3`
- Events: hardcoded list of 8 Jordanian historical events (2014–2022)
- Auth required but no institution scoping (JHSC data is public/shared)

### 3. Bias Auditor Strategy

**Decision**: On-demand batch inference with server-side caching.

- `POST /api/audit/run` — triggers MARBERT batch on all content_examples, stores results
- `GET /api/audit/results` — returns latest cached audit run
- `GET /api/audit/results/csv` — CSV download of per-category metrics
- New `bias_audit_runs` table: id, computed_at, results (JSONB), total_examples, duration_ms
- ~140s for 560 examples — run once per demo, cache indefinitely
- Binary mapping: hate/offensive → hate, not_hate/spam → not_hate (consistent with training)

### 4. D3.js Integration

**Decision**: D3.js v7 with React hybrid approach (useRef + useEffect).

- Install `d3` + `@types/d3` (devDep)
- D3 renders into ref-mounted SVGs — React manages component lifecycle
- Two chart components: `TimelineChart.tsx` (Observatory) and `BiasChart.tsx` (Bias Auditor)
- Responsive: SVG viewBox with dynamic width/height

### 5. Frontend Pages

**Decision**: Replace Placeholder components with real Observatory and Bias Auditor pages.

- `/observatory` → `ObservatoryPage.tsx` (timeline chart + event annotations)
- `/audit` → `BiasAuditorPage.tsx` (bar charts + CSV download)
- Remove `Placeholder` component from `App.tsx`
- Both pages have Arabic UI text with RTL layout

---

## Code Context

### Backend (existing)
- `mizan/backend/app/models/jhsc_tweet.py` — JhscTweet model with NULL tweet_year/month
- `mizan/backend/app/models/content_example.py` — ContentExample with ground_truth_label + hate_type
- `mizan/backend/app/services/ml_models.py` — ModelManager.classify() method
- `mizan/backend/app/main.py` — model_manager global, lifespan loading
- `mizan/backend/app/core/deps.py` — get_current_user, require_admin

### Frontend (existing)
- `mizan/frontend/src/App.tsx` — Placeholder components for /observatory and /audit (lines 12-19, 29-30)
- `mizan/frontend/src/pages/Dashboard.tsx` — 3-card grid linking to sections
- `mizan/frontend/src/components/Layout.tsx` — Nav with المرصد and مدقق التحيز links
- `mizan/frontend/package.json` — D3.js NOT YET INSTALLED

---

## Plan Breakdown

| Plan | Wave | Description |
|------|------|-------------|
| 7.1 | 1 | JHSC Temporal Backfill + Observatory API |
| 7.2 | 1 | Bias Auditor Backend (batch inference + metrics + CSV) |
| 7.3 | 2 | D3.js Install + Observatory Frontend (timeline chart) |
| 7.4 | 2 | Bias Auditor Frontend (bar charts + CSV download) |

Wave 1: Backend-only (parallel). Wave 2: Frontend-only (parallel, depends on Wave 1).

---

*Created: 2026-03-02*
