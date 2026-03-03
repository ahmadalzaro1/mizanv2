# Mizan (ميزان)

Arabic hate speech analysis platform — moderator training, trend observatory, and model bias auditing.

Built for the JYIF Generative AI National Social Hackathon (Erasmus+, Jordan).

## Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/YOUR_USERNAME/mizan.git
cd mizan

# 2. Create env file
cp .env.example .env

# 3. Start everything
docker compose up --build
```

First startup takes 5-10 minutes (downloads ML models ~2.7GB).

Once running:
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

## Setup the Database

After containers are running, open a new terminal:

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create admin accounts
docker compose exec backend python scripts/seed.py

# Seed training data (560 labeled examples)
docker compose exec backend python -m scripts.seed_content

# Seed observatory data (403K Jordanian tweets)
docker compose exec backend python -m scripts.seed_jhsc
```

## Default Accounts

After seeding, two accounts are available:

| Role  | Email                  | Password           |
|-------|------------------------|---------------------|
| Super Admin | admin@mizan.local | mizan_admin_2026   |
| Demo Admin  | demo-admin@mizan.local | demo_admin_2026 |

Create moderator accounts from the admin panel after logging in.

## What's Inside

| Component | What it does |
|-----------|-------------|
| **Moderator Training** | AI-assisted hate speech labeling practice with calibration scoring |
| **Observatory** | 8-year Jordanian hate speech trends from JHSC dataset (D3 timeline) |
| **Bias Auditor** | MARBERT fairness analysis — confidence histograms, per-source breakdown, false positive viewer |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy 2.0, Alembic |
| ML | MARBERT (Levantine Arabic), XLM-RoBERTa (code-mixed fallback) |
| Frontend | React, Vite, Tailwind CSS, D3.js |
| Database | PostgreSQL 16 |
| Infrastructure | Docker Compose |

## Project Structure

```
mizan/
├── backend/
│   ├── app/
│   │   ├── routers/       # API endpoints (auth, training, classify, observatory, audit)
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # ML inference, AI explanations
│   │   └── core/          # Config, auth, database setup
│   ├── alembic/           # Database migrations
│   ├── data/              # Source datasets (JHSC, OSACT5, L-HSAB, Let-Mi)
│   └── scripts/           # Database seeding scripts
├── frontend/
│   ├── src/
│   │   ├── pages/         # Route pages (Dashboard, Training, Observatory, BiasAuditor)
│   │   ├── components/    # Reusable UI (charts, cards, layout)
│   │   └── lib/           # API clients, auth, utilities
│   └── e2e/               # Playwright end-to-end tests
├── docker-compose.yml
└── .env.example
```

## Services

| Service  | Port | Description |
|----------|------|-------------|
| db       | 5433 | PostgreSQL 16 (mapped to host 5433) |
| backend  | 8000 | FastAPI + MARBERT inference |
| frontend | 5173 | React + Vite dev server |

## Datasets

| Dataset | Source | Size | License |
|---------|--------|------|---------|
| JHSC | Jordanian Hate Speech Corpus | 403K tweets | CC BY 4.0 |
| L-HSAB | Levantine Hate Speech & Abusive Language | 5.8K tweets | Research |
| MLMA | Multilingual Multi-Aspect hate speech | 3.3K tweets | Research |
| AJ Comments | Al Jazeera reader comments | 32K comments | CrowdFlower |

## Local Development (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
DATABASE_URL=postgresql://mizan:mizan_dev@localhost:5433/mizan \
  python -m uvicorn app.main:app --port 8000 --reload

# Frontend
cd frontend
npm install
npm run dev
```

## License

MIT
