# Phase 3 — Moderator Training UI: Context

> Decisions locked by user discussion on 2026-03-02.
> Researcher and planner must follow these exactly — do not re-ask.

---

## A. Training Session Flow

**Auto-assign batch model.**
When a moderator navigates to `/train`, they see a "Start Training" screen. Clicking it creates a new session with 20 random unlabeled examples from `content_examples` (scoped to their institution via AUTH-04). Examples are assigned to the session and the moderator works through them one at a time.

**Session model:**
- A `training_sessions` table tracks each session (id, user_id, institution_id, created_at, completed_at)
- A `session_items` table links session → content_example with ordering and the moderator's label
- When the moderator finishes all items, `completed_at` is set

**Batch size: 20 examples per session.**
Fixed for v1. No moderator-selectable batch size.

---

## B. Labeling Interface

**Two-step labeling:**
1. Moderator sees Arabic tweet text (RTL) and selects: `hate` / `not_hate`
2. If `hate` is selected, a second step appears: choose one of the 9 hate categories (race, religion, ideology, gender, disability, social_class, tribalism, refugee_related, political_affiliation)
3. Moderator clicks "Submit" to record their label

**Arabic labels for the 9 categories:**
| English | Arabic |
|---------|--------|
| race | عنصرية |
| religion | ديني |
| ideology | أيديولوجي |
| gender | جنساني |
| disability | إعاقة |
| social_class | طبقي |
| tribalism | عشائري |
| refugee_related | لاجئين |
| political_affiliation | سياسي |

**hate / not_hate labels in Arabic:**
- hate → خطاب كراهية
- not_hate → ليس كراهية

---

## C. Post-Submit Feedback

**Show ground truth after submission.**
After the moderator submits their label, the interface reveals the dataset's ground-truth label (the "correct answer" from the expert annotations). The moderator sees whether they matched or not. This is quiz-style instant feedback.

**No AI prediction in Phase 3.**
The AI model (MARBERT) is not available until Phase 4. The "agree/disagree with AI" feature (TRAIN-05) is deferred to Phase 5 when both the AI prediction and explanation are available together.

**What Phase 3 records per item:**
- `moderator_label` (hate/not_hate)
- `moderator_hate_type` (one of 9 categories, or null if not_hate)
- `is_correct` (computed: did moderator match ground truth?)

**Binary mapping for `is_correct` computation:**
The ground truth uses 4 labels (`hate`, `offensive`, `not_hate`, `spam`), but the moderator only chooses 2 (`hate`, `not_hate`). The mapping for correctness:
- Ground truth `hate` or `offensive` → moderator `hate` is correct
- Ground truth `not_hate` or `spam` → moderator `not_hate` is correct
- Rationale: `offensive` is harmful speech, so catching it as hate is rewarded. `spam` is not harmful. May be revisited in Phase 6 (calibration scoring).

---

## D. Navigation

**Allow back navigation.**
Moderators can go back to review and change previous answers within the session. The session tracks current position, and the moderator can navigate forward/backward through the example list.

**Progress bar.**
A visual progress indicator shows current position (e.g., "7/20") and how many are labeled vs. remaining.

**Session completion.**
When all 20 examples are labeled, show a summary screen with:
- Total correct / total (e.g., "14/20 correct")
- Accuracy percentage
- Button to start a new session or return to dashboard

---

## E. Styling

**Install Tailwind CSS.**
Phase 3 introduces Tailwind CSS to the frontend. One-time setup cost that pays off for Phases 5-8.

**RTL with Tailwind:**
- Use `dir="rtl"` on root layout
- Tailwind v3.3+ has built-in RTL support via `rtl:` variant
- Font: Tajawal (already loaded via Google Fonts in index.html)

**Design direction:**
- Keep the existing color palette: `#1a1a2e` (dark navy) as primary, white backgrounds, `#f9f9f9` for surfaces
- Cards for tweet display with large Arabic text
- Big touch-friendly buttons for label selection
- Clean, minimal — this is a work tool, not a marketing site

