# Phase 12: Active Learning Loop - Research

**Researched:** 2026-03-03
**Domain:** Active learning sampling strategies, FastAPI + SQLAlchemy query patterns, React strategy picker UI
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Strategy Picker UX**
- Radio cards on the Training start screen (before session creation), not a dropdown
- Strategy is locked for the session — no mid-session switching
- Sequential strategy pre-selected as default (preserves current behavior)
- Button text stays "ابدأ التدريب" regardless of selected strategy
- Strategy name shown in session summary and session history list

**Uncertainty Sampling**
- Batch pre-compute MARBERT confidence on all 560 content_examples at migration/startup time
- New `ai_confidence` column on `content_examples` table (migration required)
- Select top-20 examples closest to 0.5 confidence (sort by |confidence - 0.5| ascending)
- Exclude examples already labeled by this moderator in prior sessions
- If no confidence scores exist (model never ran), disable uncertainty card with Arabic message: "يتطلب تحميل النموذج"

**Disagreement Sampling**
- Definition: examples where prior moderators' labels disagree with ground truth (is_correct=false)
- Consider ALL moderators' labels across the platform, not just current user
- Rank by error rate — most incorrect labels across all sessions first, take top 20
- If no prior sessions exist, disable card with Arabic message: "يتطلب جلسة سابقة واحدة على الأقل"
- Fallback: when no moderator history exists, use AI-vs-ground-truth disagreement (pre-computed MARBERT scores)

**Strategy Labels & Arabic**
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

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TRAIN-08 | New requirement: Add uncertainty and disagreement sampling strategies to training sessions so moderators practice on the most educational examples — improving calibration faster. | Covered by: active_learning.py service design (strategies section), migration pattern for ai_confidence column, strategy picker UI pattern, SQLAlchemy query patterns for uncertainty/disagreement ranking |
</phase_requirements>

---

## Summary

Phase 12 adds three sampling strategies to the existing training session creation flow. The core work is a new `active_learning.py` backend service, one Alembic migration adding `ai_confidence Float` to `content_examples`, a `strategy` enum column on `training_sessions`, and UI changes to `TrainingPage.tsx`, `SessionHistoryList.tsx`, `SessionSummary.tsx`, and `training-api.ts`. No new pages are created.

The two non-sequential strategies require different pre-conditions: uncertainty sampling requires MARBERT confidence scores pre-computed on all 560 `content_examples` rows (stored in `ai_confidence`); disagreement sampling requires prior `session_items` rows with `is_correct` populated. Both have graceful disabled states with Arabic messages when pre-conditions are not met. The backend must communicate these availability flags to the frontend at session-start time via a new availability endpoint or by piggybacking them onto the existing `list_sessions` response.

The implementation touches a known SQLAlchemy query complexity boundary: ranking by error rate across all moderators requires a GROUP BY aggregate subquery on `session_items`. The project's established pattern (raw SQL when ORM queries cause issues) should be applied defensively here.

**Primary recommendation:** Implement `active_learning.py` as a pure service module (no router) that `training.py` imports — keeping strategy logic out of the router layer. Use `strategy` as a body field on `POST /api/training/sessions`, defaulting to `"sequential"`.

---

## Standard Stack

### Core (no new dependencies — all already in use)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy 2.0 | Already installed | Query patterns for uncertainty/disagreement ranking | Project standard; all existing DB logic uses it |
| FastAPI | Already installed | New query param / body field on sessions endpoint | Project standard |
| Alembic | Already installed | Migration: `ai_confidence` Float on content_examples + `strategy` Enum on training_sessions | Project standard |
| React + Vite | Already installed | Strategy picker radio cards in TrainingPage | Project standard |
| Tailwind CSS v3.4 | Already installed | Card layout, color-coding, RTL logical properties | Project standard |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `torch` / `model_manager.classify()` | Already installed | Pre-computing MARBERT confidence for `ai_confidence` column | Used in a one-time script or startup hook; reuses existing `classify()` method |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Body field `strategy` on POST | Query param `?strategy=uncertainty` | Body is cleaner for session creation; follows REST convention. Query param is acceptable but inconsistent with existing `SubmitLabelRequest` pattern |
| Pre-compute at migration time | Pre-compute at model load time (startup) | Startup is simpler but ties ML inference to server boot; a one-time script is more predictable and separable from server health |

