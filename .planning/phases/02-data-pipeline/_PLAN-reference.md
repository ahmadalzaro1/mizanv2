# Phase 2: Data Pipeline — PLAN

> **Goal**: The database contains 500+ pre-seeded Arabic examples with ground-truth labels drawn from 4 datasets, AND all 403K JHSC tweets are loaded and queryable for the Observatory, AND a GET /api/export endpoint exists.
> **Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, OBS-01
> **Context file**: `.planning/phases/2-CONTEXT.md` — read this before executing any plan.
> **Stack**: Python/FastAPI (backend), PostgreSQL (db), pandas, tqdm, SQLAlchemy 2.0
> **Working dir**: `/Users/ahmadalzaro/Desktop/AI Hatespeech Project/`

---

## Execution Order

Plans must be executed in this order — each depends on the previous:

```
Plan 2.1 (schema migration)
  → Plan 2.2 (dataset acquisition — HUMAN STEP, cannot be automated)
    → Plan 2.3 (seed 500+ examples)
      → Plan 2.4 (load 403K JHSC rows)
        → Plan 2.5 (export API endpoint)
```

**All paths in this document are absolute from repo root:**
`/Users/ahmadalzaro/Desktop/AI Hatespeech Project/`

---

## Plan 2.1 — Database Schema Migration

**Requirement**: DATA-01, OBS-01
**Goal**: Alembic migration creates `content_examples` and `jhsc_tweets` tables with all enums and indexes. Two new SQLAlchemy model files created. `alembic upgrade head` runs without error.

---

### Files to Create/Modify

- `mizan/backend/alembic/versions/b1f2c3d4e5f6_phase2_data_tables.py` — new Alembic migration
- `mizan/backend/app/models/content_example.py` — ContentExample ORM model + ContentLabel/HateType enums
- `mizan/backend/app/models/jhsc_tweet.py` — JhscTweet ORM model + JhscLabel enum

---

### Steps

#### Step 1: Create `mizan/backend/app/models/content_example.py`

Exact file contents:

```python
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum
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
    source_dataset = Column(String(50), nullable=False)  # jhsc / osact5 / l-hsab / let-mi
    dialect = Column(String(50), nullable=True)           # jordanian / levantine
    ground_truth_label = Column(
        Enum(ContentLabel, name="contentlabel", create_constraint=True),
        nullable=False,
    )
    hate_type = Column(
        Enum(HateType, name="hatetype", create_constraint=True),
        nullable=True,  # null for offensive / not_hate / spam rows
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**Do NOT** call `ContentLabel.create()` or `HateType.create()` here — enum creation happens in the Alembic migration only.

#### Step 2: Create `mizan/backend/app/models/jhsc_tweet.py`

Exact file contents:

```python
import enum
from sqlalchemy import Column, Integer, Text, Enum
from app.database import Base


class JhscLabel(str, enum.Enum):
    # Values are EXACT strings from JHSC CSV (confirmed by file inspection — all lowercase)
    negative = "negative"
    neutral = "neutral"
    positive = "positive"
    very_positive = "very positive"


class JhscTweet(Base):
    __tablename__ = "jhsc_tweets"

    id = Column(Integer, primary_key=True)  # JHSC's own Tweet id — used for idempotent re-seed
    text = Column(Text, nullable=True)       # May be None if tweet was deleted
    label = Column(
        Enum(JhscLabel, name="jhsclabel", create_constraint=True),
        nullable=False,
    )
    tweet_year = Column(Integer, nullable=True)   # extracted from CSV date column if present
    tweet_month = Column(Integer, nullable=True)  # extracted from CSV date column if present
```

**Why integer PK**: JHSC provides numeric Tweet id — using it directly makes re-runs idempotent (conflict on duplicate id).

#### Step 3: Create the Alembic migration

Run inside the backend container to generate a migration skeleton:

```bash
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec backend alembic revision --rev-id b1f2c3d4e5f6 \
  -m "phase2 data tables"
