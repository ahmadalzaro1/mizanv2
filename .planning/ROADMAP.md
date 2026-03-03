# Roadmap — Mizan

> Mizan (ميزان) — Arabic hate speech platform with three components:
> 1. **Moderator Training** (Khaled) — AI-assisted labeling, calibration scoring
> 2. **Observatory** (Rania) — 8-year Jordanian hate speech trend analysis
> 3. **Bias Auditor** (Lina) — MARBERT fairness breakdown by hate category
>
> Hackathon: JYIF Generative AI National Social Hackathon, Jordan. 5-minute pitch.
> Demo goal: All three personas served in a single walkthrough.

---

## Phases

- [x] **Phase 1: Foundation** — Project scaffold, database schema, auth, environment setup *(complete)*
- [ ] **Phase 2: Data Pipeline** — Seed JHSC/OSACT5/L-HSAB/Let-Mi data with ground-truth labels + compute observatory metrics
- [ ] **Phase 3: Moderator Training UI** — RTL Arabic labeling interface (the demo core)
- [ ] **Phase 4: MARBERT Inference API** — Classification endpoint with confidence score
- [ ] **Phase 5: AI Explanation Layer** — Arabic-language reasoning explanation per classification
- [ ] **Phase 6: Calibration Scoring** — Per-moderator agreement tracking, live score display
- [ ] **Phase 7: Analytics & Research Layer** — Observatory trend charts + Bias Auditor breakdown
- [ ] **Phase 8: Demo Polish** — Three-persona demo path, performance tuning, pitch-ready UI
- [x] **Phase 9: E2E Testing with Playwright** — Automated end-to-end tests for three-persona demo flow (completed 2026-03-02)
- [x] **Phase 10: LLM-Powered Explanations** — Replace template-based Arabic explanations with contextual LLM explanations via local Qwen 3.5 / Ollama *(complete 2026-03-03)*
- [x] **Phase 11: Onboarding Tour** — Help-button-triggered Driver.js tour walking users through the 3 platform tools (completed 2026-03-03)
- [ ] **Phase 12: Active Learning Loop** — Uncertainty and disagreement sampling strategies for more educational training sessions

---

## Phase Details

### Phase 1: Foundation
**Goal**: A developer can run the full stack locally with authentication working and the database ready to accept data.
**Depends on**: Nothing
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04
**Success Criteria**:
  1. Running `docker compose up` starts the FastAPI backend, React frontend, and PostgreSQL without errors.
  2. A new user can register with email and password, log in, and remain logged in across browser refreshes.
  3. An institution admin can add a moderator account to their organization.
  4. A moderator who logs in only sees content and sessions scoped to their institution.
**Plans**: 4 plans — `.planning/phases/1-PLAN.md`
- Plan 1.1: Project Scaffold & Docker Compose
- Plan 1.2: Database Schema & Alembic Migrations
- Plan 1.3: FastAPI Auth API
- Plan 1.4: React Frontend Auth

---

### Phase 2: Data Pipeline
**Goal**: The database contains 100+ pre-seeded Arabic examples with ground-truth labels drawn from multiple validated datasets AND the JHSC temporal dataset is loaded and queryable for observatory use.
**Depends on**: Phase 1
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, OBS-01
**Data Sources** (confirmed + available locally — 2026-03-02):
  - **JHSC** — 302,766 Jordanian tweets (2014–2022). Labels: neutral/positive/negative/very positive. Map `negative` → hate. In `mizan/backend/data/jhsc/`.
  - **Let-Mi** — 6,603 Levantine tweets, gender hate sub-labels. Full text. In `mizan/backend/data/let-mi/`.
  - **MLMA Arabic** — 3,353 Arabic tweets, multi-label (hateful/offensive/normal) + target (gender/origin/religion/disability). Full text. In `mizan/backend/data/mlma/`.
  - **AJ Comments** — 31,692 Al Jazeera Arabic news comments. Labels: -2=hate (conf≥0.75), -1=not-hate, 0=drop (off-topic). In `mizan/backend/data/aj-comments/`.
  - **Arabic Religious (Albadi 2018)** — 5,569 tweet IDs only (no text). AraHate lexicons reserved for Phase 4. In `mizan/backend/data/arabic-religious/`.
**Label mapping**:
  - JHSC `negative` → hate; all others → not_hate
  - Let-Mi `category != none` → hate (gender_hate category)
  - MLMA `hateful*` / `abusive_hateful*` → hate; `normal*` → not_hate; target maps to category
  - AJ `languagecomment == -2` (conf ≥ 0.75) → hate; `-1` → not_hate