**Installation:** No new packages required.

---

## Architecture Patterns

### Recommended Project Structure Changes

```
mizan/backend/
├── app/
│   ├── services/
│   │   └── active_learning.py      # NEW — 3 strategy functions
│   ├── routers/
│   │   └── training.py             # MODIFIED — import strategies, add strategy body field
│   ├── models/
│   │   └── training.py             # MODIFIED — add SamplingStrategy enum + strategy column
│   └── schemas/
│       └── training.py             # MODIFIED — add strategy field to CreateSessionRequest
├── alembic/versions/
│   └── g9h0i1j2k3l4_phase12_active_learning.py   # NEW migration
└── scripts/
    └── precompute_confidence.py    # NEW — batch MARBERT classify on content_examples

mizan/frontend/src/
├── lib/
│   ├── training-api.ts             # MODIFIED — createSession(strategy), StrategyAvailability type
│   └── types.ts                    # MODIFIED — TrainingSession.strategy field
├── pages/
│   ├── TrainingPage.tsx            # MODIFIED — strategy picker cards above start button
│   └── SessionSummary.tsx          # MODIFIED — show strategy badge in summary
└── components/
    └── SessionHistoryList.tsx      # MODIFIED — show strategy chip in each row
```

### Pattern 1: Strategy Enum on TrainingSession Model

Add `SamplingStrategy` enum to `training.py` model following existing `SessionStatus` / `ModeratorLabel` enum pattern. Use raw SQL `CREATE TYPE` in Alembic — project convention (avoids SQLAlchemy double-create).

```python
# mizan/backend/app/models/training.py

class SamplingStrategy(str, enum.Enum):
    sequential = "sequential"
    uncertainty = "uncertainty"
    disagreement = "disagreement"


class TrainingSession(Base):
    # ... existing columns ...
    strategy = Column(
        Enum(SamplingStrategy),
        default=SamplingStrategy.sequential,
        nullable=False,
        server_default="sequential",
    )
```

```python
# Alembic migration (project convention: raw SQL for enum creation)
def upgrade() -> None:
    op.execute("CREATE TYPE samplingstrategy AS ENUM ('sequential', 'uncertainty', 'disagreement')")
    samplingstrategy = postgresql.ENUM(name="samplingstrategy", create_type=False)
    op.add_column(
        "training_sessions",
        sa.Column("strategy", samplingstrategy, nullable=False, server_default="sequential"),
    )
    op.add_column(
        "content_examples",
        sa.Column("ai_confidence", sa.Float(), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("training_sessions", "strategy")
    op.drop_column("content_examples", "ai_confidence")
    op.execute("DROP TYPE IF EXISTS samplingstrategy")
```

### Pattern 2: active_learning.py — Three Strategy Functions

The service module returns a list of `ContentExample` ORM objects. The router replaces its current `func.random()` query with a call to this service.