```

Then open the generated file at `mizan/backend/alembic/versions/b1f2c3d4e5f6_phase2_data_tables.py` and replace its entire contents with:

```python
"""phase2 data tables

Revision ID: b1f2c3d4e5f6
Revises: a998e4136824
Create Date: 2026-03-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b1f2c3d4e5f6"
down_revision: Union[str, None] = "a998e4136824"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Create enum types FIRST, before any table that uses them ---
    # Pattern: explicit .create() then create_type=False inside op.create_table()
    # Source: Phase 1 migration pattern (userrole enum)
    contentlabel = sa.Enum(
        "hate", "offensive", "not_hate", "spam",
        name="contentlabel",
    )
    hatetype = sa.Enum(
        "race", "religion", "ideology", "gender", "disability",
        "social_class", "tribalism", "refugee_related",
        "political_affiliation", "unknown",
        name="hatetype",
    )
    jhsclabel = sa.Enum(
        "negative", "neutral", "positive", "very positive",
        name="jhsclabel",
    )
    contentlabel.create(op.get_bind())
    hatetype.create(op.get_bind())
    jhsclabel.create(op.get_bind())

    # --- content_examples table ---
    op.create_table(
        "content_examples",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("source_dataset", sa.String(50), nullable=False),
        sa.Column("dialect", sa.String(50), nullable=True),
        sa.Column(
            "ground_truth_label",
            sa.Enum(
                "hate", "offensive", "not_hate", "spam",
                name="contentlabel",
                create_type=False,  # type already created above
            ),
            nullable=False,
        ),
        sa.Column(
            "hate_type",
            sa.Enum(
                "race", "religion", "ideology", "gender", "disability",
                "social_class", "tribalism", "refugee_related",
                "political_affiliation", "unknown",
                name="hatetype",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- jhsc_tweets table ---
    op.create_table(
        "jhsc_tweets",
        sa.Column("id", sa.Integer(), nullable=False),   # JHSC's Tweet id
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column(
            "label",
            sa.Enum(
                "negative", "neutral", "positive", "very positive",
                name="jhsclabel",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("tweet_year", sa.Integer(), nullable=True),
        sa.Column("tweet_month", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- Indexes for Observatory chart queries ---
    # No CONCURRENTLY needed — table is empty at migration time
    op.create_index("ix_jhsc_tweets_year_month", "jhsc_tweets", ["tweet_year", "tweet_month"])
    op.create_index("ix_jhsc_tweets_label", "jhsc_tweets", ["label"])


def downgrade() -> None:
    op.drop_index("ix_jhsc_tweets_label", table_name="jhsc_tweets")
    op.drop_index("ix_jhsc_tweets_year_month", table_name="jhsc_tweets")
    op.drop_table("jhsc_tweets")
    op.drop_table("content_examples")
    sa.Enum(name="jhsclabel").drop(op.get_bind())
    sa.Enum(name="hatetype").drop(op.get_bind())
    sa.Enum(name="contentlabel").drop(op.get_bind())
```

#### Step 4: Apply the migration

```bash
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec backend alembic upgrade head
```

Expected output ends with: `Running upgrade a998e4136824 -> b1f2c3d4e5f6, phase2 data tables`

---

### Verification

Run inside the backend container:

```bash
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "\dt content_examples; \dt jhsc_tweets; \dT+ contentlabel; \dT+ hatetype; \dT+ jhsclabel;"
```

Expected: All three tables listed, all three enum types listed with their correct values.

```bash
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "\di ix_jhsc_tweets_year_month; \di ix_jhsc_tweets_label;"
```

Expected: Both indexes listed.

---

### Done

- `content_examples` and `jhsc_tweets` tables exist in PostgreSQL
- `contentlabel`, `hatetype`, `jhsclabel` enum types exist in PostgreSQL
- `jhsclabel` values include exact strings `"Negative"`, `"Neutral"`, `"Positive"`, `"Very positive"` (with space)
- `ix_jhsc_tweets_year_month` and `ix_jhsc_tweets_label` indexes exist
- `alembic upgrade head` is idempotent (running twice does not error)

---

## Plan 2.2 — Dataset Acquisition & Directory Setup

**Requirement**: DATA-01, DATA-02, DATA-03, DATA-04
**Goal**: All dataset files are present in `mizan/backend/data/`, a README documents sources and licenses, and requirements.txt includes pandas and tqdm.

**NOTE: This plan requires human actions to download files. Claude can create the directory structure and README — dataset downloads must be done manually by the developer.**

---

### Files to Create/Modify

- `mizan/backend/data/README.md` — dataset sources, licenses, column formats
- `mizan/backend/data/jhsc/` — directory (JHSC files placed here manually)
- `mizan/backend/data/osact5/` — directory (OSACT5 files placed here manually)
- `mizan/backend/data/l-hsab/` — directory (L-HSAB file placed here manually)
- `mizan/backend/data/let-mi/` — directory (Let-Mi files placed here, or left empty if access pending)
- `mizan/backend/requirements.txt` — add pandas==2.2.3 and tqdm==4.66.5

---

### Steps

#### Step 1: Add pandas and tqdm to requirements.txt

Open `mizan/backend/requirements.txt` and add these two lines at the end:

```
pandas==2.2.3
tqdm==4.66.5
```

Then rebuild the backend container:

```bash
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  build backend && \
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  up -d backend
```

Verify install inside container:

```bash
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec backend python -c "import pandas; import tqdm; print('OK')"
```

#### Step 2: Create directory structure

```bash
mkdir -p "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/jhsc"
mkdir -p "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/osact5"
mkdir -p "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/l-hsab"
mkdir -p "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/let-mi"

# Add .gitkeep to empty dirs so they are committed
touch "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/let-mi/.gitkeep"
```

#### Step 3: Create `mizan/backend/data/README.md`

Exact file contents:

```markdown
# Mizan — Dataset Sources

This directory holds the raw dataset files used by `scripts/seed_content.py` and `scripts/seed_jhsc.py`.
Files must be downloaded manually before running the seed scripts (offline seeding requirement).

---

## JHSC — Jordanian Hate Speech Corpus

**Directory**: `data/jhsc/`
**Files**:
- `annotated-hatetweets-4-classes_train.csv` — 302,766 rows
- `annotated-hatetweets-4-classes_test.csv` — 100,923 rows

**Download**:
1. Open https://data.mendeley.com/datasets/mcnzzpgrdj/2
2. Click "Download All" — downloads `mcnzzpgrdj_2.zip`
3. Unzip — produces the two CSV files above
4. Move both files to `mizan/backend/data/jhsc/`
5. Verify: `wc -l data/jhsc/annotated-hatetweets-4-classes_train.csv` → should print 302767 (302,766 rows + 1 header)

**License**: CC BY 4.0
**Citation**: Ahmad et al. 2024, Frontiers in AI, DOI: 10.3389/frai.2024.1345445

**Column format** (header row IS present):
| Column | Type | Notes |
|--------|------|-------|
| `Tweet id` | integer | Unique tweet ID (with space in header name) |
| `Text` | string | Arabic tweet text |
| `Label` | string | One of: `Negative`, `Neutral`, `Positive`, `Very positive` |

**Label mapping to Mizan schema**:
| JHSC Label | Mizan `ground_truth_label` | Mizan `hate_type` |
|------------|---------------------------|-------------------|
| `Negative` | `not_hate` | null |
| `Neutral` | `not_hate` | null |
| `Positive` | `hate` | `unknown` |
| `Very positive` | `hate` | `unknown` |

**Observatory use**: All 403K rows loaded verbatim into `jhsc_tweets` table using original labels.
No mapping to 9-category schema for the Observatory (academically honest — JHSC is coarse-labeled).

---

## OSACT5 — Arabic Hate Speech Shared Task 2022

**Directory**: `data/osact5/`
**Files**:
- `OSACT2022-sharedTask-train.txt` — training split
- `OSACT2022-sharedTask-dev.txt` — development split

**Download**:
```bash
curl -o data/osact5/OSACT2022-sharedTask-train.txt \
  https://alt.qcri.org/resources/OSACT2022/OSACT2022-sharedTask-train.txt

curl -o data/osact5/OSACT2022-sharedTask-dev.txt \
  https://alt.qcri.org/resources1/OSACT2022/OSACT2022-sharedTask-dev.txt
```

**License**: Research use
**Citation**: OSACT5 Shared Task, LREC 2022, https://osact5-lrec.github.io

**Column format** (NO header row — tab-separated):
| Position | Column | Values |
|----------|--------|--------|
| 0 | `id` | numeric row ID |
| 1 | `text` | Arabic tweet text |
| 2 | `OFF_label` | `OFF` or `NOT_OFF` |
| 3 | `HS_label` | `NOT_HS`, `HS1`, `HS2`, `HS3`, `HS4`, `HS5`, `HS6` |
| 4 | `VLG_label` | `NOT_VLG` or `VLG` |
| 5 | `VIO_label` | `NOT_VIO` or `VIO` |

**Hate type mapping**:
| HS code | Meaning | Mizan `hate_type` |
|---------|---------|-------------------|
| `HS1` | Race/ethnicity/nationality | `race` |
| `HS2` | Religion/belief | `religion` |
| `HS3` | Ideology | `ideology` |
| `HS4` | Disability/disease | `disability` |
| `HS5` | Social class | `social_class` |
| `HS6` | Gender | `gender` |

**Label mapping to Mizan schema**:
| OFF_label | HS_label | Mizan `ground_truth_label` | Mizan `hate_type` |
|-----------|----------|---------------------------|-------------------|
| `NOT_OFF` | `NOT_HS` | `not_hate` | null |
| `OFF` | `NOT_HS` | `offensive` | null |
| `OFF` | `HS1`–`HS6` | `hate` | per HS code table |

---

## L-HSAB — Levantine Hate Speech and Abusive Language

**Directory**: `data/l-hsab/`
**File**: `L-HSAB` (no extension — it is a TSV file)

**Download**:
1. Open https://github.com/Hala-Mulki/L-HSAB-First-Arabic-Levantine-HateSpeech-Dataset
2. Navigate to `Dataset/L-HSAB`
3. Click "Download raw file" and save as `data/l-hsab/L-HSAB`

Or via curl (using raw GitHub URL):
```bash
curl -L -o data/l-hsab/L-HSAB \
  "https://raw.githubusercontent.com/Hala-Mulki/L-HSAB-First-Arabic-Levantine-HateSpeech-Dataset/master/Dataset/L-HSAB"
```

**License**: Research use (see GitHub repo)
**Citation**: Mulki et al. 2019, L-HSAB

**Column format** (NO header row — tab-separated):
| Position | Column | Values |
|----------|--------|--------|
| 0 | `text` | Arabic tweet text |
| 1 | `class_label` | `normal`, `abusive`, `hate` |

**Label mapping to Mizan schema**:
| L-HSAB `class_label` | Mizan `ground_truth_label` | Mizan `hate_type` |
|-----------------------|---------------------------|-------------------|
| `normal` | `not_hate` | null |
| `abusive` | `offensive` | null |
| `hate` | `hate` | `unknown` |

---

## Let-Mi — Arabic Levantine Misogyny Dataset

**Directory**: `data/let-mi/`
**Status**: ACCESS-GATED

**To obtain access**:
1. Submit the request form at: https://forms.gle/pKywZKRHBoLkEPqBA
2. Await approval email from dataset authors
3. Download the dataset files and place them in `data/let-mi/`

**If Let-Mi access is delayed** (fallback):
The seed script (`scripts/seed_content.py`) will detect an empty `data/let-mi/` directory and
automatically use additional OSACT5 HS6 (gender hate) rows to reach the 500+ example target.
This substitution is documented in the seed output log.

**Expected label format** (LOW confidence — inferred from WANLP 2021 paper, unconfirmed):
- Binary: `Misogyny` or `None`
- Fine-grained: `Damn`, `Der`, `Disc`, `Dom`, `Harass`, `Obj`, `Vio`, `None`

**Label mapping to Mizan schema**:
| Let-Mi `misogyny` | Mizan `ground_truth_label` | Mizan `hate_type` |
|-------------------|---------------------------|-------------------|
| `None` | `not_hate` | null |
| `Misogyny` | `hate` | `gender` |

---

## Notes on Repo Size

JHSC train + test CSV files are ~100–300MB combined. If Git repo size becomes a problem:
- Add `data/jhsc/` to `.gitignore` and document JHSC as "download before seeding"
- Or configure Git LFS: `git lfs track "data/jhsc/*.csv"`

For the hackathon demo, committing directly is simpler.
```

#### Step 4: Download JHSC (HUMAN STEP — cannot be automated)

**Developer must do this manually:**

1. Open https://data.mendeley.com/datasets/mcnzzpgrdj/2 in a browser
2. Click "Download All" — downloads `mcnzzpgrdj_2.zip` (expect ~100-300MB)
3. Unzip the file
4. Move both CSVs into the project:
   ```bash
   mv annotated-hatetweets-4-classes_train.csv \
     "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/jhsc/"
   mv annotated-hatetweets-4-classes_test.csv \
     "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/jhsc/"
   ```
5. Verify the train file header — run this and record the exact output:
   ```bash
   head -1 "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/jhsc/annotated-hatetweets-4-classes_train.csv"
   ```
   Expected: `Tweet id,Text,Label` (or with different spacing — record what you see)
6. Verify row count:
   ```bash
   wc -l "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/jhsc/annotated-hatetweets-4-classes_train.csv"
   ```
   Expected: `302767` (302,766 rows + 1 header)
7. Check if a date column exists:
   ```bash
   head -2 "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/jhsc/annotated-hatetweets-4-classes_train.csv"
   ```
   If columns beyond `Tweet id,Text,Label` appear, update `scripts/seed_jhsc.py` (Plan 2.4) to extract `tweet_year` and `tweet_month` from that column.

#### Step 5: Download OSACT5 (can be automated with curl)

```bash
curl -o "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/osact5/OSACT2022-sharedTask-train.txt" \
  "https://alt.qcri.org/resources/OSACT2022/OSACT2022-sharedTask-train.txt"

curl -o "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/osact5/OSACT2022-sharedTask-dev.txt" \
  "https://alt.qcri.org/resources1/OSACT2022/OSACT2022-sharedTask-dev.txt"
```

Verify the first line is data (no header):
```bash
head -1 "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/osact5/OSACT2022-sharedTask-train.txt"
```
Expected: a line starting with a number, followed by tab, then Arabic text.

#### Step 6: Download L-HSAB (can be automated with curl)

```bash
curl -L -o "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/l-hsab/L-HSAB" \
  "https://raw.githubusercontent.com/Hala-Mulki/L-HSAB-First-Arabic-Levantine-HateSpeech-Dataset/master/Dataset/L-HSAB"
```

Verify:
```bash
head -2 "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/l-hsab/L-HSAB"
```
Expected: Arabic text followed by tab then `normal`, `abusive`, or `hate`.

#### Step 7: Let-Mi (HUMAN STEP — access-gated)

Submit the form at https://forms.gle/pKywZKRHBoLkEPqBA and await approval.

If Let-Mi files arrive: place them in `mizan/backend/data/let-mi/`. The seed script will detect them automatically.

If Let-Mi is not available before Phase 2 execution: leave `data/let-mi/` with only `.gitkeep`. The seed script will fall back to OSACT5 HS6 rows (see Plan 2.3 for fallback logic).

#### Step 8: Add data files to git

```bash
cd "/Users/ahmadalzaro/Desktop/AI Hatespeech Project"
git add mizan/backend/data/README.md
git add mizan/backend/data/osact5/
git add mizan/backend/data/l-hsab/
git add mizan/backend/data/let-mi/.gitkeep
# JHSC only if repo size is acceptable:
git add mizan/backend/data/jhsc/
git status  # verify what is being staged before committing
git commit -m "data: add dataset files and source documentation"
```

---

### Verification

```bash
# All four dataset directories exist
ls "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/"
# Expected: README.md  jhsc/  l-hsab/  let-mi/  osact5/

# pandas and tqdm importable in container
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec backend python -c "import pandas; import tqdm; print(pandas.__version__, tqdm.__version__)"
# Expected: 2.2.3  4.66.5

# JHSC train file present and has correct row count
wc -l "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/jhsc/annotated-hatetweets-4-classes_train.csv"
# Expected: 302767

# OSACT5 train file: first field is a number
head -1 "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/osact5/OSACT2022-sharedTask-train.txt" | cut -f1
# Expected: 1

# L-HSAB: two tab-separated columns
awk -F'\t' '{print NF; exit}' "/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/backend/data/l-hsab/L-HSAB"
# Expected: 2
```

---

### Done

- `mizan/backend/data/README.md` exists documenting all four datasets with exact column formats and label mappings
- `mizan/backend/data/jhsc/` contains both JHSC CSV files
- `mizan/backend/data/osact5/` contains both OSACT5 .txt files
- `mizan/backend/data/l-hsab/L-HSAB` file exists
- `mizan/backend/data/let-mi/` directory exists (either with files or with `.gitkeep`)
- `requirements.txt` includes `pandas==2.2.3` and `tqdm==4.66.5`
- All files committed to git

---

## Plan 2.3 — Content Examples Seed Script (500+ examples)

**Requirement**: DATA-01, DATA-02, DATA-03, DATA-04
**Goal**: Running `scripts/seed_content.py` inserts 500+ rows into `content_examples` with correct label and hate_type mappings from all four datasets. Script is idempotent.

---

### Files to Create

- `mizan/backend/scripts/seed_content.py` — the seed script

---

### Steps

#### Step 1: Create `mizan/backend/scripts/seed_content.py`

Exact file contents:

```python
"""
Seed script: inserts 500+ content examples from JHSC, OSACT5, L-HSAB, and Let-Mi.
Run after applying the Phase 2 migration and placing dataset files in data/.