---

## F. Backend API Endpoints (New in Phase 3)

**Training session endpoints:**
1. `POST /api/training/sessions` — Create a new session (auto-assigns 20 examples)
2. `GET /api/training/sessions/{id}` — Get session with all items
3. `PUT /api/training/sessions/{id}/items/{item_id}` — Submit/update a label for one item
4. `GET /api/training/sessions` — List moderator's sessions (with completion status)

**All endpoints require auth.** Moderators only see their own sessions (AUTH-04 scoping via institution_id).

---

## G. Database Schema (New Tables)

**`training_sessions` table:**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| institution_id | UUID | FK → institutions.id (for scoping) |
| status | ENUM | 'in_progress' / 'completed' |
| total_items | INTEGER | Always 20 for v1 |
| correct_count | INTEGER | Computed after all items labeled |
| created_at | TIMESTAMP | |
| completed_at | TIMESTAMP | NULL until complete |

**`session_items` table:**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| session_id | UUID | FK → training_sessions.id |
| content_example_id | UUID | FK → content_examples.id |
| position | INTEGER | 1-based ordering within session |
| moderator_label | ENUM | 'hate' / 'not_hate' / NULL (unlabeled) |
| moderator_hate_type | ENUM | HateType enum / NULL |
| is_correct | BOOLEAN | NULL until labeled |
| labeled_at | TIMESTAMP | NULL until labeled |

---

## H. Requirements Coverage

| Requirement | How Phase 3 Delivers It |
|-------------|------------------------|
| TRAIN-01 | Moderator views Arabic content and submits hate/not_hate label |
| TRAIN-02 | When hate selected, moderator chooses from 9 categories |
| TRAIN-05 | **Deferred to Phase 5** (needs AI model from Phase 4) |
| TRAIN-07 | Moderator navigates through 20 examples in sequence |
| UI-01 | All Arabic text renders RTL with Tajawal font, Tailwind RTL |
| UI-02 | Tested on Chrome, Firefox, Safari desktop |
| UI-03 | Arabic primary interface (English option deferred to Phase 8) |

**Note:** TRAIN-05 partially covered — the ground-truth reveal gives feedback, but the "agree/disagree with AI" interaction requires the AI (Phase 4-5).

---

## I. Code Context (What Exists)

**From Phase 1:**
- Auth: JWT login, `get_current_user` / `require_admin` deps
- Models: `User`, `Institution`, `UserRole`
- Frontend: `AuthProvider`, `useAuth()`, `api` axios instance, `ProtectedRoute`
- Routes: `/login`, `/`, `/train` (currently placeholder)

**From Phase 2:**
- Models: `ContentExample` (560 rows), `ContentLabel` enum, `HateType` enum
- Seed data: 560 examples (125 JHSC + 125 Let-Mi + 125 MLMA + 185 AJ)
- Export: `GET /api/export?format=csv|json`
- DB port: 5433 on host

**Pattern to follow:**
- Backend routers in `app/routers/` with `APIRouter(prefix=..., tags=...)`
- Pydantic schemas in `app/schemas/`
- SQLAlchemy models in `app/models/`
- Alembic migration for new tables
- Frontend pages in `src/pages/`, shared components in `src/components/`

---

## J. Decisions That Are OUT OF SCOPE for Phase 3

Do not include:
- AI classification / MARBERT inference (Phase 4)
- Arabic explanations (Phase 5)
- Agree/disagree with AI (Phase 5)
- Calibration scoring (Phase 6)
- Observatory charts (Phase 7)
- Bias Auditor (Phase 7)
- English language toggle (Phase 8)
- Admin session creation (v2 — ADMIN-02)

Phase 3 delivers: the training labeling loop end-to-end in RTL Arabic with Tailwind CSS.

---

*Written: 2026-03-02 after user discussion via /gsd:plan-phase 3*
