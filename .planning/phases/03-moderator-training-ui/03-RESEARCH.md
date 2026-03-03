# Phase 3: Moderator Training UI - Research

**Researched:** 2026-03-02
**Domain:** Tailwind CSS RTL setup, FastAPI pagination, React labeling UI state management
**Confidence:** HIGH

## Summary

Phase 3 introduces Tailwind CSS to the existing Vite + React + TypeScript frontend, builds a sequential Arabic labeling interface, and adds four backend API endpoints for training sessions. The research covers five domains: (1) Tailwind CSS v3.3+ installation in an existing Vite project with RTL configuration, (2) RTL layout patterns using Tailwind's logical properties, (3) FastAPI offset pagination for session items, (4) React state management with `useReducer` for a 20-item sequential labeling flow, and (5) annotation UI patterns for content classification.

The existing frontend uses inline styles with `dir="rtl"` already set on `<html>` and Tajawal font loaded via Google Fonts. The project uses `"type": "module"` in package.json (ESM), which affects config file generation. The backend follows a clean pattern: routers in `app/routers/`, schemas in `app/schemas/`, models in `app/models/`, SQLAlchemy 2.0 ORM queries, and Alembic migrations with raw SQL for enum types.

**Primary recommendation:** Use Tailwind CSS v3.4 (latest v3 line) with logical properties (`ms-`, `me-`, `ps-`, `pe-`, `text-start`, `text-end`) for all directional styling. Use `useReducer` for the labeling session state. Use simple offset pagination on the backend since session items are a fixed set of 20.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Auto-assign batch model**: Clicking "Start Training" creates a session with 20 random unlabeled examples from `content_examples`, scoped by institution_id (AUTH-04)
- **Batch size: 20 examples per session** (fixed for v1)
- **Two-step labeling**: hate/not_hate first, then 9-category selection if hate
- **Post-submit feedback**: Show ground truth after submission (quiz-style), compute `is_correct`
- **No AI prediction in Phase 3** (deferred to Phase 4-5)
- **Allow back navigation** within session
- **Progress bar** showing current position (e.g., "7/20")
- **Session completion screen**: total correct, accuracy %, start new session or return to dashboard
- **Install Tailwind CSS** in Phase 3 (one-time setup)
- **Design direction**: existing color palette (#1a1a2e navy, white, #f9f9f9 surfaces), cards for tweet display, big touch-friendly buttons, clean/minimal
- **Four backend endpoints**: POST /api/training/sessions, GET /api/training/sessions/{id}, PUT /api/training/sessions/{id}/items/{item_id}, GET /api/training/sessions
- **Database tables**: `training_sessions` and `session_items` with schema as defined in CONTEXT.md
- **Arabic labels for categories**: race=عنصرية, religion=ديني, ideology=أيديولوجي, gender=جنساني, disability=إعاقة, social_class=طبقي, tribalism=عشائري, refugee_related=لاجئين, political_affiliation=سياسي
- **hate/not_hate labels**: hate=خطاب كراهية, not_hate=ليس كراهية

### Claude's Discretion
- Tailwind configuration details (plugins, theme extension)
- Component structure and file organization
- State management approach (useState vs useReducer)
- Exact UI layout and spacing

### Deferred Ideas (OUT OF SCOPE)
- AI classification / MARBERT inference (Phase 4)
- Arabic explanations (Phase 5)
- Agree/disagree with AI (Phase 5)
- Calibration scoring (Phase 6)
- Observatory charts (Phase 7)
- Bias Auditor (Phase 7)
- English language toggle (Phase 8)
- Admin session creation (v2 -- ADMIN-02)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TRAIN-01 | Moderator can view Arabic content and submit hate/not_hate label | Labeling UI component with two-step flow, `PUT /api/training/sessions/{id}/items/{item_id}` endpoint |
| TRAIN-02 | Moderator can select hate type from 9 categories when labeling hate | Second step of labeling UI with 9 Arabic-labeled category buttons |
| TRAIN-05 | Moderator marks agree/disagree with AI | **Deferred to Phase 5** per CONTEXT.md -- Phase 3 shows ground truth only |
| TRAIN-07 | Moderator navigates through 10-50 examples in sequence | useReducer state with currentIndex, back/forward navigation, progress bar |
| UI-01 | All Arabic text renders RTL with appropriate font | Tailwind CSS v3.4 with logical properties, `dir="rtl"` on html, Tajawal font |
| UI-02 | Platform usable on Chrome, Firefox, Safari desktop | Standard Tailwind CSS -- no browser-specific issues |
| UI-03 | Arabic primary interface with English option | Arabic-only in Phase 3; English toggle deferred to Phase 8 |
</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| tailwindcss | 3.4.x | Utility-first CSS framework | Industry standard for rapid UI development, built-in RTL via logical properties since v3.3 |
| postcss | 8.x | CSS processing pipeline | Required peer dependency for Tailwind with Vite |
| autoprefixer | 10.x | Vendor prefix automation | Required peer dependency for Tailwind |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| react-router-dom | 6.27.0 | Client-side routing | Already installed -- use for training page routes |
| axios | 1.7.7 | HTTP client | Already installed -- use existing `api` instance for all backend calls |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Tailwind CSS | Keep inline styles | Inline styles don't support responsive/hover/RTL variants cleanly; Tailwind pays off across Phases 5-8 |
| useReducer | useState with multiple state variables | useState is simpler but leads to fragmented state for 20-item session with navigation |
| Offset pagination | Cursor pagination | Overkill for fixed 20-item sessions; offset is simpler and sufficient |

**Installation:**
```bash
cd mizan/frontend
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
```

Note: The project uses `"type": "module"` in package.json. Running `npx tailwindcss init` detects this and generates ESM-compatible config files automatically (`export default` syntax).

---

## Architecture Patterns

### Recommended Frontend Structure
```
src/
├── components/
│   ├── Layout.tsx              # Shared layout (header + nav + main)
│   ├── ProtectedRoute.tsx      # Existing auth guard
│   └── training/
│       ├── LabelingCard.tsx    # Tweet display card with Arabic text
│       ├── LabelButtons.tsx    # hate/not_hate + 9-category selection
│       ├── ProgressBar.tsx     # "7/20" progress indicator
│       ├── FeedbackReveal.tsx  # Ground truth reveal after submit
│       └── SessionSummary.tsx  # Completion screen with score
├── pages/
│   └── training/
│       ├── TrainingLanding.tsx # "Start Training" button screen
│       └── TrainingSession.tsx # Main labeling flow (useReducer)
├── lib/
│   ├── api.ts                 # Existing axios instance
│   ├── auth.tsx               # Existing auth context
│   ├── types.ts               # Existing + new training types
│   └── training-reducer.ts    # useReducer logic for session state
└── index.css                  # NEW: Tailwind directives
```

### Recommended Backend Structure
```
app/
├── models/
│   └── training_session.py    # TrainingSession + SessionItem models
├── schemas/
│   └── training.py            # Pydantic schemas for request/response
└── routers/
    └── training.py            # 4 training endpoints
```

### Pattern 1: useReducer for Session State

**What:** A reducer manages the entire labeling session state as a single object with all 20 items, current position, and navigation history.

**When to use:** When state transitions depend on previous state (navigating back, submitting labels, computing correctness).

**State shape:**
```typescript
interface SessionItem {
  id: string
  contentExampleId: string
  position: number
  text: string
  groundTruthLabel: 'hate' | 'not_hate'
  groundTruthHateType: string | null
  moderatorLabel: 'hate' | 'not_hate' | null
  moderatorHateType: string | null
  isCorrect: boolean | null
  isSubmitted: boolean
}

interface SessionState {
  sessionId: string
  items: SessionItem[]
  currentIndex: number    // 0-based index into items array
  totalItems: number      // always 20
  labeledCount: number    // how many have been submitted
  correctCount: number    // running tally of correct answers
  isComplete: boolean     // true when all 20 labeled
  isLoading: boolean
  error: string | null
}

type SessionAction =
  | { type: 'LOAD_SESSION'; payload: { sessionId: string; items: SessionItem[] } }
  | { type: 'SELECT_LABEL'; payload: { label: 'hate' | 'not_hate' } }
  | { type: 'SELECT_HATE_TYPE'; payload: { hateType: string } }
  | { type: 'SUBMIT_LABEL' }
  | { type: 'NAVIGATE'; payload: { direction: 'next' | 'prev' } }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'CLEAR_ERROR' }
```

**Why useReducer over useState:**
- Session state has 6+ interdependent fields
- Actions like SUBMIT_LABEL need to compute `isCorrect`, update `labeledCount`, `correctCount`, and potentially `isComplete`
- Back navigation must restore previous item state
- Single dispatch replaces multiple setState calls
- Predictable state transitions are testable

### Pattern 2: Two-Step Labeling Flow

**What:** When the moderator selects "hate", a second step slides in to choose from 9 categories. Selecting "not_hate" skips the second step.

**When to use:** This is the locked decision from CONTEXT.md.

**Flow:**
```
[View tweet text]
    ↓
[Select: خطاب كراهية / ليس كراهية]
    ↓ (if hate)               ↓ (if not_hate)
[Select category]          [Submit button enabled]
    ↓
[Submit button enabled]
    ↓
[Reveal ground truth + is_correct]
    ↓
[Next button → advance currentIndex]
```

### Pattern 3: Backend Training Router

**What:** Four endpoints in a single router file, all requiring authentication and institution scoping.

**When to use:** Standard FastAPI pattern matching existing `auth.py` and `export.py` routers.

**Example:**
```python
# app/routers/training.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.training_session import TrainingSession, SessionItem, SessionStatus
from app.models.content_example import ContentExample
from app.schemas.training import (
    SessionResponse, SessionListResponse,
    SubmitLabelRequest, SessionItemResponse,
)

router = APIRouter(prefix="/api/training", tags=["training"])

@router.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Query 20 random content_examples
    # 2. Create TrainingSession row
    # 3. Create 20 SessionItem rows with position 1-20
    # 4. Return session with items
    ...

@router.get("/sessions", response_model=list[SessionListResponse])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Return user's sessions with completion status
    ...

@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Return session with all items (ordered by position)
    # Verify ownership (user_id matches current_user.id)
    ...

@router.put("/sessions/{session_id}/items/{item_id}", response_model=SessionItemResponse)
def submit_label(
    session_id: str,
    item_id: str,
    request: SubmitLabelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Validate session ownership
    # 2. Update item with moderator_label, moderator_hate_type
    # 3. Compute is_correct by comparing to ground_truth
    # 4. Set labeled_at timestamp
    # 5. Check if all items labeled -> update session status
    # 6. Return updated item
    ...
```

### Anti-Patterns to Avoid
- **Storing UI state on the server:** Do NOT send currentIndex to the backend. Navigation state is frontend-only. The backend only cares about labels.
- **Using separate useState for each field:** With 6+ interdependent state values, scattered useState calls lead to impossible-to-debug race conditions.
- **Fetching items one at a time:** Load all 20 items in a single GET request. The dataset is small (20 items of Arabic text). No pagination needed for session items.
- **Using `ml-` / `mr-` / `pl-` / `pr-` in Tailwind:** Always use logical properties (`ms-`, `me-`, `ps-`, `pe-`) for RTL compatibility.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RTL layout flipping | Custom CSS with direction checks | Tailwind logical properties (`ms-`, `me-`, `ps-`, `pe-`, `text-start`) | Logical properties auto-flip based on `dir` attribute; zero JS needed |
| CSS utility classes | Inline style objects (current pattern) | Tailwind utility classes | Inline styles can't do hover, focus, responsive, or RTL variants |
| Random item selection | Custom shuffle algorithm in Python | SQLAlchemy `func.random()` with `.limit(20)` | Database-level randomization is simpler and avoids loading all rows |
| Session state machine | Manual boolean flags | `useReducer` with typed actions | Reducer guarantees valid state transitions, easy to test |

**Key insight:** The existing codebase uses inline styles everywhere (Dashboard.tsx has 80+ lines of style objects). Tailwind eliminates this complexity while adding RTL support, responsive design, and hover states for free.

---

## Common Pitfalls

### Pitfall 1: Tailwind Not Processing Files
**What goes wrong:** Tailwind generates an empty CSS file; no utility classes appear.
**Why it happens:** `content` array in `tailwind.config.js` doesn't match actual file paths, or `index.css` with `@tailwind` directives isn't imported in `main.tsx`.
**How to avoid:** Verify `content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}']` matches the project structure. Import `./index.css` in `main.tsx` before any components.
**Warning signs:** All elements appear unstyled, browser dev tools show no Tailwind classes in `<style>`.

### Pitfall 2: Physical Properties Instead of Logical
**What goes wrong:** Margins, paddings, and borders appear on the wrong side in RTL layout.
**Why it happens:** Using `ml-4` (margin-left) instead of `ms-4` (margin-start) — physical properties don't flip in RTL.
**How to avoid:** Use this mapping for ALL directional utilities:
| Physical (DO NOT USE) | Logical (USE THIS) |
|-----------------------|--------------------|
| `ml-*` | `ms-*` |
| `mr-*` | `me-*` |
| `pl-*` | `ps-*` |
| `pr-*` | `pe-*` |
| `left-*` | `start-*` |
| `right-*` | `end-*` |
| `text-left` | `text-start` |
| `text-right` | `text-end` |
| `rounded-l-*` | `rounded-s-*` |
| `rounded-r-*` | `rounded-e-*` |
| `border-l-*` | `border-s-*` |
| `border-r-*` | `border-e-*` |
**Warning signs:** Elements visually misaligned, margins appearing on the left instead of right.

### Pitfall 3: Flex Direction in RTL
**What goes wrong:** Flexbox layouts don't need `flex-row-reverse` in RTL — `flex-row` already reverses in RTL context.
**Why it happens:** Developers assume they need to reverse flex direction manually for RTL.
**How to avoid:** When `dir="rtl"` is set, `flex-row` automatically flows right-to-left. Using `flex-row-reverse` in RTL would actually make it flow left-to-right (double reversal). Just use `flex-row` and let the browser handle it.
**Warning signs:** Navigation items or button groups appearing in reversed order.

### Pitfall 4: Icons and Arrows
**What goes wrong:** Chevron/arrow icons point the wrong direction in RTL.
**Why it happens:** SVG icons have fixed orientation; they don't auto-mirror with RTL.
**How to avoid:** Use `rtl:-scale-x-100` on directional icons (arrows, chevrons) to flip them. Non-directional icons (checkmarks, x-marks) should NOT be flipped.
**Warning signs:** "Next" arrow pointing left (should point left in RTL, which is correct direction) — test carefully.

### Pitfall 5: LTR Input Fields
**What goes wrong:** Email, URL, and number inputs render oddly in RTL.
**Why it happens:** These fields contain LTR content (email addresses, URLs) within an RTL page.
**How to avoid:** Add `dir="ltr"` on input fields that contain LTR content (email, password). The existing Login.tsx already does this correctly. Keep Arabic text inputs without `dir` override.
**Warning signs:** Email cursor appearing on the wrong side, @ symbol misplaced.

### Pitfall 6: SQLAlchemy Enum Gotcha (Known Project Issue)
**What goes wrong:** Alembic migration fails with "type already exists" error for new enums.
**Why it happens:** `sa.Enum` in a `create_table` block tries to CREATE TYPE twice.
**How to avoid:** Follow the established pattern from Phase 2: use `op.execute("CREATE TYPE ...")` first, then `postgresql.ENUM(create_type=False)` in the column definition.
**Warning signs:** Migration error mentioning duplicate type name.

### Pitfall 7: Random Selection Bias
**What goes wrong:** Same examples appear in multiple sessions; some examples never get selected.
**Why it happens:** `ORDER BY RANDOM() LIMIT 20` selects any 20 rows without checking if they were previously assigned.
**How to avoid:** For v1 with 560 examples and a solo developer demo, pure random is acceptable. The 20/560 overlap probability is low enough. If needed later, exclude already-seen example IDs with a subquery.
**Warning signs:** Moderator seeing the same tweets in consecutive sessions (cosmetic issue for demo, not a blocker).

---

## Code Examples

### Tailwind CSS Installation (Vite + ESM)

```bash
# From mizan/frontend/
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
```

Generated `tailwind.config.js` (ESM because package.json has `"type": "module"`):
```javascript
// Source: https://v3.tailwindcss.com/docs/guides/vite
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        tajawal: ['Tajawal', 'sans-serif'],
      },
      colors: {
        mizan: {
          navy: '#1a1a2e',
          surface: '#f9f9f9',
        },
      },
    },
  },
  plugins: [],
}
```

Generated `postcss.config.js`:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

`src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Global base styles */
body {
  font-family: 'Tajawal', sans-serif;
}
```

`src/main.tsx` (add import):
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'    // <-- ADD THIS LINE
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

### RTL Layout with Logical Properties

```tsx
// Source: https://tailwindcss.com/blog/tailwindcss-v3-3 (logical properties)

// CORRECT: Using logical properties (auto-flips in RTL)
<div className="flex items-center gap-3 ps-4 pe-6 ms-2">
  <img className="h-10 w-10 rounded-full" src={avatar} alt="" />
  <div className="ms-3">
    <p className="text-sm font-medium text-start">{name}</p>
  </div>
</div>

// WRONG: Using physical properties (won't flip in RTL)
<div className="flex items-center gap-3 pl-4 pr-6 ml-2">
  {/* This will have wrong margins in RTL */}
</div>
```

### Labeling Card Component Pattern

```tsx
// Tweet display card for Arabic content
function LabelingCard({ text, position, total }: {
  text: string
  position: number
  total: number
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 max-w-2xl mx-auto">
      {/* Progress indicator */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-gray-500">
          {position} / {total}
        </span>
        <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
          <div
            className="bg-mizan-navy rounded-full h-2 transition-all duration-300"
            style={{ width: `${(position / total) * 100}%` }}
          />
        </div>
      </div>

      {/* Arabic tweet text - large, clear */}
      <div className="py-8 px-4">
        <p className="text-xl leading-relaxed text-gray-900 font-tajawal">
          {text}
        </p>
      </div>
    </div>
  )
}
```

### useReducer Session Logic

```typescript
// src/lib/training-reducer.ts
function sessionReducer(state: SessionState, action: SessionAction): SessionState {
  switch (action.type) {
    case 'LOAD_SESSION':
      return {
        ...state,
        sessionId: action.payload.sessionId,
        items: action.payload.items,
        totalItems: action.payload.items.length,
        currentIndex: 0,
        labeledCount: action.payload.items.filter(i => i.isSubmitted).length,
        correctCount: action.payload.items.filter(i => i.isCorrect === true).length,
        isComplete: false,
        isLoading: false,
        error: null,
      }

    case 'SELECT_LABEL': {
      const items = [...state.items]
      const current = { ...items[state.currentIndex] }
      current.moderatorLabel = action.payload.label
      // Clear hate type if switching to not_hate
      if (action.payload.label === 'not_hate') {
        current.moderatorHateType = null
      }
      items[state.currentIndex] = current
      return { ...state, items }
    }

    case 'SELECT_HATE_TYPE': {
      const items = [...state.items]
      const current = { ...items[state.currentIndex] }
      current.moderatorHateType = action.payload.hateType
      items[state.currentIndex] = current
      return { ...state, items }
    }

    case 'SUBMIT_LABEL': {
      const items = [...state.items]
      const current = { ...items[state.currentIndex] }
      // Compute correctness: compare moderator label to ground truth
      const labelMatch = current.moderatorLabel === current.groundTruthLabel
      current.isCorrect = labelMatch
      current.isSubmitted = true
      items[state.currentIndex] = current

      const labeledCount = items.filter(i => i.isSubmitted).length
      const correctCount = items.filter(i => i.isCorrect === true).length
      const isComplete = labeledCount === state.totalItems

      return { ...state, items, labeledCount, correctCount, isComplete }
    }

    case 'NAVIGATE': {
      const delta = action.payload.direction === 'next' ? 1 : -1
      const newIndex = state.currentIndex + delta
      if (newIndex < 0 || newIndex >= state.totalItems) return state
      return { ...state, currentIndex: newIndex }
    }

    default:
      return state
  }
}
```

### FastAPI Training Session Creation

```python
# Source: Follows project pattern from app/routers/auth.py and app/routers/export.py
from sqlalchemy import func

@router.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Select 20 random examples
    examples = (
        db.query(ContentExample)
        .order_by(func.random())
        .limit(20)
        .all()
    )

    if len(examples) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Not enough content examples available",
        )

    session = TrainingSession(
        user_id=current_user.id,
        institution_id=current_user.institution_id,
        status=SessionStatus.in_progress,
        total_items=20,
        correct_count=0,
    )
    db.add(session)
    db.flush()  # Get session.id before creating items

    for i, example in enumerate(examples, start=1):
        item = SessionItem(
            session_id=session.id,
            content_example_id=example.id,
            position=i,
        )
        db.add(item)

    db.commit()
    db.refresh(session)
    return session
```

### Alembic Migration Pattern (Project Convention)

```python
# Following Phase 2 pattern: raw SQL for enums, postgresql.ENUM(create_type=False)
def upgrade():
    op.execute("CREATE TYPE sessionstatus AS ENUM ('in_progress', 'completed')")
    op.execute("CREATE TYPE moderatorlabel AS ENUM ('hate', 'not_hate')")

    op.create_table(
        'training_sessions',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('institution_id', sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('institutions.id', ondelete='CASCADE'), nullable=True),
        sa.Column('status', sa.dialects.postgresql.ENUM('in_progress', 'completed',
                  name='sessionstatus', create_type=False), nullable=False),
        sa.Column('total_items', sa.Integer, nullable=False),
        sa.Column('correct_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'session_items',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('training_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_example_id', sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('content_examples.id', ondelete='CASCADE'), nullable=False),
        sa.Column('position', sa.Integer, nullable=False),
        sa.Column('moderator_label', sa.dialects.postgresql.ENUM('hate', 'not_hate',
                  name='moderatorlabel', create_type=False), nullable=True),
        sa.Column('moderator_hate_type', sa.dialects.postgresql.ENUM(
                  name='hatetype', create_type=False), nullable=True),
        sa.Column('is_correct', sa.Boolean, nullable=True),
        sa.Column('labeled_at', sa.DateTime, nullable=True),
    )

def downgrade():
    op.drop_table('session_items')
    op.drop_table('training_sessions')
    op.execute("DROP TYPE IF EXISTS moderatorlabel")
    op.execute("DROP TYPE IF EXISTS sessionstatus")
    # NOTE: hatetype enum already exists from Phase 2 -- do NOT drop it
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tailwind v2 + `@tailwindcss/typography` RTL plugin | Tailwind v3.3+ built-in logical properties | March 2023 (v3.3) | No third-party plugin needed for RTL |
| `ltr:ml-3 rtl:mr-3` variant pairs | `ms-3` logical property | Tailwind v3.3 | 50% fewer classes, cleaner markup |
| `text-left` / `text-right` | `text-start` / `text-end` | Tailwind v3.3 | Auto-flips with document direction |
| Tailwind v4 (latest) | Tailwind v3.4 (LTS) | January 2025 (v4.0 released) | v4 is a full rewrite with breaking changes; v3.4 is stable and well-documented |

**Deprecated/outdated:**
- `tailwindcss-rtl` plugin: Unnecessary since v3.3 added native logical properties
- `tailwindcss-vanilla-rtl` plugin: Same -- superseded by built-in support
- Tailwind v4: Released Jan 2025 but uses completely different configuration system (CSS-based config, no `tailwind.config.js`). NOT recommended for this project because: (a) most documentation and examples still target v3, (b) v4 setup is fundamentally different, (c) v3.4 is battle-tested and stable

---

## Annotation UI Design Recommendations

Based on research from Label Studio, Prodigy, and annotation UX best practices:

### Content Display
- Display tweet text in a **large, centered card** with generous padding (py-8 px-4)
- Use **text-xl** or larger for Arabic text (Arabic characters appear 20-25% smaller than Latin at the same font size)
- Keep the content card visually dominant -- it's the primary focus area
- Add subtle source dataset tag (e.g., "JHSC", "Let-Mi") in muted text below the content

### Label Selection
- Use **large, touch-friendly buttons** (min-height 48px, full-width on mobile)
- Two primary buttons for hate/not_hate: distinct colors (red for hate, green for not_hate)
- Category buttons in a **3x3 grid** layout when hate is selected
- Selected state should be visually distinct (filled background, not just border change)

### Progress and Feedback
- **Top progress bar** showing filled portion (e.g., 7/20 = 35% filled)
- Text counter alongside bar: "7 من 20" (7 of 20)
- After submit, show ground truth with **color-coded feedback**: green checkmark for correct, red X for incorrect
- Brief animation/transition when revealing feedback (200-300ms)

### Navigation
- "السابق" (Previous) and "التالي" (Next) buttons at bottom of card
- Previous button disabled on first item; Next disabled on last unlabeled item
- Keyboard shortcuts: Left arrow = next (RTL), Right arrow = previous (RTL)
- Allow re-visiting and changing already-submitted answers

---

## Open Questions

1. **HateType enum reuse in session_items**
   - What we know: The `hatetype` enum already exists in PostgreSQL from Phase 2 (used by `content_examples.hate_type`)
   - What's unclear: Whether `moderator_hate_type` in `session_items` should reuse the same enum or create a new one
   - Recommendation: Reuse the existing `hatetype` enum. It contains exactly the 9 categories plus "unknown". The migration should NOT create a new enum -- just reference the existing one with `create_type=False`.

2. **Institution scoping for content_examples**
   - What we know: CONTEXT.md says examples are "scoped to their institution via AUTH-04"
   - What's unclear: `content_examples` table has no `institution_id` column -- it's shared across all institutions
   - Recommendation: For v1, all content examples are global (shared). The institution scoping applies to **sessions** (a moderator only sees their own sessions). Content examples are the same for everyone. This is consistent with how the seeded data works (560 global examples from 4 datasets).

3. **Session list pagination**
   - What we know: GET /api/training/sessions lists a moderator's sessions
   - What's unclear: Whether pagination is needed for the sessions list
   - Recommendation: Skip pagination for v1. A moderator in demo context will have 1-5 sessions at most. Return all sessions ordered by `created_at DESC`.

---

## Sources

### Primary (HIGH confidence)
- [Tailwind CSS v3 Vite Guide](https://v3.tailwindcss.com/docs/guides/vite) - Exact installation steps for Tailwind v3 with Vite
- [Tailwind CSS v3.3 Release Blog](https://tailwindcss.com/blog/tailwindcss-v3-3) - Logical properties reference (`ms-`, `me-`, `ps-`, `pe-`, etc.)
- [Tailwind CSS v3 Text Align Docs](https://v3.tailwindcss.com/docs/text-align) - `text-start` / `text-end` utilities
- [React useReducer Reference](https://react.dev/reference/react/useReducer) - Official React docs for useReducer
- [SQLModel FastAPI Pagination](https://sqlmodel.tiangolo.com/tutorial/fastapi/limit-and-offset/) - Offset/limit pattern with SQLAlchemy

### Secondary (MEDIUM confidence)
- [Flowbite RTL Guide](https://flowbite.com/docs/customize/rtl/) - RTL best practices with Tailwind, logical property mapping
- [Labellerr Data Labeling UI Best Practices](https://www.labellerr.com/blog/best-data-labeling-user-interface-tools-features-and-best-practices/) - Annotation interface UX
- [FastAPI Pagination Blog](https://oneuptime.com/blog/post/2026-02-02-fastapi-pagination/view) - Pagination patterns comparison

### Tertiary (LOW confidence)
- None -- all findings verified with primary or secondary sources

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Tailwind v3 with Vite is extremely well-documented; installation steps verified with official docs
- Architecture: HIGH - Patterns derived from official React docs and existing project conventions (routers, models, schemas)
- RTL support: HIGH - Logical properties confirmed in Tailwind v3.3 release notes with full mapping table
- Pitfalls: HIGH - RTL gotchas verified across multiple sources; Alembic enum issue confirmed from project history
- Annotation UI: MEDIUM - Based on general annotation tool UX research, not a specific Arabic labeling tool

**Research date:** 2026-03-02
**Valid until:** 2026-04-02 (Tailwind v3 is in LTS, unlikely to change)
