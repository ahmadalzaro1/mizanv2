# Mizan — Repository Map

A guide to every file and folder in this repo. Files marked with **[KEY]** are the most important ones to understand the system.

---

## Root

```
mizan/
├── docker-compose.yml     [KEY] Orchestrates all 3 services (DB, backend, frontend)
├── .env.example           [KEY] Template for environment variables — copy to .env
├── .gitignore                   Excludes .env, node_modules, model_cache, __pycache__
└── README.md                    Setup instructions and project overview
```

| File | What it does |
|------|-------------|
| `docker-compose.yml` | Defines PostgreSQL 16 (port 5433), FastAPI backend (port 8000), and Vite frontend (port 5173). One command starts everything. |
| `.env.example` | Contains DATABASE_URL, JWT_SECRET, VITE_API_URL, and optional ML model IDs. Defaults work out of the box. |

---

## Backend

### Entry Point

```
backend/
├── app/
│   └── main.py            [KEY] FastAPI app — loads ML models at startup, registers all routers
├── Dockerfile                   Python 3.11 container image
└── requirements.txt       [KEY] All Python dependencies (FastAPI, SQLAlchemy, PyTorch, Transformers)
```

| File | What it does |
|------|-------------|
| `app/main.py` | Creates the FastAPI app, adds CORS middleware, loads MARBERT + XLM-R models on startup via `lifespan`, mounts all 6 API routers. |
| `requirements.txt` | Pin-free deps: fastapi, uvicorn, sqlalchemy, alembic, torch, transformers, bcrypt, python-jose, pandas. |

### Configuration & Auth

```
backend/app/core/
├── config.py              [KEY] All environment variable loading (DB URL, JWT secret, model IDs)
├── deps.py                      Dependency injection (get_db session, get_current_user)
└── security.py                  JWT token creation and password hashing with bcrypt
```

| File | What it does |
|------|-------------|
| `config.py` | `Settings` class reads all env vars with sensible defaults. ML model IDs default to MARBERT Levantine + XLM-R multilingual. |
| `deps.py` | FastAPI dependencies: `get_db()` yields a SQLAlchemy session, `get_current_user()` extracts user from JWT Bearer token. |
| `security.py` | `create_access_token()` and `verify_password()` — standard JWT + bcrypt. |

### Database

```
backend/app/
├── database.py                  SQLAlchemy engine + session factory
└── models/
    ├── __init__.py              Re-exports all models for Alembic auto-detection
    ├── user.py              [KEY] User model with roles (super_admin, admin, moderator)
    ├── institution.py             Multi-tenant institution model
    ├── content_example.py   [KEY] 560 labeled hate speech examples (training data)
    ├── jhsc_tweet.py              403K Jordanian tweets for Observatory trends
    ├── training.py                Training sessions + per-item labels by moderators
    └── bias_audit.py              Audit run results stored as JSONB
```

| File | What it does |
|------|-------------|
| `user.py` | `User` model with `UserRole` enum (super_admin, admin, moderator). JWT auth checks role for protected endpoints. |
| `content_example.py` | Each row: Arabic text + ground truth label + hate category + source dataset. Used by Training and Bias Auditor. |
| `jhsc_tweet.py` | `JhscTweet` with BigInteger ID (Twitter IDs exceed INT max), label, and temporal fields for Observatory trends. |
| `bias_audit.py` | `BiasAuditRun` stores full audit results in a JSONB `results` column — per-category, per-source, confidence distributions, false positives. |

### API Routers

```
backend/app/routers/
├── auth.py                [KEY] POST /auth/login — JWT token endpoint
├── training.py            [KEY] Training session CRUD — start, label items, get summary
├── classify.py            [KEY] POST /api/classify — MARBERT/XLM-R inference on Arabic text
├── observatory.py               GET /api/observatory/trends — monthly hate speech counts + events
├── audit.py               [KEY] Bias auditor — run/stream audit, get results, download CSV
└── export.py                    GET /api/export — admin-only data export (CSV/JSON)
```

| File | What it does |
|------|-------------|
| `auth.py` | `POST /auth/login` returns a JWT token. `POST /auth/register` creates moderator accounts (admin-only). |
| `training.py` | `POST /api/training/sessions` starts a 20-item session. `PUT /api/training/sessions/{id}/items/{id}` submits moderator's label. Returns AI classification + explanation after each label. |
| `classify.py` | `POST /api/classify` takes Arabic text, detects code-mixing (30% Latin threshold), routes to MARBERT or XLM-R, returns label + confidence + AI explanation. |
| `observatory.py` | `GET /api/observatory/trends` returns monthly hate speech counts from 403K JHSC tweets + 8 hardcoded historical events (Arab Spring, COVID, etc.). |
| `audit.py` | `POST /api/audit/run/stream` runs MARBERT on all 560 examples with SSE progress streaming. Captures per-source metrics, confidence distributions, and false positive samples in one pass. `GET /api/audit/results` returns cached results. |