Usage (inside container):
  docker compose exec backend python scripts/seed_content.py

Idempotent: safe to run twice — exits early if content_examples already has rows.
"""
import sys
import uuid
import os
sys.path.insert(0, "/app")

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import insert

from app.database import engine
from app.models.content_example import ContentExample, ContentLabel, HateType


# ── Configuration ────────────────────────────────────────────────────────────
DATA_DIR = "/app/data"
N_PER_DATASET = 125   # target ~125 per dataset → ~500 total

# ── JHSC label → Mizan label mapping ─────────────────────────────────────────
JHSC_LABEL_MAP = {
    "negative":      (ContentLabel.not_hate, None),
    "neutral":       (ContentLabel.not_hate, None),
    "positive":      (ContentLabel.hate,     HateType.unknown),
    "very positive": (ContentLabel.hate,     HateType.unknown),  # note the space
}

# ── OSACT5 HS code → Mizan hate_type ─────────────────────────────────────────
OSACT5_HS_MAP = {
    "HS1": HateType.race,
    "HS2": HateType.religion,
    "HS3": HateType.ideology,
    "HS4": HateType.disability,
    "HS5": HateType.social_class,
    "HS6": HateType.gender,
}

# ── L-HSAB class → Mizan label ───────────────────────────────────────────────
LHSAB_LABEL_MAP = {
    "normal":   (ContentLabel.not_hate, None),
    "abusive":  (ContentLabel.offensive, None),
    "hate":     (ContentLabel.hate, HateType.unknown),
}


def make_row(text: str, source: str, dialect: str, label: ContentLabel, hate_type) -> dict:
    """Build a dict ready for bulk insert into content_examples."""
    return {
        "id": uuid.uuid4(),
        "text": str(text),
        "source_dataset": source,
        "dialect": dialect,
        "ground_truth_label": label.value,
        "hate_type": hate_type.value if hate_type else None,
    }


def load_jhsc_sample(n: int) -> list[dict]:
    """Load n examples from JHSC train CSV. Samples from hate and not_hate rows."""
    path = os.path.join(DATA_DIR, "jhsc", "annotated-hatetweets-4-classes_train.csv")
    if not os.path.exists(path):
        print(f"  WARN: JHSC file not found at {path} — skipping")
        return []

    # JHSC CSV has a header row. Confirmed columns: tweet_id, new_tweet_content, Label
    df = pd.read_csv(path, encoding="utf-8", usecols=["tweet_id", "new_tweet_content", "Label"])
    df = df.dropna(subset=["new_tweet_content", "Label"])

    # Only sample rows with meaningful labels (exclude neutral which is generic tweets)
    meaningful = df[df["Label"].isin(["negative", "positive", "very positive"])]
    sample = meaningful.sample(n=min(n, len(meaningful)), random_state=42)

    rows = []
    for _, row in sample.iterrows():
        label_str = str(row["Label"]).strip()
        mizan_label, hate_type = JHSC_LABEL_MAP.get(label_str, (ContentLabel.not_hate, None))
        rows.append(make_row(row["new_tweet_content"], "jhsc", "jordanian", mizan_label, hate_type))
    print(f"  Loaded {len(rows)} rows from JHSC")
    return rows


def load_osact5(n: int) -> list[dict]:
    """Load n examples from OSACT5 train split."""
    path = os.path.join(DATA_DIR, "osact5", "OSACT2022-sharedTask-train.txt")
    if not os.path.exists(path):
        print(f"  WARN: OSACT5 file not found at {path} — skipping")
        return []

    # NO header row — must pass header=None and explicit names
    df = pd.read_csv(
        path,
        sep="\t",
        header=None,
        names=["id", "text", "OFF_label", "HS_label", "VLG_label", "VIO_label"],
        encoding="utf-8",
    )
    df = df.dropna(subset=["text", "OFF_label", "HS_label"])
    sample = df.sample(n=min(n, len(df)), random_state=42)

    rows = []
    for _, row in sample.iterrows():
        off = str(row["OFF_label"]).strip()
        hs = str(row["HS_label"]).strip()

        if off == "NOT_OFF" and hs == "NOT_HS":
            mizan_label = ContentLabel.not_hate
            hate_type = None
        elif off == "OFF" and hs == "NOT_HS":
            mizan_label = ContentLabel.offensive
            hate_type = None
        elif off == "OFF" and hs in OSACT5_HS_MAP:
            mizan_label = ContentLabel.hate
            hate_type = OSACT5_HS_MAP[hs]
        else:
            # Unknown combination — skip
            continue

        rows.append(make_row(row["text"], "osact5", "levantine", mizan_label, hate_type))
    print(f"  Loaded {len(rows)} rows from OSACT5")
    return rows


def load_lhsab(n: int) -> list[dict]:
    """Load n examples from L-HSAB."""
    path = os.path.join(DATA_DIR, "l-hsab", "L-HSAB")
    if not os.path.exists(path):
        print(f"  WARN: L-HSAB file not found at {path} — skipping")
        return []

    # NO header row — tab-separated, 2 columns
    df = pd.read_csv(
        path,
        sep="\t",
        header=None,
        names=["text", "class_label"],
        encoding="utf-8",
    )
    df = df.dropna(subset=["text", "class_label"])
    sample = df.sample(n=min(n, len(df)), random_state=42)

    rows = []
    for _, row in sample.iterrows():
        class_str = str(row["class_label"]).strip().lower()
        if class_str not in LHSAB_LABEL_MAP:
            continue
        mizan_label, hate_type = LHSAB_LABEL_MAP[class_str]
        rows.append(make_row(row["text"], "l-hsab", "levantine", mizan_label, hate_type))
    print(f"  Loaded {len(rows)} rows from L-HSAB")
    return rows


def load_letmi(n: int) -> list[dict]:
    """
    Load n examples from Let-Mi.
    Expected column names (LOW confidence — verify when files arrive):
      - column 0 or 'id': tweet ID (drop)
      - column 1 or 'text': Arabic tweet text
      - 'misogyny': 'misogyny' or 'none' (confirmed lowercase)

    Returns empty list if data/let-mi/ has no data files (access pending).
    """
    letmi_dir = os.path.join(DATA_DIR, "let-mi")
    # Find any file that is not .gitkeep
    data_files = [
        f for f in os.listdir(letmi_dir)
        if not f.startswith(".") and os.path.isfile(os.path.join(letmi_dir, f))
    ]

    if not data_files:
        print("  WARN: Let-Mi data/let-mi/ is empty — applying fallback (OSACT5 HS6 rows)")
        return _letmi_fallback(n)

    # Attempt to load first data file found
    path = os.path.join(letmi_dir, data_files[0])
    try:
        # Try tab-separated, no header first
        df = pd.read_csv(path, sep="\t", header=None, encoding="utf-8")
        # Assign column names based on position
        if df.shape[1] >= 3:
            df.columns = ["id", "text", "misogyny"] + [f"col{i}" for i in range(3, df.shape[1])]
        elif df.shape[1] == 2:
            df.columns = ["text", "misogyny"]
        else:
            print(f"  ERROR: Let-Mi file {path} has unexpected column count {df.shape[1]}")
            return _letmi_fallback(n)
    except Exception as e:
        print(f"  ERROR reading Let-Mi file: {e}")
        return _letmi_fallback(n)

    df = df.dropna(subset=["text", "misogyny"])
    sample = df.sample(n=min(n, len(df)), random_state=42)

    rows = []
    for _, row in sample.iterrows():
        misogyny = str(row["misogyny"]).strip()
        if misogyny == "misogyny":
            mizan_label = ContentLabel.hate
            hate_type = HateType.gender
        elif misogyny == "none":
            mizan_label = ContentLabel.not_hate
            hate_type = None
        else:
            continue  # unknown label value — skip
        rows.append(make_row(row["text"], "let-mi", "levantine", mizan_label, hate_type))

    print(f"  Loaded {len(rows)} rows from Let-Mi")
    return rows


def _letmi_fallback(n: int) -> list[dict]:
    """
    Fallback when Let-Mi is unavailable: use OSACT5 HS6 (gender hate) rows.
    These are labeled hate / gender — equivalent to what Let-Mi would provide.
    """
    path = os.path.join(DATA_DIR, "osact5", "OSACT2022-sharedTask-train.txt")
    if not os.path.exists(path):
        print("  WARN: OSACT5 fallback file also not found — Let-Mi slot will be empty")
        return []

    df = pd.read_csv(
        path,
        sep="\t",
        header=None,
        names=["id", "text", "OFF_label", "HS_label", "VLG_label", "VIO_label"],
        encoding="utf-8",
    )
    # HS6 rows only (gender hate) — the Let-Mi equivalent
    gender_rows = df[(df["HS_label"] == "HS6") & (df["OFF_label"] == "OFF")]
    sample = gender_rows.sample(n=min(n, len(gender_rows)), random_state=99)

    rows = []
    for _, row in sample.iterrows():
        rows.append(make_row(row["text"], "let-mi-fallback", "levantine", ContentLabel.hate, HateType.gender))

    print(f"  Let-Mi fallback: loaded {len(rows)} OSACT5 HS6 (gender hate) rows")
    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

with Session(engine) as session:
    existing = session.query(ContentExample).first()
    if existing:
        count = session.query(ContentExample).count()
        print(f"Content examples already seeded ({count} rows). Skipping.")
        sys.exit(0)

    print("Seeding content examples...")
    all_rows = []
    all_rows += load_jhsc_sample(N_PER_DATASET)
    all_rows += load_osact5(N_PER_DATASET)
    all_rows += load_lhsab(N_PER_DATASET)
    all_rows += load_letmi(N_PER_DATASET)

    if not all_rows:
        print("ERROR: No rows loaded from any dataset. Check data/ directory.")
        sys.exit(1)

    # Add created_at field (not in make_row to keep it clean)
    from datetime import datetime
    for row in all_rows:
        row["created_at"] = datetime.utcnow()

    session.execute(
        insert(ContentExample).execution_options(render_nulls=True),
        all_rows,
    )
    session.commit()

    print(f"\nDone. Seeded {len(all_rows)} content examples.")
    print("Breakdown:")
    by_source = {}
    for row in all_rows:
        src = row["source_dataset"]
        by_source[src] = by_source.get(src, 0) + 1
    for src, count in sorted(by_source.items()):
        print(f"  {src}: {count}")
```

---

### Steps (continued)

#### Step 2: Run the seed script

```bash
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec backend python scripts/seed_content.py
```

Expected output ends with:
```
Done. Seeded 500 content examples.
Breakdown:
  jhsc: 125
  l-hsab: 125
  let-mi: 125        (or let-mi-fallback: 125 if Let-Mi unavailable)
  osact5: 125
```

---

### Verification

```bash
# Total row count
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "SELECT COUNT(*) FROM content_examples;"
# Expected: 500+ rows

# Verify all four source_dataset values present
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "SELECT source_dataset, COUNT(*) FROM content_examples GROUP BY source_dataset ORDER BY source_dataset;"
# Expected: jhsc, l-hsab, let-mi (or let-mi-fallback), osact5 — each ~125 rows

# Verify hate_type is non-null for hate rows and null for non-hate rows
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "SELECT ground_truth_label, hate_type, COUNT(*) FROM content_examples GROUP BY ground_truth_label, hate_type ORDER BY ground_truth_label;"
# Expected: hate rows have hate_type IN (unknown, race, religion, ideology, gender, disability, social_class)
#           offensive rows have hate_type = null
#           not_hate rows have hate_type = null

# Verify Arabic text is present (spot check)
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "SELECT text FROM content_examples LIMIT 3;"
# Expected: Arabic text visible (not escaped unicode)

# Verify idempotency — running twice must not error or add rows
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec backend python scripts/seed_content.py
# Expected: "Content examples already seeded (500 rows). Skipping."
```

---

### Done

- `content_examples` table has 500+ rows
- All four datasets represented with ~125 rows each (or Let-Mi substituted with OSACT5 HS6)
- Every hate row has a non-null `hate_type`; every non-hate/offensive row has `hate_type = null`
- JHSC `hate_type` is always `unknown` (not guessed)
- OSACT5 rows have specific `hate_type` values (race, religion, ideology, disability, social_class, gender)
- Script is idempotent — running twice exits early without adding duplicate rows

---

## Plan 2.4 — JHSC Full Load (403K rows for Observatory)

**Requirement**: OBS-01
**Goal**: All 403K JHSC rows loaded into `jhsc_tweets` table in ~1-2 minutes using chunked bulk insert. Script is idempotent.

---

### Files to Create

- `mizan/backend/scripts/seed_jhsc.py` — the bulk load script

---

### Steps

#### Step 1: Create `mizan/backend/scripts/seed_jhsc.py`

Exact file contents:

```python
"""
Bulk load script: inserts all 403K JHSC rows into jhsc_tweets table.
Uses chunked SQLAlchemy Core inserts with tqdm progress bar.

