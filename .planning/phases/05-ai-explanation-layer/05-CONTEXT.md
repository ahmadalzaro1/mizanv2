# Phase 5 Context — AI Explanation Layer

> Decisions captured via discuss-phase on 2026-03-02.
> These decisions are LOCKED — downstream agents should not re-ask.

---

## Phase Boundary

**Goal**: After a moderator submits a label, the platform displays an Arabic-language explanation of the model's reasoning.
**Requirements**: AI-02, TRAIN-03, TRAIN-04
**Depends on**: Phase 3 (Training UI) ✅, Phase 4 (MARBERT API) ✅

**NOT in scope**: Calibration scoring (Phase 6), LLM-based explanations, model retraining.

---

## Decisions

### 1. Explanation Generation Method

**Decision**: Hybrid — template-based Arabic prose + keyword extraction from attention weights.

- Pre-written Arabic sentence templates keyed to: label (hate/not_hate), confidence range, and hate category
- Extract top 2-3 words from the tweet using MARBERT attention weights (highest attention scores from the last layer)
- For not-hate classifications, highlight safe signal words too (green highlights)
- No external API calls (no LLM). Fully offline, zero cost, ~50ms added latency

### 2. Explanation Content & Tone

**Decision**: One educational sentence per classification.

- **Length**: One sentence. E.g. "صنّف النموذج هذا المحتوى كخطاب كراهية عنصري بثقة عالية، حيث رصد كلمات مؤثرة مثل «...» و«...»"
- **Tone**: Educational — like a teacher explaining to a student. Warm, instructive
- **Hate category**: Always mentioned when label is hate. Maps to the 9-category schema (عنصرية، ديني، عشائري, etc.)
- **Confidence**: Expressed as Arabic phrases, NOT percentages:
  - `>90%` → بثقة عالية
  - `70-90%` → بثقة متوسطة
  - `<70%` → بثقة منخفضة
- **Model name**: Hidden. Non-technical moderators don't need to know MARBERT vs XLM-R
- **Trigger words**: Quoted in «guillemets» within the sentence

### 3. Classification Timing & Persistence

**Decision**: Classify at label submission time. Store results in DB.

- **When**: When moderator clicks submit on their label, the backend calls `ModelManager.classify()` AND extracts attention weights in the same request
- **Persistence**: Save AI label, confidence, explanation text, and trigger words to the `session_items` table (new columns). Needed for Phase 6 calibration and session history review
- **Cold start fallback**: If model not loaded, show the normal correct/incorrect feedback WITHOUT the AI explanation section. Display note: "النموذج غير جاهز بعد"
- **Performance budget**: ~300ms total (250ms classify + 50ms attention extraction). Well under 3s target

### 4. UI Placement & Display

**Decision**: Explanation appears below feedback cards, above navigation. TweetCard gets enhanced with highlights.

**Layout order after label submission:**
1. ProgressBar (unchanged)
2. TweetCard — enhanced with highlighted trigger words (colored backgrounds):
   - Hate triggers: amber/orange background
   - Safe signals: green background
3. Correct/Incorrect banner (existing)
4. Your answer card (existing)
5. Correct answer card (existing)
6. **NEW: تفسير النموذج card** — light blue background (bg-blue-50), distinct border, small AI icon + header "تفسير النموذج", containing the one-sentence Arabic explanation
7. Navigation buttons (existing)

**Revisit behavior**: Always show the explanation when moderator navigates back to a previously labeled item (data is persisted in DB)

**Not-hate case**: Same layout. Green highlights on safe words. Explanation says something like: "صنّف النموذج هذا المحتوى كمحتوى آمن بثقة عالية، حيث لم يرصد مؤشرات على خطاب كراهية"

---

## Code Context (from codebase scout)

### Backend integration points
- `mizan/backend/app/services/ml_models.py` — `ModelManager.classify()` returns label, confidence, probabilities. Needs new method to extract attention weights
- `mizan/backend/app/routers/classify.py` — existing standalone classify endpoint (Phase 5 doesn't use this directly; classification happens inside the training label submission flow)
- `mizan/backend/app/routers/training.py` — `submit_label()` at line 158 is where classification + explanation generation should be triggered
- `mizan/backend/app/schemas/classify.py` — `ClassifyResponse` schema for reference

### Frontend integration points
- `mizan/frontend/src/components/FeedbackReveal.tsx` — add the AI explanation card section below existing feedback
- `mizan/frontend/src/components/TweetCard.tsx` — add optional `highlights` prop for colored word backgrounds
- `mizan/frontend/src/pages/TrainingSession.tsx` — pass AI explanation data through to FeedbackReveal and TweetCard

### Database changes needed
- `session_items` table needs new columns: `ai_label`, `ai_confidence`, `ai_explanation_text`, `ai_trigger_words` (JSONB array)

### Existing patterns to follow
- Arabic label maps already exist in `FeedbackReveal.tsx` (LABEL_AR, HATE_TYPE_AR) — reuse for explanation templates
- RTL + Tailwind + font-tajawal pattern established in all Phase 3 components
- Anti-cheat pattern: ground truth hidden until moderator submits — AI explanation follows same timing (only shown after submission)

---

## Deferred Ideas

*(None captured during discussion)*

---

*Created: 2026-03-02*