### ML Services

```
backend/app/
├── schemas/
│   ├── auth.py                  Login request/response schemas
│   ├── classify.py              Classification request/response schemas
│   └── training.py              Training session schemas
└── services/
    ├── ml_models.py       [KEY] ModelManager — loads MARBERT + XLM-R, runs inference
    └── explanation.py     [KEY] AI explanation — attention-based keywords + Arabic templates
```

| File | What it does |
|------|-------------|
| `ml_models.py` | `ModelManager.load_models()` downloads and caches MARBERT + XLM-R from HuggingFace. `classify()` runs inference with softmax confidence. Code-mixed detection routes to XLM-R when >30% Latin characters. |
| `explanation.py` | `ExplanationService` extracts top-3 attention-weighted keywords from the last transformer layer, then generates Arabic prose explanation using templates keyed to label/confidence/category. |

### Database Migrations

```
backend/alembic/
├── env.py                       Alembic config — connects to DATABASE_URL
├── script.py.mako               Migration template
└── versions/
    ├── a998e4..._initial_schema.py          Users + institutions tables
    ├── b1f2c3..._phase2_data_tables.py      content_examples + jhsc_tweets
    ├── c3d4e5..._phase3_training_tables.py  training_sessions + training_items
    ├── d4e5f6..._phase5_ai_explanation.py   confidence + keywords columns
    ├── e7f8a9..._phase7_jhsc_temporal.py    year/month columns on jhsc_tweets
    └── f8a9b0..._phase7_bias_audit_runs.py  bias_audit_runs table with JSONB
```

Run all migrations: `docker compose exec backend alembic upgrade head`

### Seed Scripts

```
backend/scripts/
├── seed.py                [KEY] Creates super-admin + demo admin accounts
├── seed_content.py        [KEY] Loads 560 labeled examples from 4 datasets into content_examples
└── seed_jhsc.py                 Loads 403K Jordanian tweets into jhsc_tweets
```

| File | What it does |
|------|-------------|
| `seed.py` | Creates `admin@mizan.local` (super_admin) and `demo-admin@mizan.local` (admin) with bcrypt-hashed passwords. Idempotent. |
| `seed_content.py` | Reads CSV/Excel from `data/` folder, normalizes labels across 4 datasets (JHSC, MLMA, L-HSAB, Let-Mi) into a unified hate/not_hate + 9-category schema. 560 total examples. |
| `seed_jhsc.py` | Bulk-inserts 403K tweets with Snowflake ID bitwise extraction for year/month. Powers the Observatory timeline. |

### Source Datasets

```
backend/data/
├── README.md                    Dataset descriptions, sizes, and licenses
├── jhsc/                        Jordanian Hate Speech Corpus (403K tweets, CC BY 4.0)
├── mlma/                        Multilingual Multi-Aspect hate speech (3.3K, EMNLP 2019)
├── let-mi/                      Levantine hate speech + misogyny (5.8K, EACL 2021)
├── aj-comments/                 Al Jazeera comments (32K, CrowdFlower)
└── arabic-religious/            Arabic religious hate (BNS/PMI, reserved)
```

---

## Frontend

### Entry Point

```
frontend/
├── index.html                   Single HTML shell — Vite injects React here
├── src/
│   ├── main.tsx           [KEY] React root — renders App with BrowserRouter
│   └── App.tsx            [KEY] Route definitions — maps URLs to page components
├── Dockerfile                   Node 20 Alpine container
├── package.json                 Dependencies (React 18, D3 7, Tailwind 3.4, Axios)
└── vite.config.ts               Vite dev server config
```

| File | What it does |
|------|-------------|
| `App.tsx` | React Router routes: `/login`, `/dashboard`, `/training/*`, `/observatory`, `/bias-auditor`, `/admin/*`. All routes except login wrapped in `ProtectedRoute`. |
| `main.tsx` | Renders `<App />` inside `<AuthProvider>` and `<BrowserRouter>`. |

### Pages

```
frontend/src/pages/
├── Login.tsx                    Login form — calls POST /auth/login, stores JWT
├── Dashboard.tsx          [KEY] Landing page — 3 persona cards linking to each tool
├── TrainingPage.tsx       [KEY] Start training session — shows session history
├── TrainingSession.tsx    [KEY] Active labeling — 20 items, 2-step (hate/not → category)
├── SessionSummary.tsx           Post-session results with calibration score
├── ObservatoryPage.tsx    [KEY] D3 timeline chart + event markers + summary cards
├── BiasAuditorPage.tsx    [KEY] 4-tab fairness dashboard with SSE progress streaming
└── admin/
    └── CreateModerator.tsx      Admin form to create moderator accounts
```