Usage (inside container):
  docker compose exec backend python scripts/seed_jhsc.py

Idempotent: safe to run twice — exits early if jhsc_tweets already has rows.

JHSC CSV format (header row present):
  "Tweet id"  "Text"  "Label"
  Labels: Negative, Neutral, Positive, Very positive

Note: If the CSV has a date column (not confirmed), update EXTRACT_DATE = True
and the column name in the reader loop.
"""
import sys
sys.path.insert(0, "/app")

import os
import math
import pandas as pd
from sqlalchemy import insert, text
from tqdm import tqdm

from app.database import engine
from app.models.jhsc_tweet import JhscTweet, JhscLabel

# ── Configuration ─────────────────────────────────────────────────────────────
DATA_DIR = "/app/data/jhsc"
TRAIN_FILE = "annotated-hatetweets-4-classes_train.csv"
TEST_FILE  = "annotated-hatetweets-4-classes_test.csv"
CHUNK_SIZE = 10_000   # rows per INSERT batch — safe for psycopg2 execute_values

# Set to True ONLY if the CSV has a date/year column (check with `head -1` on the file)
EXTRACT_DATE = False
DATE_COLUMN = None  # e.g., "tweet_date" — update if date column found after download

# ── Valid JHSC label strings (must match PostgreSQL jhsclabel enum exactly) ───
VALID_LABELS = {"negative", "neutral", "positive", "very positive"}


def count_existing() -> int:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM jhsc_tweets"))
        return result.scalar()


def load_file(csv_path: str, desc: str) -> int:
    """
    Stream-reads a JHSC CSV in CHUNK_SIZE chunks, inserts each chunk into jhsc_tweets.
    Returns number of rows inserted.
    """
    if not os.path.exists(csv_path):
        print(f"  WARN: {csv_path} not found — skipping")
        return 0

    # Count total rows for tqdm (subtract 1 for header)
    total_rows = sum(1 for _ in open(csv_path, encoding="utf-8")) - 1
    total_chunks = math.ceil(total_rows / CHUNK_SIZE)

    reader = pd.read_csv(
        csv_path,
        chunksize=CHUNK_SIZE,
        encoding="utf-8",
        # Let pandas use the header row (default header=0)
        # Columns will be named: "Tweet id", "Text", "Label"
        # (plus any additional columns if they exist)
    )

    inserted = 0
    with engine.begin() as conn:
        for chunk in tqdm(reader, total=total_chunks, desc=desc):
            rows = []
            for _, row in chunk.iterrows():
                tweet_id_raw = row.get("tweet_id")
                text_raw = row.get("new_tweet_content")
                label_raw = row.get("Label") or row.get("label")

                if pd.isna(tweet_id_raw) or pd.isna(label_raw):
                    continue  # skip malformed rows

                label_str = str(label_raw).strip()
                if label_str not in VALID_LABELS:
                    continue  # skip unknown labels

                tweet_year = None
                tweet_month = None
                if EXTRACT_DATE and DATE_COLUMN and not pd.isna(row.get(DATE_COLUMN)):
                    try:
                        date_val = pd.to_datetime(row[DATE_COLUMN])
                        tweet_year = date_val.year
                        tweet_month = date_val.month
                    except Exception:
                        pass  # leave null if parsing fails

                rows.append({
                    "id": int(tweet_id_raw),
                    "text": str(text_raw) if pd.notna(text_raw) else None,
                    "label": label_str,
                    "tweet_year": tweet_year,
                    "tweet_month": tweet_month,
                })

            if rows:
                conn.execute(
                    insert(JhscTweet).prefix_with("OR IGNORE").execution_options(render_nulls=True),
                    rows,
                )
                inserted += len(rows)

    return inserted


# ── Main ──────────────────────────────────────────────────────────────────────

existing = count_existing()
if existing > 0:
    print(f"jhsc_tweets already has {existing:,} rows. Skipping.")
    sys.exit(0)

print("Loading JHSC tweets into jhsc_tweets table...")
print(f"Chunk size: {CHUNK_SIZE:,} rows per batch")

total = 0
total += load_file(os.path.join(DATA_DIR, TRAIN_FILE), "Train CSV")
total += load_file(os.path.join(DATA_DIR, TEST_FILE),  "Test CSV ")

print(f"\nDone. Loaded {total:,} rows into jhsc_tweets.")

# Quick sanity check
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT label, COUNT(*) as n FROM jhsc_tweets GROUP BY label ORDER BY label")
    )
    print("\nBreakdown by label:")
    for label, count in result:
        print(f"  {label}: {count:,}")
```

**Critical note on `OR IGNORE`:** PostgreSQL does not support `INSERT OR IGNORE`. Replace `.prefix_with("OR IGNORE")` with the PostgreSQL equivalent. Update the insert line to:

```python
from sqlalchemy.dialects.postgresql import insert as pg_insert

conn.execute(
    pg_insert(JhscTweet)
    .on_conflict_do_nothing(index_elements=["id"])
    .execution_options(render_nulls=True),
    rows,
)
```

Update the import at the top of the file accordingly:
```python
from sqlalchemy.dialects.postgresql import insert as pg_insert
```

And remove `from sqlalchemy import insert` (or keep it if used elsewhere).

#### Step 2: Run the bulk load

```bash
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec backend python scripts/seed_jhsc.py
```

Expected: tqdm progress bars for both files, total ~403K rows, completes in ~1-2 minutes.

---

### Verification

```bash
# Total row count
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "SELECT COUNT(*) FROM jhsc_tweets;"
# Expected: 403,688 (or close — some rows may be skipped if malformed)

# Breakdown by label
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "SELECT label, COUNT(*) FROM jhsc_tweets GROUP BY label ORDER BY label;"
# Expected four rows: Negative, Neutral, Positive, Very positive

# Verify "Very positive" (with space) is a valid enum value — not rejected
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "SELECT COUNT(*) FROM jhsc_tweets WHERE label = 'Very positive';"
# Expected: > 0 (should be ~7,000)

# Observatory query (aggregate by year+month) — test that indexes are used
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c \
  "EXPLAIN SELECT tweet_year, tweet_month, label, COUNT(*) FROM jhsc_tweets GROUP BY tweet_year, tweet_month, label LIMIT 5;"
# Expected: plan references ix_jhsc_tweets_year_month or ix_jhsc_tweets_label

# Idempotency check
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec backend python scripts/seed_jhsc.py
# Expected: "jhsc_tweets already has 403,688 rows. Skipping."
```

---

### Done

- `jhsc_tweets` table has ~403,688 rows
- All four JHSC label values (`Negative`, `Neutral`, `Positive`, `Very positive`) present
- `tweet_year` and `tweet_month` are populated if the CSV contains a date column; null otherwise
- Script completes in under 3 minutes
- Script is idempotent — running twice exits early without errors or duplicate rows
- Observatory aggregate query executes and returns results (even if slow — Phase 8 will optimize)

---

## Plan 2.5 — Export API Endpoint

**Requirement**: DATA-04
**Goal**: `GET /api/export?format=csv` and `GET /api/export?format=json` return downloadable files with all content_examples rows. Admin role required. Arabic text is preserved unescaped in JSON output.

---

### Files to Create/Modify

- `mizan/backend/app/models/content_example.py` — already created in Plan 2.1; no changes needed
- `mizan/backend/app/routers/export.py` — new router
- `mizan/backend/app/main.py` — add export router import and registration

---

### Steps

#### Step 1: Create `mizan/backend/app/routers/export.py`

Exact file contents:

```python
"""
Export router: GET /api/export