```python
# mizan/backend/app/services/active_learning.py

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.content_example import ContentExample
from app.models.training import TrainingSession, SessionItem, SamplingStrategy


def _excluded_ids_subquery(db: Session, user_id):
    """Subquery for content_example IDs already seen by this user."""
    return (
        db.query(SessionItem.content_example_id)
        .join(TrainingSession)
        .filter(TrainingSession.user_id == user_id)
        .subquery()
    )


def select_examples_sequential(db: Session, user_id, limit: int = 20) -> list[ContentExample]:
    """Current behavior: random order, exclude already-seen examples."""
    excluded = _excluded_ids_subquery(db, user_id)
    return (
        db.query(ContentExample)
        .filter(~ContentExample.id.in_(excluded))
        .order_by(func.random())
        .limit(limit)
        .all()
    )


def select_examples_uncertainty(db: Session, user_id, limit: int = 20) -> list[ContentExample]:
    """Select examples where MARBERT confidence is closest to 0.5.

    Sorts by ABS(ai_confidence - 0.5) ascending.
    Excludes examples with NULL ai_confidence (model not run yet).
    """
    excluded = _excluded_ids_subquery(db, user_id)
    return (
        db.query(ContentExample)
        .filter(
            ~ContentExample.id.in_(excluded),
            ContentExample.ai_confidence.isnot(None),
        )
        .order_by(
            func.abs(ContentExample.ai_confidence - 0.5)
        )
        .limit(limit)
        .all()
    )


def select_examples_disagreement(db: Session, user_id, limit: int = 20) -> list[ContentExample]:
    """Select examples with highest moderator error rate across all sessions.

    Ranks by: count(is_correct=false) / count(*) descending.
    Falls back to AI-vs-ground-truth disagreement when no labeled history exists.
    """
    excluded = _excluded_ids_subquery(db, user_id)

    # Aggregate error rate per content_example across ALL moderators
    error_subq = (
        db.query(
            SessionItem.content_example_id,
            func.count(case((SessionItem.is_correct == False, 1))).label("wrong_count"),
            func.count(SessionItem.id).label("total_count"),
        )
        .filter(SessionItem.is_correct.isnot(None))
        .group_by(SessionItem.content_example_id)
        .subquery()
    )

    results = (
        db.query(ContentExample)
        .join(error_subq, ContentExample.id == error_subq.c.content_example_id)
        .filter(~ContentExample.id.in_(excluded))
        .order_by(
            (error_subq.c.wrong_count.cast(sa.Float) / error_subq.c.total_count).desc()
        )
        .limit(limit)
        .all()
    )

    # Fallback: no labeled history → use uncertainty sampling
    if not results:
        return select_examples_uncertainty(db, user_id, limit)
    return results


def select_examples(
    db: Session, user_id, strategy: SamplingStrategy, limit: int = 20
) -> list[ContentExample]:
    """Dispatch to correct strategy."""
    if strategy == SamplingStrategy.uncertainty:
        return select_examples_uncertainty(db, user_id, limit)
    if strategy == SamplingStrategy.disagreement:
        return select_examples_disagreement(db, user_id, limit)
    return select_examples_sequential(db, user_id, limit)
```

### Pattern 3: Strategy Availability Check (New Endpoint)

The frontend needs to know which strategies are available before rendering the picker. Add a lightweight `GET /api/training/strategies/availability` endpoint that returns boolean flags. This avoids embedding availability logic in the frontend.

```python
# In training.py router

@router.get("/strategies/availability")
def get_strategy_availability(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Return which sampling strategies are currently available."""
    # Uncertainty: any content_example has ai_confidence?
    has_confidence = db.query(ContentExample).filter(
        ContentExample.ai_confidence.isnot(None)
    ).first() is not None

    # Disagreement: any session_items with is_correct populated?
    has_labeled_history = db.query(SessionItem).filter(
        SessionItem.is_correct.isnot(None)
    ).first() is not None

    return {
        "sequential": True,
        "uncertainty": has_confidence,
        "disagreement": has_labeled_history,
    }
```

### Pattern 4: CreateSession with Strategy Body Field

Extend the existing `POST /api/training/sessions` to accept an optional `strategy` field. Follows `SubmitLabelRequest` pattern — Pydantic body schema.

```python
# app/schemas/training.py — add new schema

class CreateSessionRequest(BaseModel):
    strategy: str = "sequential"  # default preserves current behavior
```

```python
# app/routers/training.py — modify create_session

@router.post("/sessions", status_code=201)
def create_session(
    request: CreateSessionRequest = Body(default_factory=CreateSessionRequest),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    db: Session = Depends(get_db),
):
    try:
        strategy = SamplingStrategy(request.strategy)
    except ValueError:
        strategy = SamplingStrategy.sequential

    examples = select_examples(db, current_user.id, strategy)

    if len(examples) == 0:
        raise HTTPException(status_code=400, detail="لا توجد أمثلة متاحة")

    session = TrainingSession(
        user_id=current_user.id,
        institution_id=current_user.institution_id,
        status=SessionStatus.in_progress,
        total_items=len(examples),
        strategy=strategy,               # NEW
    )
    # rest unchanged ...
```