**Success Criteria**:
  1. Running the seed script populates the database with at least 100 examples drawn from JHSC, Let-Mi, MLMA, and AJ Comments.
  2. Each example has a ground-truth label plus a hate type (from the 9-category schema, nullable for undifferentiated examples).
  3. Each example is tagged with dialect (Jordanian/Levantine/mixed), content type, and hate category — queryable via API.
  4. JHSC temporal data (2014–2022, aggregated by month/year) is loaded into `jhsc_monthly` and queryable.
  5. An admin can trigger a CSV or JSON export of all annotations.
**Plans**: 5 plans — `mizan/.planning/phases/02-data-pipeline/PLAN.md`
- Plan 2.1: Database Schema Migration (5 new tables)
- Plan 2.2: Dataset Preparation Scripts (4 prep scripts → all_seed.json)
- Plan 2.3: Content Examples Seed Script
- Plan 2.4: JHSC Full Load Script (Snowflake ID → timestamp → monthly aggregation)
- Plan 2.5: Export API Endpoint

---

### Phase 3: Moderator Training UI
**Goal**: A moderator can open the platform, work through a training session of Arabic content, and submit labels — the full labeling loop is functional end-to-end in RTL Arabic.
**Depends on**: Phase 1, Phase 2
**Requirements**: TRAIN-01, TRAIN-02, TRAIN-05, TRAIN-07, UI-01, UI-02, UI-03
**Success Criteria**:
  1. All Arabic text renders right-to-left with Tajawal or IBM Plex Arabic font — no LTR bleed.
  2. A moderator can navigate through a sequence of 10–50 examples in the correct RTL layout.
  3. A moderator can select hate/not-hate and, when hate, choose one of the 9 categories before submitting.
  4. After submitting, the moderator can mark whether they agree or disagree with the AI classification.
  5. Platform is fully usable in Chrome, Firefox, and Safari on desktop.
**Plans**: 4 plans — `.planning/phases/03-moderator-training-ui/`
- Plan 3.1: Tailwind CSS Installation & RTL Layout Shell (Wave 1)
- Plan 3.2: Training Session Backend — Schema + API (Wave 1)
- Plan 3.3: Training Labeling Interface — Frontend Core (Wave 2)
- Plan 3.4: Session Flow & Summary — Start, Complete, History (Wave 3)

---

### Phase 4: MARBERT Inference API
**Goal**: The backend can classify any Arabic text using MARBERT and return a result fast enough for a live demo.
**Depends on**: Phase 1
**Requirements**: AI-01, AI-03, AI-04
**Success Criteria**:
  1. Posting Arabic text returns a hate/not-hate prediction and confidence score (0–1).
  2. API returns a classification response within 3 seconds for a single text input.
  3. Code-mixed Arabic-English input falls back to XLM-RoBERTa and returns a valid classification.
**Plans**: 2 plans — `.planning/phases/04-marbert-inference-api/`
- Plan 4.1: ML Dependencies & Model Service (Wave 1)
- Plan 4.2: Classify API Endpoint & Integration (Wave 2)

---

### Phase 5: AI Explanation Layer
**Goal**: After a moderator submits a label, the platform displays an Arabic-language explanation of the model's reasoning.
**Depends on**: Phase 3, Phase 4
**Requirements**: AI-02, TRAIN-03, TRAIN-04
**Success Criteria**:
  1. After label submission, the moderator sees the AI classification and confidence score.
  2. An Arabic-language explanation of the reasoning appears — natural prose, not technical output.
  3. The explanation is grammatically correct and readable by a non-technical Jordanian Arabic speaker.
**Plans**: 2 plans — `.planning/phases/05-ai-explanation-layer/`
- Plan 5.1: Backend — Schema Migration + Explanation Service (Wave 1)
- Plan 5.2: Frontend — AI Explanation Display (Wave 2)

---

### Phase 6: Calibration Scoring
**Goal**: Moderators see a live calibration score reflecting their agreement with ground-truth labels, updating after each submission.
**Depends on**: Phase 3, Phase 5
**Requirements**: TRAIN-06
**Success Criteria**:
  1. After each submission, the moderator's calibration score (% agreement with ground truth) updates immediately.
  2. The score is accurate — 7/10 correct = 70%.
**Plans**: 1 plan — `.planning/phases/06-calibration-scoring/`
- Plan 6.1: Calibration Scoring — Live Display (Wave 1)

---

