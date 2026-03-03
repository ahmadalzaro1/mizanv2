# Phase 12: Active Learning Loop - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Add 3 sampling strategies (sequential, uncertainty, disagreement) to training sessions so moderators practice on the most educational examples. Includes strategy picker UI, `ai_confidence` column migration on `content_examples`, and backend `active_learning.py` service. No new pages — modifications to existing TrainingPage and session creation flow.

</domain>

<decisions>
## Implementation Decisions

### Strategy Picker UX
- Radio cards on the Training start screen (before session creation), not a dropdown
- Strategy is locked for the session — no mid-session switching
- Sequential strategy pre-selected as default (preserves current behavior)
- Button text stays "ابدأ التدريب" regardless of selected strategy
- Strategy name shown in session summary and session history list

### Uncertainty Sampling
- Batch pre-compute MARBERT confidence on all 560 content_examples at migration/startup time
- New `ai_confidence` column on `content_examples` table (migration required)
- Select top-20 examples closest to 0.5 confidence (sort by |confidence - 0.5| ascending)
- Exclude examples already labeled by this moderator in prior sessions
- If no confidence scores exist (model never ran), disable uncertainty card with Arabic message: "يتطلب تحميل النموذج"

### Disagreement Sampling
- Definition: examples where prior moderators' labels disagree with ground truth (is_correct=false)
- Consider ALL moderators' labels across the platform, not just current user
- Rank by error rate — most incorrect labels across all sessions first, take top 20
- If no prior sessions exist, disable card with Arabic message: "يتطلب جلسة سابقة واحدة على الأقل"
- Fallback: when no moderator history exists, use AI-vs-ground-truth disagreement (pre-computed MARBERT scores)

### Strategy Labels & Arabic
- User-friendly Arabic names with one-line descriptions on each card:
  - تدريب تسلسلي — أمثلة عشوائية للتعلم الأساسي (sequential training — random examples for basic learning)
  - تدريب التحدي — أمثلة يصعب على الذكاء الاصطناعي تصنيفها (challenge training — examples the AI struggles with)
  - أمثلة مثيرة للجدل — أمثلة اختلف عليها المشرفون الآخرون (controversial examples — examples other moderators disagreed on)
- Color-coded cards: Green = sequential, Amber = uncertainty, Red = disagreement
- Subtle badge/chip at top of session page showing active strategy during training
- Strategy name visible in session summary page and session history list

### Claude's Discretion
- Exact card layout dimensions and spacing
- Icon choices for strategy cards
- Badge/chip styling during session
- Pre-compute script implementation details (batch size, error handling)
- Migration rollback strategy

</decisions>

<specifics>
## Specific Ideas

- Color coding matches existing patterns: green (safe/ممتاز from calibration), amber (warning/جيد), red (danger/يحتاج تحسين)
- Strategy cards should feel similar to the Dashboard persona cards (3 cards with color accents)
- Disabled cards should be visually distinct (greyed out) with the Arabic explanation text

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `TrainingPage.tsx`: Current start screen with "ابدأ التدريب" button — needs strategy cards added above it
- `SessionHistoryList.tsx`: Session list component — needs strategy column/badge
- `training-api.ts`: `createSession()` currently takes no params — needs `strategy` parameter
- `training.py` router: `create_session()` uses `func.random()` — needs strategy-based selection logic
- `ContentExample` model: 560 rows, needs `ai_confidence` Float column
- `SessionItem` model: already has `ai_confidence` + `is_correct` columns
- `ml_models.py` / `model_manager`: MARBERT classify available via `classify_with_explanation()`

### Established Patterns
- Tailwind CSS with RTL (ms-/me-/ps-/pe- logical properties)
- Tajawal font throughout, `font-tajawal` class
- Mizan-navy color scheme (`bg-mizan-navy`, `text-mizan-navy`)
- FastAPI routers with `Depends(get_current_user)` auth pattern
- Alembic migrations with explicit enum handling

### Integration Points
- `POST /api/training/sessions` — add `strategy` query param or body field
- `TrainingSession` model — add `strategy` column (enum: sequential/uncertainty/disagreement)
- `TrainingPage.tsx` — add card picker between heading and start button
- Session detail page — add strategy badge
- `SessionSummary.tsx` — show strategy used

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 12-active-learning*
*Context gathered: 2026-03-03*