| File | What it does |
|------|-------------|
| `Dashboard.tsx` | Three persona-themed cards: Khaled (Training, green), Rania (Observatory, red), Lina (Bias Auditor, blue). Each links to its tool. |
| `TrainingSession.tsx` | Fetches 20 items, presents Arabic tweet text, moderator selects hate/not_hate then picks from 9 Arabic categories. Shows AI explanation + feedback after each label. |
| `ObservatoryPage.tsx` | Calls `/api/observatory/trends`, renders D3 area chart of monthly hate speech volume (2015-2023) with event markers (Arab Spring, COVID, etc.). |
| `BiasAuditorPage.tsx` | 4 tabs: Overview (insight summary + BiasChart), Confidence (histogram grid), Sources (per-dataset table), False Positives (sample cards). SSE progress bar during 560-example audit run. |

### Components

```
frontend/src/components/
├── Layout.tsx             [KEY] Shared page shell — navbar, RTL Arabic, max-width container
├── ProtectedRoute.tsx           Redirects to /login if no JWT token
├── TweetCard.tsx                Displays Arabic tweet with highlight color (amber=hate, green=safe)
├── AIExplanation.tsx            Blue card showing Arabic AI explanation + trigger words
├── LabelSelector.tsx            Two-step label UI — binary then 9 Arabic categories
├── FeedbackReveal.tsx           Shows ground truth vs moderator label after submission
├── CalibrationScore.tsx         Live % agreement score with color-coded Arabic display
├── ProgressBar.tsx              Training session progress (items completed / total)
├── SessionHistoryList.tsx       List of past training sessions with scores
├── BiasChart.tsx                D3 horizontal grouped bar chart — per-category F1/precision/recall
├── ConfidenceHistogram.tsx      D3 small multiples 3x3 grid — confidence distribution per category
├── SourceBreakdownTable.tsx     Per-dataset metrics table with color-coded F1/FPR cells
├── FalsePositiveList.tsx        Cards showing misclassified non-hate examples with confidence bars
└── TimelineChart.tsx            D3 area chart — Observatory monthly hate speech trends
```

### API Clients & Utilities

```
frontend/src/lib/
├── api.ts                 [KEY] Axios instance with JWT Bearer token (reads from localStorage)
├── auth.tsx               [KEY] AuthProvider context — login/logout, token storage
├── audit-api.ts                 Bias Auditor API client — includes SSE streaming via fetch/ReadableStream
├── training-api.ts              Training session API client
├── observatory-api.ts           Observatory trends API client
├── types.ts                     Shared TypeScript interfaces
└── format.ts                    toArabicDigits() — converts 0-9 to Arabic-Indic numerals
```

| File | What it does |
|------|-------------|
| `api.ts` | Creates an Axios instance with `baseURL` from env and interceptor that attaches `Authorization: Bearer {token}` from `localStorage.getItem('mizan_token')`. All API clients import this. |
| `auth.tsx` | React context providing `login()`, `logout()`, `user`, `token`. Wraps the entire app. |
| `audit-api.ts` | `runAuditStream()` uses `fetch()` + `ReadableStream` (not EventSource) to support JWT headers during SSE streaming. |

### E2E Tests

```
frontend/e2e/
├── global-setup.ts        [KEY] Logs in before all tests, saves auth state
├── auth.spec.ts                 Login flow, token storage, protected route redirect
├── dashboard.spec.ts            Dashboard cards visible, navigation to all 3 tools
├── training.spec.ts             Start session, label items, calibration score, back nav
├── observatory.spec.ts          Timeline chart renders, event legend, summary cards
└── bias-auditor.spec.ts         4-tab layout, tab navigation, section headers
```

Run tests: `cd frontend && npx playwright test`

### Config Files

```
frontend/
├── tailwind.config.js           Custom colors (mizan-navy, mizan-surface), Tajawal font
├── postcss.config.js            PostCSS with Tailwind + autoprefixer
├── tsconfig.json                TypeScript strict mode config
├── tsconfig.node.json           TypeScript config for Vite/Node files
├── tsconfig.e2e.json            TypeScript config for Playwright tests
├── playwright.config.ts         Playwright browser test config
└── .dockerignore                Excludes node_modules from Docker build context
```

---

## Essential Files Quick Reference

If you're trying to understand the system, start with these files in order:

| # | File | Why |
|---|------|-----|
| 1 | `docker-compose.yml` | How the 3 services connect |
| 2 | `backend/app/main.py` | Backend entry point, model loading |
| 3 | `backend/app/routers/classify.py` | Core ML inference endpoint |
| 4 | `backend/app/services/ml_models.py` | How MARBERT + XLM-R are loaded and used |
| 5 | `frontend/src/App.tsx` | All frontend routes |
| 6 | `frontend/src/pages/Dashboard.tsx` | Landing page, links to all 3 tools |
| 7 | `frontend/src/pages/TrainingSession.tsx` | Main interactive feature |
| 8 | `frontend/src/pages/BiasAuditorPage.tsx` | Most complex page (4 tabs, SSE, D3) |
| 9 | `backend/app/routers/audit.py` | Most complex backend (SSE streaming, metrics) |
| 10 | `backend/scripts/seed_content.py` | How training data is prepared from raw datasets |