### Pattern 5: Frontend Strategy Picker (Radio Cards)

Modeled after Dashboard's 3-card grid (`Dashboard.tsx` — `border-t-4` accent cards). Strategy is local state in `TrainingPage`; passed to `createSession(strategy)`.

```tsx
// TrainingPage.tsx additions (conceptual pattern)

type Strategy = 'sequential' | 'uncertainty' | 'disagreement'

const STRATEGIES = [
  {
    id: 'sequential' as Strategy,
    name: 'تدريب تسلسلي',
    desc: 'أمثلة عشوائية للتعلم الأساسي',
    accent: 'border-green-500',
    bg: 'bg-green-50',
    ring: 'ring-green-500',
  },
  {
    id: 'uncertainty' as Strategy,
    name: 'تدريب التحدي',
    desc: 'أمثلة يصعب على الذكاء الاصطناعي تصنيفها',
    accent: 'border-amber-500',
    bg: 'bg-amber-50',
    ring: 'ring-amber-500',
  },
  {
    id: 'disagreement' as Strategy,
    name: 'أمثلة مثيرة للجدل',
    desc: 'أمثلة اختلف عليها المشرفون الآخرون',
    accent: 'border-red-500',
    bg: 'bg-red-50',
    ring: 'ring-red-500',
  },
]

// Selected card: add ring-2 + ring-offset-2 + ring-{color} for visual selection indicator
// Disabled card: add opacity-50 + cursor-not-allowed + pointer-events-none
```

### Pattern 6: Pre-compute Script

One-time script to populate `content_examples.ai_confidence`. Runs after `alembic upgrade head`.

```python
# mizan/backend/scripts/precompute_confidence.py

from app.database import SessionLocal
from app.models.content_example import ContentExample
from app.services.ml_models import ModelManager
from app.core.config import settings

def main():
    db = SessionLocal()
    manager = ModelManager()
    manager.load_models(settings.marbert_model_id, settings.xlm_model_id)

    examples = db.query(ContentExample).filter(
        ContentExample.ai_confidence.is_(None)
    ).all()
    print(f"Pre-computing confidence for {len(examples)} examples...")

    for i, ex in enumerate(examples):
        result = manager.classify(ex.text, settings.code_mixed_threshold)
        ex.ai_confidence = result["confidence"]
        if i % 50 == 0:
            db.commit()
            print(f"  {i}/{len(examples)} done")

    db.commit()
    print("Done.")

if __name__ == "__main__":
    main()
```

### Pattern 7: Session Badge in TrainingSession Page

A small chip at the top of the session labeling page showing which strategy is active. The `TrainingSession` type already gets the `strategy` field from the API. The chip renders conditionally:

```tsx
// In TrainingSession.tsx — above the ProgressBar
{session.strategy && session.strategy !== 'sequential' && (
  <div className="mb-3 flex justify-start">
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
      session.strategy === 'uncertainty'
        ? 'bg-amber-100 text-amber-700'
        : 'bg-red-100 text-red-700'
    }`}>
      {session.strategy === 'uncertainty' ? 'تدريب التحدي' : 'أمثلة مثيرة للجدل'}
    </span>
  </div>
)}
```

### Anti-Patterns to Avoid

- **Putting strategy selection logic in the router:** The router should call `active_learning.select_examples()` — business logic belongs in the service layer.
- **Using `sa.Enum` directly in `op.add_column`:** Project convention requires `op.execute("CREATE TYPE ...")` + `postgresql.ENUM(create_type=False)`. Violating this double-creates the type and breaks Alembic.
- **Querying `is_correct=False` with `==`:** SQLAlchemy's `==` on booleans in filter can behave unexpectedly with NULLs. Use `case((SessionItem.is_correct == False, 1))` for counting or filter with `.filter(SessionItem.is_correct.is_(False))`.
- **Calling `model_manager` in the migration:** Alembic migrations must be pure DB operations. Run pre-compute as a separate script after migration, never inside `upgrade()`.
- **Hardcoding availability in frontend:** Don't compute strategy availability client-side. Fetch from `GET /api/training/strategies/availability` on `TrainingPage` mount.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Absolute value in SQL ORDER BY | Custom Python sort after fetching all rows | `func.abs()` in SQLAlchemy | Pushes sort to DB, handles large datasets without loading all 560 rows into Python |
| Error rate calculation | Python loop over all session_items | GROUP BY aggregate subquery with `func.count(case(...))` | Single DB round-trip; correct with concurrent writers |
| Strategy availability check | Frontend-side check on fetched data | `GET /api/training/strategies/availability` endpoint | Clean separation; avoids leaking DB query logic to client |

**Key insight:** The disagreement ranking is a GROUP BY aggregate query — doing it in Python after fetching all rows risks memory issues if `session_items` grows large over time.

---

## Common Pitfalls

### Pitfall 1: Alembic Enum Double-Create

**What goes wrong:** Adding `strategy` enum with `sa.Enum("sequential", "uncertainty", "disagreement", name="samplingstrategy")` inside `op.add_column` causes `CREATE TYPE samplingstrategy` to run twice — once by SQLAlchemy, once because Alembic detects it. Migration fails with `type "samplingstrategy" already exists`.

**Why it happens:** SQLAlchemy's `Enum` type tries to create the DB type when rendering DDL. Alembic also runs it.

**How to avoid:** Always use `op.execute("CREATE TYPE samplingstrategy AS ENUM (...)")` before the `add_column`, then pass `postgresql.ENUM(name="samplingstrategy", create_type=False)` as the column type. This is the confirmed project convention (see Phase 3 migration).

**Warning signs:** `ProgrammingError: type "samplingstrategy" already exists` during `alembic upgrade head`.

### Pitfall 2: NULL ai_confidence Breaking Uncertainty Sort

**What goes wrong:** If any `content_examples` rows have `ai_confidence = NULL`, `ORDER BY ABS(ai_confidence - 0.5)` puts NULLs at the end (PostgreSQL default) but they remain in the result set if the `.isnot(None)` filter is omitted. The sort succeeds but returns nulls mixed in at wrong positions.

**Why it happens:** `func.abs(None - 0.5)` evaluates to NULL in SQL; NULL sorts last by default in PostgreSQL.

**How to avoid:** Always add `.filter(ContentExample.ai_confidence.isnot(None))` in `select_examples_uncertainty`. Also check this before reporting `has_confidence = True` in the availability endpoint.

**Warning signs:** Uncertainty session returns items with no model confidence score.

### Pitfall 3: Stale TrainingSession Type on Frontend

**What goes wrong:** `TrainingSession` interface in `types.ts` lacks a `strategy` field. When the API returns `strategy: "uncertainty"`, TypeScript ignores it (extra field). The session page badge never renders. The session history list can't show the chip.

**Why it happens:** TypeScript interfaces aren't automatically updated when the backend API schema changes.

**How to avoid:** Add `strategy: 'sequential' | 'uncertainty' | 'disagreement'` to the `TrainingSession` interface in `types.ts` as part of the same plan that modifies the backend.

### Pitfall 4: createSession() Called Without Strategy Arg

**What goes wrong:** `SessionSummary.tsx` calls `createSession()` when starting a new session from the summary page. If `createSession()` signature changes to `createSession(strategy)` without updating `SessionSummary.tsx`, TypeScript catches it at build time but E2E tests catch it at runtime if types aren't strict.

**Why it happens:** `SessionSummary.tsx` has its own "start new session" button that bypasses the `TrainingPage` strategy picker.

**How to avoid:** `createSession(strategy: Strategy = 'sequential')` — default to `'sequential'` so `SessionSummary.tsx` doesn't need updating. Users starting from summary always get sequential (sensible default since they finished a session).

### Pitfall 5: Disagreement Fallback Infinite Loop

**What goes wrong:** `select_examples_disagreement` falls back to `select_examples_uncertainty` when no labeled history exists. If uncertainty also returns empty (no `ai_confidence` computed), the function returns an empty list. The router raises HTTP 400. This is correct behavior — but the frontend must handle the 400 gracefully.

**Why it happens:** Both non-sequential strategies have pre-conditions that may not be met simultaneously on a fresh install.

**How to avoid:** The availability endpoint returns `disagreement: false` when no labeled history exists. The frontend disables the card before the user can attempt to start with it. The 400 is a safety net, not the primary guard.

### Pitfall 6: SQLAlchemy Boolean Filter with NULL Values

**What goes wrong:** `filter(SessionItem.is_correct == False)` in SQLAlchemy may not correctly handle the three-valued logic (True/False/NULL) in PostgreSQL. `is_correct` is nullable (NULL until moderator submits).

**Why it happens:** SQL `NULL = FALSE` evaluates to NULL (not TRUE), so rows where `is_correct IS NULL` are correctly excluded — but the SQLAlchemy ORM `== False` operator may or may not generate `IS FALSE` vs `= FALSE` depending on SQLAlchemy version.

**How to avoid:** Use `case((SessionItem.is_correct.is_(False), 1))` for counting incorrect labels. Use `.filter(SessionItem.is_correct.isnot(None))` as a pre-filter when needed.

---

## Code Examples

### Uncertainty Query with func.abs()

```python
# Source: SQLAlchemy 2.0 docs — func, ordering
from sqlalchemy import func

