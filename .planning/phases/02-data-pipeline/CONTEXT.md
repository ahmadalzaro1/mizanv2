# Phase 2 — Data Pipeline: Context

> Decisions locked by user discussion on 2026-03-02.
> Researcher and planner must follow these exactly — do not re-ask.

---

## A. Data Sourcing

**Seed script must work completely offline.**
No internet connection required when running the seed. All data files are committed inside the project repo as CSV or JSON. Do not rely on HuggingFace, GitHub, or any external download at seed time.

**All 7 datasets must be clearly represented.**
Each of the following contributes examples to the seed — they must be traceable to their source:
- JHSC (Jordanian dialect) — already downloaded
- OSACT5 (fine-grained pan-Arabic) — to download
- L-HSAB (Levantine, 3-class) — to download
- Let-Mi (Levantine gender hate) — partially downloaded (train part only, 5,240 rows)
- Arabic Religious Hate Speech (religious hate, binary) — to download from GitHub
- MLMA Arabic (multi-aspect: gender/religion/disability) — to download from GitHub
- Al Jazeera Abusive Language (32K comments, ternary) — to download from QCRI

**Target: 500+ seeded examples total.**
Roughly 70+ per dataset across 7 datasets. The planner should pre-process and commit cleaned CSV/JSON files for each dataset. The seed script reads from these local files.

**New dataset sources (added 2026-03-02):**
- Arabic Religious Hate Speech: https://github.com/nuhaalbadi/Arabic_hatespeech (6,136 tweets, binary hate/not, religious subcategories)
- MLMA Arabic: https://github.com/HKUST-KnowComp/MLMA_hate_speech (3,353 tweets, gender/sexual orientation/religion/disability)
- Al Jazeera: http://alt.qcri.org/~hmubarak/offensive/AJCommentsClassification-CF.xlsx (32,000 comments, ternary: obscene/offensive/clean)
- Let-Mi full: https://drive.google.com/file/d/1mM2vnjsy7QfUmdVUpKqHRJjZyQobhTrW/view (full 6,603 rows — user only has train part)

**JHSC is not yet downloaded.**
The phase plan must include a step for downloading JHSC from Mendeley Data
(`https://data.mendeley.com/datasets/mcnzzpgrdj/2`) and processing it into a committed file before seeding can run.

---

## B. Label Schema

**Label taxonomy (4 possible values at top level):**
- `hate` — content that targets a group (has a hate_type)
- `offensive` — rude/aggressive content, NOT targeting a group (no hate_type)
- `not_hate` — neutral/normal content
- `spam` — spam (from JHSC; keep as-is)

**Hate type: stored as a fixed enum.**
The `hate_type` column uses a PostgreSQL enum with exactly these 9 allowed values:
```
race, religion, ideology, gender, disability, social_class,
tribalism, refugee_related, political_affiliation
```
Plus a special value: `unknown` — used when the source dataset doesn't specify hate type.

**hate_type = 'unknown' for JHSC and L-HSAB examples.**
These datasets only say "hate" without specifying type. Store `label=hate, hate_type=unknown`.
Do NOT guess or infer the type.

**Jordanian-specific categories are reserved — no seeded examples.**
Tribalism, refugee_related, political_affiliation exist in the enum but will have zero seeded examples.
They are available for future human annotation (post-Phase 2). The demo can still display them as options.

**'Offensive' is its own label, separate from hate.**
Do not map JHSC's "offensive" to `label=hate`. Store it as `label=offensive, hate_type=null`.

---

## C. JHSC Temporal Data (Observatory)

**Store all 403,688 JHSC rows in the database.**
Full row-level storage in a dedicated `jhsc_tweets` table (separate from the 500+ training examples table).
Each row includes: tweet text (optional), date, and the original JHSC 4-class label.

**Observatory chart shows volume by JHSC's own 4 labels.**
The chart displays monthly counts of hate / offensive / neutral / spam — using JHSC's original labels.
Do NOT attempt to map these to the 9-category schema for the Observatory.
This is academically honest: JHSC is coarse-labeled data.

**A few seconds of load time is acceptable.**
No pre-aggregation table required in Phase 2. The chart will query the `jhsc_tweets` table and aggregate
by month/year at query time. If the query is slow, a loading state is fine for the demo.
(Performance optimization is deferred to Phase 8: Demo Polish.)

**Download instructions must be included in the plan.**
The plan must include a step-by-step guide for downloading the JHSC dataset from Mendeley Data,
processing it into a format the seed can use, and where to place it in the project.

---

## D. Export API

**Build the export endpoint in Phase 2 — future-proofed.**
Do not defer. The export endpoint is built now with a schema that supports all future data types,
even though only seeded data exists in Phase 2. Later phases populate more columns.

**Both CSV and JSON formats supported.**
The endpoint accepts a `format` query param: `?format=csv` or `?format=json`.
Triggers a file download in the browser.

**API endpoint — not a CLI script.**
`GET /api/export` — accessible from the frontend. Admin role required.
A download button in the admin dashboard triggers this endpoint.

**Export schema covers all four data types (populated as phases complete):**

| Column | Available in Phase | Description |
|--------|-------------------|-------------|
| `example_id` | Phase 2 | Unique ID for the content item |
| `text` | Phase 2 | The Arabic tweet/comment |
| `source_dataset` | Phase 2 | Which dataset it came from (jhsc/osact5/l-hsab/let-mi) |
| `dialect` | Phase 2 | jordanian / levantine |
| `ground_truth_label` | Phase 2 | hate / offensive / not_hate / spam |
| `hate_type` | Phase 2 | The 9-category enum value, or 'unknown', or null |
| `moderator_id` | Phase 3+ | Who labeled it |
| `moderator_label` | Phase 3+ | What the moderator labeled it |
| `moderator_agree_ai` | Phase 3+ | Did the moderator agree with MARBERT? |
| `ai_label` | Phase 4+ | MARBERT's prediction |
| `ai_confidence` | Phase 4+ | MARBERT's confidence score (0–1) |
| `calibration_score` | Phase 6+ | Moderator's running calibration % at time of this annotation |

Columns not yet populated are exported as `null` / empty.

---

## Code Context

**Existing from Phase 1:**
- `mizan/backend/app/models/` — `Institution`, `User`, `UserRole` enum
- `mizan/backend/scripts/seed.py` — pattern for seed scripts (SQLAlchemy Session, idempotent `if not exists` checks)
- `mizan/backend/alembic/` — Alembic migration infrastructure (add new migration for Phase 2 tables)
- `mizan/backend/app/routers/auth.py` — auth pattern (JWT, role-based)
- DB port: 5433 on host, 5432 inside Docker
- bcrypt used directly (no passlib); email validated via regex (not email-validator)

**New tables needed in Phase 2:**
1. `content_examples` — the 500+ seeded training examples with labels
2. `jhsc_tweets` — all 403K JHSC rows for Observatory
3. (Export endpoint reads from both tables)

**Seed script pattern:**
Follow the existing `seed.py` pattern: idempotent (safe to run twice), uses SQLAlchemy Session,
reads from local files committed in `mizan/backend/data/` (new folder to create).

---

## Decisions That Are OUT OF SCOPE for Phase 2

These are for later phases — do not include:
- Moderator training UI (Phase 3)
- MARBERT inference (Phase 4)
- Observatory chart rendering (Phase 7)
- Bias Auditor (Phase 7)
- AI explanations (Phase 5)
- Calibration scoring (Phase 6)

Phase 2 delivers: data in the DB, JHSC loaded, export API endpoint, no UI work.

---

*Written: 2026-03-02 after user discussion via /gsd:discuss-phase 2*
