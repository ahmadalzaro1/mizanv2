# Phase 1 — Foundation: Context

> Decisions locked by user discussion on 2026-03-02.
> Researcher and planner must follow these exactly — do not re-ask.

---

## Institution & User Model

**Institutions are seeded manually.**
No public registration flow. You (the developer) create institution records directly in the database. There is no sign-up page for institutions in v1.

**Roles: admin and moderator on the same account.**
A user has a role field: `super_admin`, `admin`, or `moderator`. An admin can also do labeling sessions — one person can hold both admin and moderator responsibilities. No strict account separation required.

**Admin creates moderator accounts directly.**
There is no invite link or join code flow. The admin fills in name + email + password and the account is immediately ready. No email sending required in v1.

**Observatory and Bias Auditor are accessible to any logged-in user.**
No special role required to view the analytics views. Any authenticated user (admin or moderator) can access `/observatory` and `/audit`.

**Super-admin account exists.**
One seeded super-admin account (the developer) that can see all institutions and all data. Hardcoded or seeded via a script — not creatable through the UI.

---

## Auth Mechanism

**JWT tokens stored in localStorage.**
On login, the server issues a JWT. The frontend stores it in localStorage. No expiry — the user stays logged in until they explicitly log out. No refresh token flow needed for v1.

**Auth flow:**
1. POST `/auth/login` with email + password → returns JWT
2. Frontend stores JWT in localStorage
3. All subsequent API requests include `Authorization: Bearer <token>`
4. Protected routes redirect to login if no token present

---

## Project Structure

**Single repo, two top-level folders.**

```
mizan/
  backend/          # FastAPI + MARBERT + ML
  frontend/         # React + Vite
  docker-compose.yml
  .env.example
  README.md
```

**Frontend routing — one React app, three sections:**

```
frontend/src/
  pages/
    observatory/    # /observatory — Rania persona
    bias-auditor/   # /audit — Lina persona
    training/       # /train — Khaled persona
  components/       # shared UI components
  lib/              # API client, utils
```

All three components are pages within a single React application. A shared navigation bar switches between the three views.

---

## Local Dev Setup

**Full Docker — everything containerized.**
`docker compose up` starts the entire stack. Three services:
- `db` — PostgreSQL
- `backend` — FastAPI (with MARBERT loaded inside it)
- `frontend` — React/Vite dev server

Hot reload for both frontend (Vite) and backend (uvicorn `--reload`) must work inside Docker via volume mounts.

**MARBERT runs inside the FastAPI container.**
No separate ML service container. The model loads when FastAPI starts. The backend container will need sufficient memory allocated (at least 4GB) for the model weights.

---

## Code Context

No existing code — greenfield project. These are the only files that exist:
- `.planning/` — GSD planning files
- `docs/` — Research and hackathon documentation

The planner should scaffold the entire project structure from scratch.

---

## Decisions That Are OUT OF SCOPE for Phase 1

These will be built in later phases — do not include in Phase 1 plans:
- MARBERT inference endpoint (Phase 4)
- Arabic RTL UI (Phase 3)
- Observatory charts (Phase 7)
- Bias Auditor (Phase 7)
- Seed data / JHSC loading (Phase 2)

Phase 1 delivers: running stack + auth + empty DB schema + Docker setup.

---

*Written: 2026-03-02 after user discussion via /gsd:discuss-phase 1*