examples = (
    db.query(ContentExample)
    .filter(
        ~ContentExample.id.in_(excluded_subq),
        ContentExample.ai_confidence.isnot(None),
    )
    .order_by(func.abs(ContentExample.ai_confidence - 0.5).asc())
    .limit(20)
    .all()
)
```

### Disagreement Aggregate Subquery

```python
# Source: SQLAlchemy 2.0 docs — subqueries, case expressions
from sqlalchemy import func, case
import sqlalchemy as sa

error_subq = (
    db.query(
        SessionItem.content_example_id,
        func.count(case((SessionItem.is_correct.is_(False), 1))).label("wrong_count"),
        func.count(SessionItem.id).label("total_count"),
    )
    .filter(SessionItem.is_correct.isnot(None))
    .group_by(SessionItem.content_example_id)
    .subquery()
)

ranked = (
    db.query(ContentExample)
    .join(error_subq, ContentExample.id == error_subq.c.content_example_id)
    .filter(~ContentExample.id.in_(excluded_subq))
    .order_by(
        (error_subq.c.wrong_count.cast(sa.Float) / error_subq.c.total_count).desc()
    )
    .limit(20)
    .all()
)
```

### Frontend createSession with Strategy

```typescript
// training-api.ts
export type SamplingStrategy = 'sequential' | 'uncertainty' | 'disagreement'

export async function createSession(
  strategy: SamplingStrategy = 'sequential'
): Promise<TrainingSession> {
  const res = await api.post<TrainingSession>('/api/training/sessions', { strategy })
  return res.data
}

export interface StrategyAvailability {
  sequential: boolean
  uncertainty: boolean
  disagreement: boolean
}

export async function getStrategyAvailability(): Promise<StrategyAvailability> {
  const res = await api.get<StrategyAvailability>('/api/training/strategies/availability')
  return res.data
}
```

### Types.ts Addition

```typescript
// types.ts — add strategy to TrainingSession
export type SamplingStrategy = 'sequential' | 'uncertainty' | 'disagreement'

export interface TrainingSession {
  id: string
  status: 'in_progress' | 'completed'
  total_items: number
  labeled_count: number
  correct_count: number | null
  created_at: string
  completed_at: string | null
  strategy: SamplingStrategy          // NEW
  items?: SessionItem[]
}
```

### Strategy Badge Display (Arabic Names)

```typescript
// Mapping from strategy enum value to Arabic display name
const STRATEGY_LABELS: Record<SamplingStrategy, string> = {
  sequential: 'تدريب تسلسلي',
  uncertainty: 'تدريب التحدي',
  disagreement: 'أمثلة مثيرة للجدل',
}
```

### Alembic Migration Skeleton

```python
revision: str = "g9h0i1j2k3l4"
down_revision: Union[str, None] = "f8a9b0c1d2e3"  # last Phase 7 migration

