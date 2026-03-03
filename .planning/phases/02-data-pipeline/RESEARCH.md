# Phase 2: Data Pipeline — Research

**Researched:** 2026-03-02
**Domain:** Dataset ingestion, PostgreSQL enums, bulk loading, FastAPI export
**Confidence:** HIGH (stack) / MEDIUM (Let-Mi format) / HIGH (JHSC/OSACT5/L-HSAB)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**A. Data Sourcing**
- Seed script must work completely offline. No internet at seed time.
- All 4 datasets committed to repo as CSV/JSON in `mizan/backend/data/`.
- Target: 500+ examples total (~125+ per dataset).
- JHSC is not yet downloaded — plan must include Mendeley download step.

**B. Label Schema**
- `ContentLabel` enum: `hate`, `offensive`, `not_hate`, `spam`
- `HateType` enum: `race`, `religion`, `ideology`, `gender`, `disability`, `social_class`, `tribalism`, `refugee_related`, `political_affiliation`, `unknown`
- `hate_type = 'unknown'` for JHSC and L-HSAB (source doesn't specify type).
- `hate_type = null` for `offensive`, `not_hate`, `spam` rows.
- Jordanian-specific categories (`tribalism`, `refugee_related`, `political_affiliation`) reserved — zero seeded examples.
- JHSC "offensive" maps to `label=offensive, hate_type=null` (NOT to hate).

**C. JHSC Temporal Data (Observatory)**
- All 403,688 JHSC rows loaded into `jhsc_tweets` table.
- Observatory chart uses JHSC's own 4 labels (Negative/Neutral/Positive/Very positive) — no mapping to 9-category schema.
- No pre-aggregation table needed in Phase 2.

**D. Export API**
- `GET /api/export` endpoint, admin role required.
- `?format=csv` and `?format=json` both supported.
- Export schema covers all future columns — Phase 2 columns populated, later phases null.
- API endpoint, not CLI script.

### Claude's Discretion
- None specified — all decisions locked.

### Deferred Ideas (OUT OF SCOPE)
- Moderator training UI (Phase 3)
- MARBERT inference (Phase 4)
- AI explanations (Phase 5)
- Calibration scoring (Phase 6)
- Observatory chart rendering (Phase 7)
- Bias Auditor (Phase 7)
- Pre-aggregation performance tables (Phase 8)
</user_constraints>

---

## Summary

Phase 2 loads research-grade Arabic hate speech data into PostgreSQL and exposes it via a FastAPI export endpoint. Three of the four datasets (OSACT5, L-HSAB, JHSC) have confirmed column formats; Let-Mi requires a form-gated access request before files can be committed. The 403K-row JHSC load is the main engineering challenge — chunked Core inserts with psycopg2 are the right approach for this project's SQLAlchemy 2.0 + psycopg2-binary stack.

The enum handling in this project follows the same pattern as Phase 1 (`userrole` in the initial migration) — use `sa.Enum(...)` with a named type, create it explicitly in the migration before the table. Nullable enum columns are straightforward with `nullable=True`.

**Primary recommendation:** Use SQLAlchemy 2.0 `session.execute(insert(Model), list_of_dicts)` in 10,000-row chunks with `render_nulls=True` for the JHSC bulk load. Keep seed data in a standalone script (not in Alembic migrations) following the Phase 1 `seed.py` pattern.

---

## Dataset Formats

### 1. JHSC — Jordanian Hate Speech Corpus

**Source:** Mendeley Data, DOI: 10.17632/mcnzzpgrdj.2, CC BY 4.0
**Access:** Manual download from https://data.mendeley.com/datasets/mcnzzpgrdj/2 (click "Download All")
**Format:** CSV, UTF-8 encoded
**Files:**
- `annotated-hatetweets-4-classes_train.csv` — 302,766 rows
- `annotated-hatetweets-4-classes_test.csv` — 100,923 rows
- Combined: 403,688 rows

**Confirmed columns (from Mendeley page + PMC paper):**

| Column | Type | Notes |
|--------|------|-------|
| `Tweet id` | integer | Unique tweet ID; strip before training |
| `Text` | string | Arabic tweet text, preprocessed |
| `Label` | string | One of the 4 values below |

**Exact label values (case-sensitive strings from paper):**

| JHSC Label | Meaning | Maps to Mizan |
|-----------|---------|---------------|
| `Negative` | No hate speech | `not_hate` |
| `Neutral` | General/neutral tweet | `not_hate` (or keep as `spam` if desired — see note) |
| `Positive` | Hate speech (bullying, sarcasm, racism) | `hate`, `hate_type=unknown` |
| `Very positive` | Severe hate speech | `hate`, `hate_type=unknown` |

> **Note on "Neutral":** The paper describes neutral as "general tweet (add, prayer, no sentiment)" — closest to `not_hate`. The CONTEXT.md says Observatory uses JHSC's original labels verbatim. For the 500-example seed, sample only Negative/Positive/Very positive rows to have meaningful training data.

> **Label distribution (from PMC paper):** 149,706 offensive (Positive), 126,297 offensive (secondary breakdown), 7,034 very offensive (Very positive), 120,651 neutral (Neutral).

**Tweet years:** 2014–2022

**Download steps (must be in Phase 2 plan):**
1. Visit https://data.mendeley.com/datasets/mcnzzpgrdj/2
2. Click "Download All" — downloads a .zip file (~few hundred MB)
3. Unzip — contains the two CSV files
4. Place both at `mizan/backend/data/jhsc/`
5. Commit to repo (check .gitignore does not block .csv in data/)

---

### 2. OSACT5 — Arabic Hate Speech 2022 Shared Task

**Source:** QCRI / Arabic Hate Speech 2022 Shared Task
**Access:** Direct download (no registration required)
- Train: https://alt.qcri.org/resources/OSACT2022/OSACT2022-sharedTask-train.txt
- Dev: https://alt.qcri.org/resources1/OSACT2022/OSACT2022-sharedTask-dev.txt
**Format:** Tab-separated (.txt, no header row)
**License:** Research use

**Confirmed columns (verified by fetching dev file directly):**

| Position | Column | Values |
|----------|--------|--------|
| 0 | `id` | numeric row ID |
| 1 | `text` | Arabic tweet text (emojis, @USER, URL markers) |
| 2 | `OFF_label` | `OFF` or `NOT_OFF` |
| 3 | `HS_label` | `NOT_HS`, `HS1`, `HS2`, `HS3`, `HS4`, `HS5`, `HS6` |
| 4 | `VLG_label` | `NOT_VLG` or `VLG` |
| 5 | `VIO_label` | `NOT_VIO` or `VIO` |

**Confirmed example row (directly observed):**
```
1	@USER ردينا ع التطنز 😏👊🏻	OFF	NOT_HS	NOT_VLG	NOT_VIO
```

**Hate type mapping (HS codes to Mizan enum):**

| OSACT5 Code | Meaning | Mizan `hate_type` |
|-------------|---------|-------------------|
| `HS1` | Race/ethnicity/nationality | `race` |
| `HS2` | Religion/belief | `religion` |
| `HS3` | Ideology | `ideology` |
| `HS4` | Disability/disease | `disability` |
| `HS5` | Social class | `social_class` |
| `HS6` | Gender | `gender` |

**Label mapping to Mizan schema:**

| OFF_label | HS_label | Mizan `label` | Mizan `hate_type` |
|-----------|----------|---------------|-------------------|
| `NOT_OFF` | `NOT_HS` | `not_hate` | null |
| `OFF` | `NOT_HS` | `offensive` | null |
| `OFF` | `HS1`–`HS6` | `hate` | per table above |

**Read pattern:**
```python
import pandas as pd
df = pd.read_csv(
    "data/osact5/OSACT2022-sharedTask-train.txt",
    sep="\t",
    header=None,
    names=["id", "text", "OFF_label", "HS_label", "VLG_label", "VIO_label"],
    encoding="utf-8",
)
```

---

### 3. L-HSAB — Levantine Hate Speech and Abusive Language

**Source:** GitHub, Hala Mulki, 2019
**Access:** https://github.com/Hala-Mulki/L-HSAB-First-Arabic-Levantine-HateSpeech-Dataset (public)
**File:** `Dataset/L-HSAB` (no extension — it is a TSV file)
**Format:** Tab-separated, no header row, UTF-8
**Size:** 5,846 Syrian/Lebanese Arabic tweets

**Confirmed columns (verified by fetching raw file):**

| Position | Column | Values |
|----------|--------|--------|
| 0 | `Tweet` | Arabic tweet text |
| 1 | `Class` | `normal`, `abusive`, `hate` |

**Confirmed example rows (directly observed):**
- Tweet text + tab + `abusive`
- Tweet text + tab + `normal`

**Label mapping to Mizan schema:**

| L-HSAB `Class` | Mizan `label` | Mizan `hate_type` |
|----------------|---------------|-------------------|
| `normal` | `not_hate` | null |
| `abusive` | `offensive` | null |
| `hate` | `hate` | `unknown` |

**Read pattern:**
```python
df = pd.read_csv(
    "data/l-hsab/L-HSAB",
    sep="\t",
    header=None,
    names=["text", "class_label"],
    encoding="utf-8",
)
```

---

### 4. Let-Mi — Arabic Levantine Misogyny Dataset

**Source:** bilalghanem/let-mi, WANLP 2021, Hala Mulki + Bilal Ghanem
**Access:** GATED — requires form submission at https://forms.gle/pKywZKRHBoLkEPqBA
**Format:** Not confirmed (likely TSV based on similar datasets from same authors)
**Size:** ~9,833 Arabic/dialectal Levantine tweets

**Confirmed label schema (from ArMI 2021 shared task page and WANLP paper):**

Sub-task A (binary):
- `Misogyny` — misogynistic content
- `None` — not misogynistic

Sub-task B (fine-grained, 7 categories):
- `Damn` — cursing/damning
- `Der` — derailing (justifying abuse of women)
- `Disc` — discrediting (slurs)
- `Dom` — dominance (male superiority)
- `Harass` — sexual harassment
- `Obj` — stereotyping and objectification
- `Vio` — threat of violence
- `None` — no misogynistic behavior

**Likely column names** (LOW confidence — inferred from paper, not confirmed by file inspection):
- `id` (tweet ID)
- `text` (tweet text)
- `misogyny` (`Misogyny` or `None`)
- `category` (Sub-task B label)

**CRITICAL NOTE:** Files are access-controlled. The planner MUST include a step: request access at the form URL, await approval, then place files at `mizan/backend/data/let-mi/`. Until then, the Let-Mi portion of the seed cannot be committed.

**Fallback plan if Let-Mi access is delayed:** Substitute with additional OSACT5 rows (gender hate, HS6) to reach the 500+ example target. Label them with `gender` hate_type from OSACT5. Document the substitution in the data README.

**Label mapping to Mizan schema:**

| Let-Mi `misogyny` | Let-Mi `category` | Mizan `label` | Mizan `hate_type` |
|-------------------|-------------------|---------------|-------------------|
| `None` | `None` | `not_hate` | null |
| `Misogyny` | any | `hate` | `gender` |

---

## Standard Stack

### Core (already in requirements.txt)
| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| sqlalchemy | 2.0.35 | ORM + Core inserts | Use Core insert() for bulk loads |
| alembic | 1.13.3 | Schema migrations | New migration for Phase 2 tables |
| psycopg2-binary | 2.9.9 | PostgreSQL driver | Uses execute_values internally via SQLAlchemy 2.0 |
| fastapi | 0.115.0 | Export endpoint | StreamingResponse for file downloads |

### New Dependencies to Add
| Library | Purpose | Install |
|---------|---------|---------|
| pandas | CSV parsing + label mapping | `pip install pandas==2.2.3` |
| tqdm | Progress bar for 403K insert | `pip install tqdm==4.66.5` |

> **pandas note:** pandas is the standard tool for reading TSV/CSV with mixed encodings and null handling. For 403K rows it is appropriate — read in chunks of 50K using `pd.read_csv(..., chunksize=50000)` to avoid loading all 403K into memory at once.

**Installation:**
```bash
pip install pandas==2.2.3 tqdm==4.66.5
```

Add both to `requirements.txt`.

---

## Architecture Patterns

### Recommended File Layout

```
mizan/backend/
├── data/
│   ├── README.md                        # Documents sources, licenses, columns
│   ├── jhsc/
│   │   ├── annotated-hatetweets-4-classes_train.csv
│   │   └── annotated-hatetweets-4-classes_test.csv
│   ├── osact5/
│   │   ├── OSACT2022-sharedTask-train.txt
│   │   └── OSACT2022-sharedTask-dev.txt
│   ├── l-hsab/
│   │   └── L-HSAB
│   └── let-mi/
│       └── (place files here after form approval)
├── app/
│   ├── models/
│   │   ├── content_example.py           # ContentExample + enums
│   │   └── jhsc_tweet.py                # JhscTweet model
│   ├── routers/
│   │   └── export.py                    # GET /api/export
│   └── schemas/
│       └── export.py                    # ExportRow pydantic schema
├── scripts/
│   ├── seed.py                          # Phase 1 (unchanged)
│   ├── seed_content.py                  # Phase 2: 500+ examples
│   └── seed_jhsc.py                     # Phase 2: 403K JHSC rows
└── alembic/
    └── versions/
        └── XXXX_phase2_data_tables.py   # New migration
```

---

### Pattern 1: SQLAlchemy Enum Definition (matching Phase 1 style)

The project uses `sa.Enum(...)` with named PostgreSQL types (see `userrole` in Phase 1 migration). Follow the same pattern.

**Model definition:**
```python
# Source: Phase 1 pattern (user.py) + SQLAlchemy 2.0 docs
import enum
from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class ContentLabel(str, enum.Enum):
    hate = "hate"
    offensive = "offensive"
    not_hate = "not_hate"
    spam = "spam"

class HateType(str, enum.Enum):
    race = "race"
    religion = "religion"
    ideology = "ideology"
    gender = "gender"
    disability = "disability"
    social_class = "social_class"
    tribalism = "tribalism"
    refugee_related = "refugee_related"
    political_affiliation = "political_affiliation"
    unknown = "unknown"

class ContentExample(Base):
    __tablename__ = "content_examples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    source_dataset = Column(String(50), nullable=False)  # jhsc/osact5/l-hsab/let-mi
    dialect = Column(String(50), nullable=True)           # jordanian/levantine
    ground_truth_label = Column(Enum(ContentLabel), nullable=False)
    hate_type = Column(Enum(HateType), nullable=True)     # null for non-hate rows
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**Alembic migration (follows Phase 1 pattern exactly):**
```python
# Source: Phase 1 migration a998e4136824, adapted
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Create enum types first
    contentlabel = sa.Enum(
        'hate', 'offensive', 'not_hate', 'spam',
        name='contentlabel'
    )
    hatetype = sa.Enum(
        'race', 'religion', 'ideology', 'gender', 'disability',
        'social_class', 'tribalism', 'refugee_related',
        'political_affiliation', 'unknown',
        name='hatetype'
    )
    contentlabel.create(op.get_bind())
    hatetype.create(op.get_bind())

    op.create_table('content_examples',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('source_dataset', sa.String(50), nullable=False),
        sa.Column('dialect', sa.String(50), nullable=True),
        sa.Column('ground_truth_label',
                  sa.Enum('hate', 'offensive', 'not_hate', 'spam',
                          name='contentlabel', create_type=False),
                  nullable=False),
        sa.Column('hate_type',
                  sa.Enum('race', 'religion', 'ideology', 'gender',
                          'disability', 'social_class', 'tribalism',
                          'refugee_related', 'political_affiliation', 'unknown',
                          name='hatetype', create_type=False),
                  nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    # ... jhsc_tweets table below

def downgrade() -> None:
    op.drop_table('content_examples')
    op.drop_table('jhsc_tweets')
    sa.Enum(name='contentlabel').drop(op.get_bind())
    sa.Enum(name='hatetype').drop(op.get_bind())
    sa.Enum(name='jhsclabel').drop(op.get_bind())
```

> **Key detail:** `create_type=False` on the `Enum()` inside `op.create_table()` prevents double-creation. The explicit `.create()` calls at the top of `upgrade()` create the PostgreSQL type first. This is the correct pattern — confirmed by `code.keplergrp.com` and consistent with Phase 1.

---

### Pattern 2: JHSC Tweets Table

```python
class JhscLabel(str, enum.Enum):
    negative = "Negative"
    neutral = "Neutral"
    positive = "Positive"
    very_positive = "Very positive"

class JhscTweet(Base):
    __tablename__ = "jhsc_tweets"

    id = Column(Integer, primary_key=True)   # use JHSC's own tweet_id
    text = Column(Text, nullable=True)        # may be None if Twitter deleted tweet
    label = Column(Enum(JhscLabel), nullable=False)
    tweet_year = Column(Integer, nullable=True)
    tweet_month = Column(Integer, nullable=True)
```

> **Why integer PK:** JHSC provides a numeric Tweet id column. Use it directly to make re-seeding idempotent (check `if not exists by id`).

---

### Pattern 3: Bulk Insert 403K Rows (SQLAlchemy 2.0 Core)

**This is the correct pattern for 403K rows with this project's stack (SQLAlchemy 2.0 + psycopg2-binary).**

```python
# Source: SQLAlchemy 2.0 docs (docs.sqlalchemy.org/en/20/orm/queryguide/dml.html)
import pandas as pd
from sqlalchemy import insert
from tqdm import tqdm
from app.database import engine
from app.models.jhsc_tweet import JhscTweet

CHUNK_SIZE = 10_000

def seed_jhsc(csv_path: str):
    reader = pd.read_csv(
        csv_path,
        chunksize=CHUNK_SIZE,
        encoding="utf-8",
        names=["tweet_id", "text", "label"],  # actual header row in file — skip it
        skiprows=1,
    )
    with engine.begin() as conn:
        for chunk in tqdm(reader, desc="Loading JHSC"):
            rows = []
            for _, row in chunk.iterrows():
                rows.append({
                    "id": int(row["tweet_id"]),
                    "text": row["text"] if pd.notna(row["text"]) else None,
                    "label": row["label"],
                    "tweet_year": None,   # extract from tweet_id if needed
                    "tweet_month": None,
                })
            conn.execute(
                insert(JhscTweet).execution_options(render_nulls=True),
                rows,
            )
```

> **render_nulls=True:** Without this, rows with different null patterns are grouped into separate batches (very slow for 403K rows). Always use it for bulk inserts where some columns may be null.

> **engine.begin() vs Session:** For raw bulk inserts without ORM bookkeeping, use `engine.begin()` (Core connection). This avoids Session overhead and is appropriate when you do not need the inserted objects back.

> **Chunk size:** 10,000 rows per chunk is safe for psycopg2's execute_values (which SQLAlchemy 2.0 uses internally for PostgreSQL). For 400K rows this is 40 round trips — fast enough (typically ~30-60 seconds total).

---

### Pattern 4: FastAPI Export Endpoint

```python
# Source: FastAPI docs (fastapi.tiangolo.com/advanced/custom-response/)
# + Phase 1 auth pattern (deps.py require_admin)
import csv
import io
import json
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/export", tags=["export"])

def row_to_dict(example) -> dict:
    return {
        "example_id": str(example.id),
        "text": example.text,
        "source_dataset": example.source_dataset,
        "dialect": example.dialect,
        "ground_truth_label": example.ground_truth_label.value if example.ground_truth_label else None,
        "hate_type": example.hate_type.value if example.hate_type else None,
        # Phase 3+ columns — null in Phase 2
        "moderator_id": None,
        "moderator_label": None,
        "moderator_agree_ai": None,
        # Phase 4+ columns
        "ai_label": None,
        "ai_confidence": None,
        # Phase 6+ columns
        "calibration_score": None,
    }

def generate_csv(rows):
    """Generator: yields CSV lines from a list of dicts."""
    buffer = io.StringIO()
    fieldnames = [
        "example_id", "text", "source_dataset", "dialect",
        "ground_truth_label", "hate_type",
        "moderator_id", "moderator_label", "moderator_agree_ai",
        "ai_label", "ai_confidence", "calibration_score",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    yield buffer.getvalue()
    buffer.truncate(0)
    buffer.seek(0)
    for row in rows:
        writer.writerow(row)
        yield buffer.getvalue()
        buffer.truncate(0)
        buffer.seek(0)

@router.get("")
def export_dataset(
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    examples = db.query(ContentExample).all()
    rows = [row_to_dict(e) for e in examples]

    if format == "csv":
        return StreamingResponse(
            generate_csv(rows),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=mizan-export.csv"},
        )
    else:
        def generate_json():
            yield json.dumps(rows, ensure_ascii=False).encode("utf-8")
        return StreamingResponse(
            generate_json(),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=mizan-export.json"},
        )
```

> **ensure_ascii=False:** Critical for Arabic text. Without this, Arabic characters are escaped as `\uXXXX`.

---

### Pattern 5: Indexes for Observatory Queries

The Observatory chart queries `jhsc_tweets` by year and month. Add indexes in the same Alembic migration.

```python
# In upgrade(), after creating jhsc_tweets table:
op.create_index("ix_jhsc_tweets_year_month", "jhsc_tweets", ["tweet_year", "tweet_month"])
op.create_index("ix_jhsc_tweets_label", "jhsc_tweets", ["label"])

# In downgrade(), before dropping table:
op.drop_index("ix_jhsc_tweets_year_month", table_name="jhsc_tweets")
op.drop_index("ix_jhsc_tweets_label", table_name="jhsc_tweets")
```

> **No CONCURRENTLY needed:** Standard `CREATE INDEX` is fine here because the table is empty at migration time. `CONCURRENTLY` is only needed when adding indexes to live tables with data. Running the migration against an empty table will always be fast.

---

### Pattern 6: Seed Script Structure (Idempotent, follows Phase 1)

```python
# scripts/seed_content.py — 500+ examples, idempotent
with Session(engine) as session:
    existing = session.query(ContentExample).first()
    if existing:
        print("Content examples already seeded, skipping.")
        sys.exit(0)

    # Load each dataset, map labels, bulk insert
    rows = []
    rows += load_jhsc_sample("data/jhsc/annotated-hatetweets-4-classes_train.csv", n=125)
    rows += load_osact5("data/osact5/OSACT2022-sharedTask-train.txt", n=125)
    rows += load_lhsab("data/l-hsab/L-HSAB", n=125)
    rows += load_letmi("data/let-mi/", n=125)   # skip if file missing

    session.execute(
        insert(ContentExample).execution_options(render_nulls=True),
        rows,
    )
    session.commit()
    print(f"Seeded {len(rows)} content examples.")
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSV/TSV parsing | Custom file reader | `pandas.read_csv` | Handles encoding, quoting, mixed line endings |
| PostgreSQL enum lifecycle | Raw ALTER TYPE SQL | `sa.Enum(...).create()` + `create_type=False` | Prevents double-creation, handles downgrade |
| Bulk insert batching | Manual batch loops | `session.execute(insert(Model), list_of_dicts)` with `render_nulls=True` | SQLAlchemy 2.0 uses execute_values internally for psycopg2 |
| Progress reporting | Print statements every N rows | `tqdm(reader, desc="...")` | Works with pandas chunked reader |
| Streaming file download | BytesIO + full load | `StreamingResponse` + generator | Memory-safe for large exports |
| Arabic JSON encoding | `json.dumps(...)` default | `json.dumps(..., ensure_ascii=False)` | Preserves Arabic script |

---

## Common Pitfalls

### Pitfall 1: Double-Creation of PostgreSQL Enum Types
**What goes wrong:** Alembic's autogenerate may call `CREATE TYPE contentlabel` twice — once from the explicit `.create()` call and once when the Column definition sees a new Enum. This causes `ERROR: type "contentlabel" already exists`.
**Why it happens:** SQLAlchemy Enum tracks creation state per-connection, but Alembic autogenerate emits `create_type=True` by default.
**How to avoid:** Always use `create_type=False` inside `op.create_table()` column definitions, and call `.create(op.get_bind())` manually at the top of `upgrade()`. See Pattern 1 code above.
**Warning signs:** Migration fails with "type already exists" on second run or after rollback.

### Pitfall 2: Enum Values in Python vs PostgreSQL
**What goes wrong:** Python Enum member `ContentLabel.not_hate` has `.value = "not_hate"`, but if PostgreSQL type was created with a different case (e.g. `NOT_HATE`), comparisons silently fail or throw.
**How to avoid:** Always define Python Enum values in lowercase to match the strings passed to `sa.Enum(...)` in the migration. They must be identical strings.

### Pitfall 3: render_nulls=False (default) Causes Slow Bulk Inserts
**What goes wrong:** With default `render_nulls=False`, rows where `hate_type=None` and rows where `hate_type` is set are batched separately. For 403K rows with mixed nulls, this can create thousands of separate INSERT statements.
**How to avoid:** Use `.execution_options(render_nulls=True)` on any bulk insert where nullable columns are present.
**Warning signs:** Seed script taking > 5 minutes, or seeing many small INSERT batches in PostgreSQL logs.

### Pitfall 4: JHSC Column Header Confusion
**What goes wrong:** The JHSC CSV files DO have a header row ("Tweet id", "Text", "Label"). Pandas `read_csv` without `header=0` (the default) will use the first row as column names. But the column names contain spaces ("Tweet id" not "tweet_id"), which requires careful access.
**How to avoid:** Either let pandas use the header (`header=0`, default) and access columns as `df["Tweet id"]`, or pass `names=[...]` with `skiprows=1` to rename them on load.

### Pitfall 5: JHSC "Positive" vs "Very positive" Space in Value
**What goes wrong:** The JHSC label "Very positive" contains a space. If your enum is defined as `very_positive` without the space, the string comparison fails when mapping.
**How to avoid:** Either store JHSC's original label strings as-is in `jhsc_tweets` (use `JhscLabel.very_positive = "Very positive"` as shown in Pattern 2), or normalise to lowercase/underscore at load time before inserting.

### Pitfall 6: OSACT5 File Has No Header Row
**What goes wrong:** `pd.read_csv(path, sep="\t")` will treat the first data row as column names (e.g., a numeric ID "1" becomes the column header).
**How to avoid:** Always pass `header=None` and explicit `names=[...]` for OSACT5. See Pattern reading example in dataset section.

### Pitfall 7: Arabic Text Encoding in JSON Export
**What goes wrong:** `json.dumps(rows)` with default settings escapes Arabic characters to `\u0645\u0631\u062d\u0628\u0627` — technically valid JSON but unreadable and bloated.
**How to avoid:** Always use `json.dumps(rows, ensure_ascii=False).encode("utf-8")` in the streaming generator.

### Pitfall 8: Let-Mi Files Not Available
**What goes wrong:** Planner expects all 4 datasets to be committable. Let-Mi is access-gated. If the form isn't submitted before Phase 2 starts, the 500+ total target cannot be met from 4 datasets.
**How to avoid:** Submit the form at https://forms.gle/pKywZKRHBoLkEPqBA immediately. Include a fallback in seed_content.py: if `data/let-mi/` is empty, log a warning and skip (accept ~375 examples from the other 3 datasets), OR supplement with extra OSACT5 gender-hate rows.

---

## State of the Art

| Old Approach | Current Approach | Impact for This Project |
|--------------|------------------|------------------------|
| `session.bulk_insert_mappings()` | `session.execute(insert(Model), list_of_dicts)` | SQLAlchemy 2.0 deprecated bulk_insert_mappings in favor of the new pattern; use the new way |
| Manual `op.execute("CREATE TYPE ...")` | `sa.Enum(...).create(op.get_bind())` | Cleaner, handles downgrade via `.drop()` |
| `StreamingResponse(iter([...]))` | `StreamingResponse(generator_function())` | Generator pattern is more memory-efficient for large exports |

---

## Alembic: Schema vs Seed Data — Decision

**Use separate seed scripts, NOT Alembic migrations, for the 500+ examples and 403K JHSC rows.**

**Rationale:**
- Alembic community consensus: seed data belongs outside the migration revision tree (confirmed from github.com/sqlalchemy/alembic/discussions/972)
- Data "downgrade" (removing 403K rows) is impossible without knowing original state
- This project already has this pattern: `scripts/seed.py` for Phase 1 institutions/users
- The Phase 2 migration handles ONLY schema (tables, types, indexes) — zero data

**Execution order for Phase 2:**
```bash
# 1. Apply schema migration
docker compose exec backend alembic upgrade head

# 2. Download JHSC manually (one-time, developer step)
# Place files in mizan/backend/data/jhsc/

# 3. Seed 500+ training examples (fast — ~seconds)
docker compose exec backend python scripts/seed_content.py

# 4. Load all 403K JHSC rows (slow — ~1-2 minutes)
docker compose exec backend python scripts/seed_jhsc.py
```

---

## JHSC Download Guide (Step-by-Step)

This must appear in the Phase 2 plan:

1. Open https://data.mendeley.com/datasets/mcnzzpgrdj/2 in a browser
2. Optionally sign in (sign-in is not required for CC BY 4.0 datasets)
3. Click the "Download All" button — this downloads `mcnzzpgrdj_2.zip` (~size: expect hundreds of MB)
4. Unzip: produces `annotated-hatetweets-4-classes_train.csv` and `annotated-hatetweets-4-classes_test.csv`
5. Create `mizan/backend/data/jhsc/` if it does not exist
6. Move both CSV files into `mizan/backend/data/jhsc/`
7. Verify: `wc -l mizan/backend/data/jhsc/annotated-hatetweets-4-classes_train.csv` should print 302,767 (302,766 rows + 1 header)
8. Add to git: `git add mizan/backend/data/jhsc/` — verify .gitignore does not exclude .csv in data/
9. Commit with message: `data: add JHSC training corpus (302K rows, CC BY 4.0)`

**Note on repo size:** Two CSV files for JHSC will be large (~100-300MB). If repo size is a concern, consider adding to `.gitattributes` for Git LFS, or document in README that JHSC must be downloaded manually (keeping files in `.gitignore`). For a hackathon demo, committing directly is simpler.

---

## Open Questions

1. **JHSC actual column header row**
   - What we know: Mendeley page describes columns as "Tweet id", "Text", "Label" — likely these are the exact header strings.
   - What's unclear: Exact capitalisation and whether headers use space or underscore.
   - Recommendation: When downloading, immediately run `head -1 annotated-hatetweets-4-classes_train.csv` and document the actual header.

2. **Let-Mi file format (exact columns)**
   - What we know: Binary label is `Misogyny`/`None`; 7 fine-grained categories. Dataset is access-gated.
   - What's unclear: Exact file name, whether it is one file or split train/test, exact column names.
   - Recommendation: Submit form now. If delayed, use OSACT5 HS6 (gender) rows as Let-Mi substitute and document clearly.

3. **JHSC date extraction**
   - What we know: Tweets span 2014–2022. A `tweet_year`/`tweet_month` column is wanted.
   - What's unclear: Whether the JHSC CSV includes a date column, or only a numeric tweet_id (from which a rough date could be inferred via Twitter Snowflake ID).
   - Recommendation: Check when downloading. If no date column, leave `tweet_year`/`tweet_month` as null in Phase 2 and note it as a gap for the Observatory.

4. **Git LFS for 300MB+ JHSC files**
   - What we know: The hackathon is a demo — JHSC files need to be in repo or loadable offline.
   - What's unclear: Whether the Git repo has LFS configured.
   - Recommendation: Check `git lfs status`. If not configured, add a `data/jhsc/.gitkeep` and document JHSC as a "download before seeding" step with a `scripts/download_jhsc.py` helper that automates the Mendeley download.

---

## Sources

### Primary (HIGH confidence)
- Direct fetch of `https://alt.qcri.org/resources1/OSACT2022/OSACT2022-sharedTask-dev.txt` — confirmed 6-column TSV format, exact label values
- `https://data.mendeley.com/datasets/mcnzzpgrdj/2` — confirmed CSV format, column names, file names
- `https://github.com/Hala-Mulki/L-HSAB-First-Arabic-Levantine-HateSpeech-Dataset/blob/master/Dataset/L-HSAB` — confirmed 2-column TSV, label values (`normal`/`abusive`/`hate`)
- `https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html` — confirmed `session.execute(insert(...))` pattern + `render_nulls=True`
- `https://fastapi.tiangolo.com/advanced/custom-response/` — confirmed StreamingResponse + Content-Disposition pattern
- `https://github.com/sqlalchemy/alembic/issues/277` — confirmed `autocommit_block()` + `postgresql_concurrently=True` pattern
- `https://sites.google.com/view/arabichate2022/home` — confirmed OSACT5 column names (id, text, OFF_label, HS_label, VLG_label, VIO_label)

### Secondary (MEDIUM confidence)
- `https://pmc.ncbi.nlm.nih.gov/articles/PMC10912174/` — JHSC label values (Negative/Neutral/Positive/Very positive), tweet years 2014-2022
- `https://sites.google.com/view/armi2021/` — Let-Mi SubTask A/B label values
- Phase 1 project code (`user.py`, `a998e4136824_initial_schema.py`) — confirmed existing enum + migration pattern to follow

### Tertiary (LOW confidence — needs file inspection to verify)
- Let-Mi column names (`id`, `text`, `misogyny`, `category`) — inferred from WANLP 2021 paper description, not confirmed by file inspection
- JHSC date column existence — not mentioned in paper or Mendeley page, uncertain

---

## Metadata

**Confidence breakdown:**
- Dataset formats (JHSC, OSACT5, L-HSAB): HIGH — confirmed by direct file fetch or official dataset page
- Dataset formats (Let-Mi): LOW — access-gated, file not inspectable
- SQLAlchemy bulk insert pattern: HIGH — confirmed by official docs
- Alembic enum pattern: HIGH — confirmed by official source + consistent with Phase 1 code
- FastAPI StreamingResponse: HIGH — confirmed by official docs
- Index strategy: HIGH — confirmed by Alembic issue tracker

**Research date:** 2026-03-02
**Valid until:** 2026-06-01 (datasets are static academic releases; stack versions pinned in requirements.txt)