### Phase 7: Analytics & Research Layer
**Goal**: The Observatory shows 8 years of Jordanian hate speech trends. The Bias Auditor shows where MARBERT fails by category. Both are accessible to researchers and policy users.
**Depends on**: Phase 2, Phase 4
**Requirements**: OBS-02, OBS-03, BIAS-01, BIAS-02, BIAS-03
**Success Criteria**:
  1. Observatory displays a timeline chart of hate speech volume (2014–2022) from JHSC, broken down by hate type.
  2. Observatory marks at least 3 real Jordanian events on the timeline (e.g., 2015 refugee influx, 2020 elections).
  3. Bias Auditor shows MARBERT's F1/precision/recall broken down by all 9 hate categories on JHSC.
  4. Bias Auditor clearly highlights which categories the model performs weakest on.
  5. A researcher can download a bias report (PDF or CSV) summarizing model performance by category.
**Plans**: 4 plans — `.planning/phases/07-analytics-research-layer/`
- Plan 7.1: JHSC Temporal Backfill + Observatory API (Wave 1)
- Plan 7.2: Bias Auditor Backend — Batch Inference + Metrics + CSV (Wave 1)
- Plan 7.3: D3.js Install + Observatory Frontend (Wave 2)
- Plan 7.4: Bias Auditor Frontend — Charts + CSV Download (Wave 2)

---

### Phase 8: Demo Polish
**Goal**: A complete, compelling 5-minute demo path works across all three personas — the platform is pitch-ready for the hackathon jury.
**Depends on**: Phase 7
**Requirements**: (no new requirements — delivers demo integration of all prior phases)
**Success Criteria**:
  1. The three-persona demo flow — Observatory (Rania) → Bias Auditor (Lina) → Moderator Training (Khaled) — completes end-to-end in under 4 minutes without errors.
  2. Platform loads the demo session in under 3 seconds on a standard laptop on Wi-Fi.
  3. All UI text, labels, and explanations are in Arabic with no broken layout or English fallback visible during the demo.
  4. A jury member watching the 5-minute pitch can follow the platform's purpose without technical explanation.
**Plans**: TBD

---

### Phase 9: E2E Testing with Playwright
**Goal**: Automated E2E tests cover the three-persona demo flow — login, dashboard, observatory, bias auditor, and training session — catching regressions before the hackathon pitch.
**Depends on**: Phase 8
**Requirements**: (no new requirements — tests validate all prior phases)
**Success Criteria**:
  1. `npx playwright test` runs all tests headless and passes.
  2. Auth flow tested: login, logout, protected route redirect.
  3. Observatory page loads trends chart without 401.
  4. Bias Auditor page loads results and CSV downloads work.
  5. Training flow: start session → label tweet → see feedback → summary.
**Plans**: 2 plans -- `.planning/phases/09-e2e-testing/`
- Plan 9.1: Playwright Infrastructure Setup (Wave 1)
- Plan 9.2: E2E Test Suite Implementation (Wave 2)

### Phase 10: LLM-Powered Explanations
**Goal:** Replace template-based Arabic explanations with contextual LLM explanations using local Qwen 3.5 via Ollama — producing richer, more natural Arabic reasoning for each classification.
**Depends on:** Phase 09.1
**Requirements**: AI-02 (enhanced)
**Success Criteria**:
  1. Ollama service added to docker-compose with Qwen 3.5 model pulled on first run.
  2. New `llm_explanation.py` service generates Arabic explanations via local Qwen 3.5.
  3. Classify and training endpoints return LLM-generated explanations instead of templates.
  4. If Ollama is unavailable, the system falls back to existing template-based explanations gracefully.
  5. Explanation quality: contextual, referencing specific words/phrases from the input text.
**Plans**: 3 plans — 2/3 complete
- Plan 10-01: Ollama Docker service + backend config + health endpoint (COMPLETE 2026-03-03)
- Plan 10-02: llm_explanation.py service + SSE endpoints for training/audit/dev (COMPLETE 2026-03-03)
- Plan 10-03: Frontend SSE client + streaming explanation UI (TODO)
**Scope**: Add Ollama to docker-compose, create `llm_explanation.py` service, wire into classify + training endpoints, fallback to templates if Ollama unavailable

---

### Phase 11: Onboarding Tour
**Goal:** Add a help-button-triggered onboarding tour using Driver.js that walks users through the 3 platform tools — reducing time-to-first-action for new users.
**Depends on:** Phase 10
**Requirements**: UI-04 (new)
**Success Criteria**:
  1. Driver.js installed and integrated into the React frontend.
  2. A help button (?) appears in the Layout navbar, visible on all authenticated pages.
  3. Clicking the help button launches a guided tour with steps for Dashboard, Training, Observatory, and Bias Auditor.
  4. Tour highlights relevant UI elements with Arabic descriptions.
  5. Tour state persists — first-time users see it automatically, returning users trigger via help button.