def upgrade() -> None:
    # 1. Create new enum type via raw SQL (project convention)
    op.execute(
        "CREATE TYPE samplingstrategy AS ENUM ('sequential', 'uncertainty', 'disagreement')"
    )
    samplingstrategy = postgresql.ENUM(name="samplingstrategy", create_type=False)

    # 2. Add strategy column to training_sessions
    op.add_column(
        "training_sessions",
        sa.Column("strategy", samplingstrategy, nullable=False, server_default="sequential"),
    )

    # 3. Add ai_confidence to content_examples
    op.add_column(
        "content_examples",
        sa.Column("ai_confidence", sa.Float(), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("content_examples", "ai_confidence")
    op.drop_column("training_sessions", "strategy")
    op.execute("DROP TYPE IF EXISTS samplingstrategy")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Random example selection (`func.random()`) | Strategy-aware: sequential/uncertainty/disagreement | Phase 12 | Moderators practice on most educational examples rather than random ones |
| No visibility into which examples are hard | `ai_confidence` column caches per-example model difficulty | Phase 12 | Enables uncertainty sampling without repeated model inference |
| No cross-moderator disagreement tracking | Error rate aggregate over all `session_items` | Phase 12 | Surfaces systematically confusing examples for targeted practice |

**Deprecated/outdated after this phase:**
- The `func.random()` query in `create_session()` is replaced by `select_examples(db, user_id, strategy)` — it should not be retained as a code path.

---

## Open Questions

1. **Where to call the pre-compute script?**
   - What we know: The script must run after `alembic upgrade head` populates the new `ai_confidence` column. The `model_manager` must be available (models loaded).
   - What's unclear: Whether to document it as a manual post-migration step or wire it into a startup hook in `main.py` lifespan.
   - Recommendation: Document as a manual step for now (`python -m scripts.precompute_confidence`). Wiring into lifespan risks slow startup on each server restart. A future phase could add a `/api/admin/precompute` endpoint.

2. **What `down_revision` does the new migration chain to?**
   - What we know: The last migration is `f8a9b0c1d2e3` (Phase 7 bias audit). Phase 10 and 11 added no migrations.
   - What's unclear: Nothing — `f8a9b0c1d2e3` is confirmed as the correct `down_revision`.
   - Recommendation: Set `down_revision = "f8a9b0c1d2e3"`.

3. **Should `_serialize_session` expose `strategy`?**
   - What we know: `TrainingSession.strategy` will exist on the ORM object after the migration. `_serialize_session` currently omits it.
   - What's unclear: Nothing — it must be added.
   - Recommendation: Add `"strategy": session.strategy.value` to `_serialize_session()` result dict.

---

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection — `training.py` router, `training.py` model, `content_example.py`, `ml_models.py`, all Alembic migrations — confirmed patterns, column names, and enum conventions
- SQLAlchemy 2.0 `func.abs()`, `case()`, subquery join patterns — verified against project's existing usage of `func.random()`, `func.count()`, and subquery patterns in `create_session()` and audit router

### Secondary (MEDIUM confidence)
- Phase 3 migration (`c3d4e5f6a7b8`) — confirmed raw SQL enum creation is the project convention; generalizing this pattern to the new `samplingstrategy` enum is safe
- Phase 5 migration (`d4e5f6a7b8c9`) — confirmed `op.add_column` with `sa.Float()` nullable=True is the correct pattern for the `ai_confidence` column

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; all patterns present in existing code
- Architecture: HIGH — derived directly from existing code structure (training.py, models, migrations)
- Pitfalls: HIGH — Alembic enum double-create confirmed from project decision log; boolean NULL behavior confirmed from SQLAlchemy 2.0 docs

**Research date:** 2026-03-03
**Valid until:** 2026-04-03 (stable stack — 30 days)