Streams all content_examples rows as CSV or JSON.
Admin-only. Uses StreamingResponse for memory-safe large downloads.

Usage:
  GET /api/export?format=csv   → mizan-export.csv download
  GET /api/export?format=json  → mizan-export.json download

Export schema is future-proofed: Phase 3-6 columns exported as null until populated.
"""
import csv
import io
import json
from typing import Generator

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.content_example import ContentExample

router = APIRouter(prefix="/api/export", tags=["export"])

# Full export schema — covers all phases. Phase 2 populates the first 6 columns.
EXPORT_FIELDNAMES = [
    "example_id",
    "text",
    "source_dataset",
    "dialect",
    "ground_truth_label",
    "hate_type",
    # Phase 3+ columns (null until moderator labeling is built)
    "moderator_id",
    "moderator_label",
    "moderator_agree_ai",
    # Phase 4+ columns (null until MARBERT inference is built)
    "ai_label",
    "ai_confidence",
    # Phase 6+ columns (null until calibration scoring is built)
    "calibration_score",
]


def example_to_dict(example: ContentExample) -> dict:
    """Convert a ContentExample ORM object to the export row dict."""
    return {
        "example_id": str(example.id),
        "text": example.text,
        "source_dataset": example.source_dataset,
        "dialect": example.dialect,
        "ground_truth_label": example.ground_truth_label.value if example.ground_truth_label else None,
        "hate_type": example.hate_type.value if example.hate_type else None,
        # Phase 3+ — null in Phase 2
        "moderator_id": None,
        "moderator_label": None,
        "moderator_agree_ai": None,
        # Phase 4+ — null in Phase 2
        "ai_label": None,
        "ai_confidence": None,
        # Phase 6+ — null in Phase 2
        "calibration_score": None,
    }


def generate_csv(rows: list[dict]) -> Generator[str, None, None]:
    """
    Generator that yields CSV lines one at a time.
    Memory-safe: does not build the entire file in memory.
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=EXPORT_FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    yield buffer.getvalue()
    buffer.truncate(0)
    buffer.seek(0)

    for row in rows:
        writer.writerow(row)
        yield buffer.getvalue()
        buffer.truncate(0)
        buffer.seek(0)