**Plans**: TBD — run `/gsd:plan-phase 11` to break down
**Scope**: Install driver.js, create OnboardingTour component, add help button to Layout navbar, define tour steps for Dashboard/Training/Observatory/BiasAuditor

---

### Phase 12: Active Learning Loop
**Goal:** Add uncertainty and disagreement sampling strategies to training sessions so moderators practice on the most educational examples — improving calibration faster.
**Depends on:** Phase 10
**Requirements**: TRAIN-08 (new)
**Success Criteria**:
  1. New `active_learning.py` service implements 3 sampling strategies: sequential, uncertainty, and disagreement.
  2. Migration adds `ai_confidence` column to content_examples for caching model confidence scores.
  3. Training page includes a strategy picker (dropdown) before starting a session.
  4. Uncertainty sampling selects examples where MARBERT confidence is closest to 0.5.
  5. Disagreement sampling selects examples where prior moderator labels disagree with ground truth.
  6. Sequential strategy preserves current behavior as the default.
**Plans**: TBD — run `/gsd:plan-phase 12` to break down
**Scope**: New `active_learning.py` service, `ai_confidence` column migration, strategy picker in TrainingPage, 3 strategies (sequential/uncertainty/disagreement)

---

### Phase 09.1: Bias Auditor Rework (INSERTED)

**Goal:** [Urgent work - to be planned]
**Requirements**: TBD
**Depends on:** Phase 9
**Plans:** 1/3 plans executed

Plans:
- [x] TBD (run /gsd:plan-phase 09.1 to break down) (completed 2026-03-02)

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete | 2026-03-02 |
| 2. Data Pipeline | 0/5 | Planned | - |
| 3. Moderator Training UI | 4/4 | Complete | 2026-03-02 |
| 4. MARBERT Inference API | 2/2 | Complete | 2026-03-02 |
| 5. AI Explanation Layer | 2/2 | Complete | 2026-03-02 |
| 6. Calibration Scoring | 1/1 | Complete | 2026-03-02 |
| 7. Analytics & Research Layer | 0/4 | Planned | - |
| 8. Demo Polish | 0/? | Not started | - |
| 9. E2E Testing with Playwright | 2/2 | Complete   | 2026-03-02 |
| 9.1 Bias Auditor Rework | 3/3 | Complete | 2026-03-02 |
| 10. LLM-Powered Explanations | 1/3 | Complete    | 2026-03-03 |
| 11. Onboarding Tour | 2/2 | Complete    | 2026-03-03 |
| 12. Active Learning Loop | 1/3 | In Progress|  |

---

## Coverage Map

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 1 | Pending |
| AUTH-02 | Phase 1 | Pending |
| AUTH-03 | Phase 1 | Pending |
| AUTH-04 | Phase 1 | Pending |
| DATA-01 | Phase 2 | Pending |
| DATA-02 | Phase 2 | Pending |
| DATA-03 | Phase 2 | Pending |
| DATA-04 | Phase 2 | Pending |
| OBS-01 | Phase 2 | Pending |
| TRAIN-01 | Phase 3 | Pending |
| TRAIN-02 | Phase 3 | Pending |
| TRAIN-05 | Phase 3 | Pending |
| TRAIN-07 | Phase 3 | Pending |
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 3 | Pending |
| UI-03 | Phase 3 | Pending |
| AI-01 | Phase 4 | Pending |
| AI-03 | Phase 4 | Pending |
| AI-04 | Phase 4 | Pending |
| AI-02 | Phase 5 | Pending |
| TRAIN-03 | Phase 5 | Pending |
| TRAIN-04 | Phase 5 | Pending |
| TRAIN-06 | Phase 6 | Pending |
| OBS-02 | Phase 7 | Pending |
| OBS-03 | Phase 7 | Pending |
| BIAS-01 | Phase 7 | Pending |
| BIAS-02 | Phase 7 | Pending |
| BIAS-03 | Phase 7 | Pending |
| AI-02 (enhanced) | Phase 10 | Complete |
| UI-04 | Phase 11 | Pending |
| TRAIN-08 | Phase 12 | Pending |

**Total mapped: 28/28 v1 requirements + 3 v2 requirements**

---

*Created: 2026-03-02*
*Updated: 2026-03-03 — Added phases 10-12 (LLM explanations, onboarding tour, active learning)*

**Goal:** [Urgent work - to be planned]
**Requirements**: TBD
**Depends on:** Phase 9
**Plans:** 3/3 plans complete

Plans:
- [x] TBD (run /gsd:plan-phase 09.1 to break down) (completed 2026-03-02)
