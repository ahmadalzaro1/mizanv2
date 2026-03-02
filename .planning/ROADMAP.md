# Roadmap — Mizan

> Mizan (ميزان) — Arabic hate speech moderator training platform.
> Hackathon deadline: JYIF Generative AI National Social Hackathon, Jordan.
> Demo goal: Show a tweet → moderator labels it → MARBERT classifies it → AI explanation appears in Arabic.

---

## Phases

- [ ] **Phase 1: Foundation** — Project scaffold, database schema, auth, environment setup
- [ ] **Phase 2: Data Pipeline** — Seed JHSC/OSACT5 data with ground-truth labels into DB
- [ ] **Phase 3: Moderator Training UI** — RTL Arabic labeling interface (the demo core)
- [ ] **Phase 4: MARBERT Inference API** — Classification endpoint with confidence score
- [ ] **Phase 5: AI Explanation Layer** — Arabic-language reasoning explanation per classification
- [ ] **Phase 6: Calibration Scoring** — Per-moderator agreement tracking, live score display
- [ ] **Phase 7: Admin Dashboard** — Institution-level analytics, session management, export
- [ ] **Phase 8: Demo Polish** — Sample data path, performance tuning, pitch-ready UI

---

## Phase Details

### Phase 1: Foundation
**Goal**: A developer can run the full stack locally with authentication working and the database ready to accept data.
**Depends on**: Nothing
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04
**Success Criteria** (what must be TRUE):
  1. Running `docker compose up` (or equivalent) starts the FastAPI backend, React frontend, and PostgreSQL instance without errors.
  2. A new user can register with email and password, then log in and remain logged in across browser refreshes.
  3. An institution admin can add a moderator account to their organization.
  4. A moderator who logs in only sees content and sessions scoped to their institution — not data from other institutions.
**Plans**: TBD

---

### Phase 2: Data Pipeline
**Goal**: The database contains 100+ pre-seeded Jordanian Arabic examples with ground-truth labels and metadata, ready for a training session.
**Depends on**: Phase 1
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04
**Success Criteria** (what must be TRUE):
  1. Running the seed script populates the database with at least 100 examples sourced from JHSC and OSACT5.
  2. Each example in the database has a ground-truth hate/not-hate label plus a hate type (from the 9-category schema).
  3. Each example is tagged with dialect (Jordanian/Levantine), content type, and hate category — queryable via the API.
  4. An admin can trigger a CSV or JSON export of all annotations and receive a valid, parseable file.
**Plans**: TBD

---

### Phase 3: Moderator Training UI
**Goal**: A moderator can open the platform, work through a training session of Arabic content, and submit labels — the full labeling loop is functional end-to-end in RTL Arabic.
**Depends on**: Phase 1, Phase 2
**Requirements**: TRAIN-01, TRAIN-02, TRAIN-05, TRAIN-07, UI-01, UI-02, UI-03
**Success Criteria** (what must be TRUE):
  1. All Arabic text renders right-to-left with Tajawal or IBM Plex Arabic font — no LTR bleed, no font fallback to Latin.
  2. A moderator can navigate through a sequence of 10–50 examples and see each tweet/comment displayed in the correct RTL layout.
  3. A moderator can select "hate" or "not hate" and, when selecting hate, choose exactly one of the 9 hate type categories before submitting.
  4. After submitting, the moderator can mark whether they agree or disagree with the AI classification.
  5. The platform is fully usable in Chrome, Firefox, and Safari on desktop without layout breakage.
**Plans**: TBD

---

### Phase 4: MARBERT Inference API
**Goal**: The backend can classify any Arabic text input using MARBERT and return a result fast enough for a live demo.
**Depends on**: Phase 1
**Requirements**: AI-01, AI-03, AI-04
**Success Criteria** (what must be TRUE):
  1. Posting Arabic text to the classification endpoint returns a hate/not-hate prediction and a confidence score (0–1).
  2. The API returns a classification response within 3 seconds for a single text input under normal load.
  3. When the input contains code-mixed Arabic-English text, the system falls back to XLM-RoBERTa and still returns a valid classification.
**Plans**: TBD

---

### Phase 5: AI Explanation Layer
**Goal**: After a moderator submits a label, the platform displays an Arabic-language explanation of why the model classified the content as it did.
**Depends on**: Phase 3, Phase 4
**Requirements**: AI-02, TRAIN-03, TRAIN-04
**Success Criteria** (what must be TRUE):
  1. After label submission, the moderator sees the AI model's classification (hate/not-hate) and its confidence score displayed on screen.
  2. Below the classification, an Arabic-language explanation of the model's reasoning appears — written in natural Arabic prose, not technical output.
  3. The explanation is readable and grammatically correct — a Jordanian Arabic speaker can understand it without technical knowledge.
**Plans**: TBD

---

### Phase 6: Calibration Scoring
**Goal**: Moderators see a live calibration score that reflects their agreement with ground-truth labels, updating after each submission.
**Depends on**: Phase 3, Phase 5
**Requirements**: TRAIN-06
**Success Criteria** (what must be TRUE):
  1. After each label submission, the moderator's calibration score (% agreement with ground truth) updates immediately on screen.
  2. The calibration score is accurate — if a moderator agrees with 7 of 10 ground-truth labels, the score shows 70%.
**Plans**: TBD

---

### Phase 7: Admin Dashboard
**Goal**: An institution admin can manage training sessions, monitor moderator performance, and download reports.
**Depends on**: Phase 2, Phase 6
**Requirements**: ADMIN-01, ADMIN-02, ADMIN-03, ADMIN-04
**Success Criteria** (what must be TRUE):
  1. The admin dashboard lists all moderators in the institution with their current calibration scores.
  2. An admin can create a new training session by selecting a content batch and assigning it to a specific moderator.
  3. The dashboard surfaces which content items have the highest moderator disagreement rate — sortable or highlighted.
  4. An admin can download a calibration report (PDF or CSV) that includes all moderator scores and session history.
**Plans**: TBD

---

### Phase 8: Demo Polish
**Goal**: A complete, compelling 3-minute demo path works flawlessly — the platform is pitch-ready for the hackathon jury.
**Depends on**: Phase 7
**Requirements**: (no new requirements — delivers the demo integration of all prior phases)
**Success Criteria** (what must be TRUE):
  1. The demo flow — open tweet, label it, see AI classification, read Arabic explanation — completes end-to-end in under 60 seconds without errors.
  2. The platform loads the demo session in under 3 seconds on a standard laptop on Wi-Fi.
  3. All UI text, labels, and explanations are in Arabic with no broken layout, missing translations, or English fallback visible during the demo path.
  4. A jury member watching the 3-minute pitch can follow what the platform does without technical explanation.
**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/? | Not started | - |
| 2. Data Pipeline | 0/? | Not started | - |
| 3. Moderator Training UI | 0/? | Not started | - |
| 4. MARBERT Inference API | 0/? | Not started | - |
| 5. AI Explanation Layer | 0/? | Not started | - |
| 6. Calibration Scoring | 0/? | Not started | - |
| 7. Admin Dashboard | 0/? | Not started | - |
| 8. Demo Polish | 0/? | Not started | - |

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
| ADMIN-01 | Phase 7 | Pending |
| ADMIN-02 | Phase 7 | Pending |
| ADMIN-03 | Phase 7 | Pending |
| ADMIN-04 | Phase 7 | Pending |

**Total mapped: 26/26 v1 requirements**

---

*Created: 2026-03-02*