def generate_json(rows: list[dict]) -> Generator[bytes, None, None]:
    """
    Generator that yields the entire JSON array as a single chunk.
    ensure_ascii=False is critical — preserves Arabic characters as-is.
    """
    yield json.dumps(rows, ensure_ascii=False, default=str).encode("utf-8")


@router.get("")
def export_dataset(
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Export all content_examples as CSV or JSON.
    Requires admin or super_admin role.

    Query params:
      format: "csv" (default) or "json"

    Returns a file download response.
    """
    examples = db.query(ContentExample).order_by(ContentExample.created_at).all()
    rows = [example_to_dict(e) for e in examples]

    if format == "csv":
        return StreamingResponse(
            generate_csv(rows),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="mizan-export.csv"',
            },
        )
    else:
        return StreamingResponse(
            generate_json(rows),
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="mizan-export.json"',
            },
        )
```

#### Step 2: Register the export router in `mizan/backend/app/main.py`

Open `mizan/backend/app/main.py`. The current contents are:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(title="Mizan API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "mizan-backend"}
```

Add the export router import and registration. Updated file:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.routers import export

app = FastAPI(title="Mizan API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(export.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "mizan-backend"}
```

---

### Verification

First, get an admin token. Use the demo admin created in Phase 1:

```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo-admin@mizan.local", "password": "demo_admin_2026"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

Test CSV export:

```bash
curl -s -X GET "http://localhost:8000/api/export?format=csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o /tmp/mizan-export.csv

# Verify it is a real CSV (not an error response)
head -2 /tmp/mizan-export.csv
# Expected line 1: example_id,text,source_dataset,dialect,ground_truth_label,hate_type,...
# Expected line 2: a UUID, then Arabic text, then jhsc/osact5/l-hsab/let-mi

wc -l /tmp/mizan-export.csv
# Expected: 501+ lines (1 header + 500+ data rows)
```

Test JSON export:

```bash
curl -s -X GET "http://localhost:8000/api/export?format=json" \
  -H "Authorization: Bearer $TOKEN" \
  -o /tmp/mizan-export.json

# Verify Arabic text is NOT escaped (should see Arabic characters, not \u0645...)
python3 -c "
import json
with open('/tmp/mizan-export.json') as f:
    data = json.load(f)
print('Rows:', len(data))
print('First text:', data[0]['text'][:50])
print('Arabic preserved:', any('\u0600' <= c <= '\u06FF' for c in data[0]['text']))
"
# Expected: Rows: 500+, Arabic text visible, Arabic preserved: True
```

Test that non-admin is rejected:

```bash
# Get a moderator token
MOD_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "moderator@mizan.local", "password": "some_password"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', 'no_token'))")

curl -s -X GET "http://localhost:8000/api/export?format=csv" \
  -H "Authorization: Bearer $MOD_TOKEN" | python3 -c "import sys, json; print(json.load(sys.stdin))"
# Expected: {"detail": "Admin access required"}
```

Test invalid format param:

```bash
curl -s -X GET "http://localhost:8000/api/export?format=xml" \
  -H "Authorization: Bearer $TOKEN"
# Expected: 422 Unprocessable Entity
```

Test FastAPI docs show the endpoint:

```bash
curl -s http://localhost:8000/openapi.json | python3 -c \
  "import sys, json; paths = json.load(sys.stdin)['paths']; print([k for k in paths if 'export' in k])"
# Expected: ['/api/export']
```

---

### Done

- `GET /api/export?format=csv` returns a CSV file download named `mizan-export.csv`
- `GET /api/export?format=json` returns a JSON file download named `mizan-export.json`
- Both exports contain all `content_examples` rows (500+ rows)
- JSON export preserves Arabic text without `\uXXXX` escaping
- Non-admin requests return HTTP 403
- `?format=xml` returns HTTP 422 (validation error)
- Export schema includes all 12 columns from Phase 2 context; Phase 3-6 columns are null
- Endpoint appears in `/openapi.json`

---

## Phase 2 Summary — Overall Verification

After all five plans are complete, run this end-to-end check:

```bash
# 1. Both tables exist with data
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c "
SELECT 'content_examples' as table_name, COUNT(*) FROM content_examples
UNION ALL
SELECT 'jhsc_tweets', COUNT(*) FROM jhsc_tweets;
"
# Expected:
#  content_examples | 500+
#  jhsc_tweets      | 403,000+

# 2. All four source datasets represented
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c "
SELECT source_dataset, ground_truth_label, COUNT(*)
FROM content_examples
GROUP BY source_dataset, ground_truth_label
ORDER BY source_dataset, ground_truth_label;
"

# 3. Export endpoint works
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo-admin@mizan.local", "password": "demo_admin_2026"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
curl -s "http://localhost:8000/api/export?format=csv" \
  -H "Authorization: Bearer $TOKEN" | head -2

# 4. Observatory query works (may be slow — that is acceptable in Phase 2)
docker compose -f /Users/ahmadalzaro/Desktop/AI\ Hatespeech\ Project/mizan/docker-compose.yml \
  exec db psql -U mizan -d mizan -c "
SELECT tweet_year, label, COUNT(*)
FROM jhsc_tweets
WHERE tweet_year IS NOT NULL
GROUP BY tweet_year, label
ORDER BY tweet_year, label
LIMIT 10;
"
```

---

*Phase 2 plan written: 2026-03-02*
*Requirements covered: DATA-01, DATA-02, DATA-03, DATA-04, OBS-01*
