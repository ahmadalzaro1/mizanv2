---
phase: "1"
plan: "2"
subsystem: "database"
tags: [sqlalchemy, alembic, postgresql, schema, seed]
dependency_graph:
  requires: ["1-1-docker-compose"]
  provides: ["institutions-table", "users-table", "alembic-migrations", "seed-data"]
  affects: ["backend-auth", "backend-api"]
tech_stack:
  added: ["SQLAlchemy 2.0", "Alembic 1.13", "passlib[bcrypt] (seed uses bcrypt 5.x directly)"]
  patterns: ["declarative_base ORM", "Alembic autogenerate", "UUID primary keys", "enum roles"]
key_files:
  created:
    - backend/app/database.py
    - backend/app/models/institution.py
    - backend/app/models/user.py
    - backend/app/models/__init__.py
    - backend/alembic.ini
    - backend/alembic/env.py
    - backend/alembic/versions/a998e4136824_initial_schema_institutions_and_users.py
    - backend/scripts/seed.py
  modified: []
decisions:
  - "Used bcrypt directly in seed script instead of passlib due to passlib 1.7.4 incompatibility with bcrypt 5.x (Rule 1 auto-fix)"
  - "institution_id on User is nullable to allow super_admin with no institution affiliation"
  - "UserRole enum: super_admin / admin / moderator"
metrics:
  duration: "~15 minutes"
  completed_date: "2026-03-02"
  tasks_completed: 9
  files_created: 8
---

# Phase 1 Plan 2: PostgreSQL Schema and Alembic Migrations Summary

**One-liner:** SQLAlchemy ORM models for institutions and users with Alembic autogenerate migration and bcrypt-seeded demo accounts.

## What Was Built

Two PostgreSQL tables (`institutions`, `users`) backed by SQLAlchemy 2.0 declarative models, managed by Alembic migrations. A seed script populates a demo institution, super-admin, and demo admin for development and hackathon demo use.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Create `app/database.py` (engine, SessionLocal, Base, get_db) | 8793743 |
| 2 | Create Institution and User SQLAlchemy models with UserRole enum | 8793743 |
| 3 | Initialize Alembic inside backend container (`alembic init alembic`) | 8793743 |
| 4 | Update `alembic.ini` sqlalchemy.url to use `%(DATABASE_URL)s` | 8793743 |
| 5 | Replace `alembic/env.py` with model-aware version | 8793743 |
| 6 | Generate initial migration via `alembic revision --autogenerate` | 8793743 |
| 7 | Apply migration: `alembic upgrade head` | 8793743 |
| 8 | Create `scripts/seed.py` with idempotent institution and user seeding | 1628962 |
| 9 | Run seed script — demo institution, super-admin, demo admin created | 1628962 |

## Schema

### institutions
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(100) | UNIQUE, NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| role | ENUM(super_admin, admin, moderator) | NOT NULL |
| institution_id | UUID | FK -> institutions.id (CASCADE), NULLABLE |
| created_at | TIMESTAMP | NOT NULL |

## Verification Results

**Check 1 — Alembic current:**
```
a998e4136824 (head)
```

**Check 2 — Tables in database:**
```
 public | alembic_version | table | mizan
 public | institutions    | table | mizan
 public | users           | table | mizan
```

**Check 3 — Seeded users:**
```
 admin@mizan.local      | super_admin
 demo-admin@mizan.local | admin
```

All three checks passed.

## Seeded Accounts

| Account | Email | Password | Institution |
|---------|-------|----------|-------------|
| Super Admin | admin@mizan.local | mizan_admin_2026 | None (global) |
| Demo Admin | demo-admin@mizan.local | demo_admin_2026 | demo |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] passlib 1.7.4 incompatible with bcrypt 5.x in container**

- **Found during:** Task 9 (first seed run)
- **Issue:** `passlib.context.CryptContext` with bcrypt scheme fails at runtime — bcrypt 5.0.0 dropped `__about__` and changed hashing API that passlib 1.7.4 relied on. Error: `ValueError: password cannot be longer than 72 bytes` triggered during bcrypt backend detection.
- **Fix:** Replaced `CryptContext` in seed script with direct `bcrypt.hashpw()` calls. Added `hash_password()` helper wrapping the bcrypt library directly.
- **Impact on auth layer:** The same issue will affect any future use of `passlib.context.CryptContext`. Auth Plan (1.3+) should either use `bcrypt` directly or pin `passlib[bcrypt]==1.7.4` with `bcrypt<4.0`. Noted for Plan 1.3.
- **Files modified:** `backend/scripts/seed.py`
- **Commit:** 1628962

## Self-Check: PASSED

- [x] `backend/app/database.py` — exists
- [x] `backend/app/models/institution.py` — exists
- [x] `backend/app/models/user.py` — exists
- [x] `backend/app/models/__init__.py` — exists
- [x] `backend/alembic/env.py` — exists
- [x] `backend/alembic/versions/a998e4136824_initial_schema_institutions_and_users.py` — exists
- [x] `backend/scripts/seed.py` — exists
- [x] Commit 8793743 — exists (models + migration)
- [x] Commit 1628962 — exists (seed script)
- [x] Tables `institutions`, `users`, `alembic_version` confirmed in DB
- [x] Two users seeded with correct roles
