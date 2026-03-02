# STATE — Mizan

> Project memory. Updated by GSD workflow after each plan execution.

---

## Project Reference

**Name**: Mizan (ميزان — "the scale")
**Core value**: A moderator who completes a Mizan training session makes faster, more consistent hate speech decisions — and every session strengthens the underlying Jordanian Arabic benchmark dataset.
**Primary deadline**: JYIF Generative AI National Social Hackathon (Jordan) — 3-minute live demo
**The demo moment**: Tweet appears → moderator labels it → MARBERT classifies it → Arabic explanation appears

---

## Current Position

**Current phase**: Phase 1 — Foundation
**Current plan**: Not started
**Status**: Not started

```
Progress: [________] 0/8 phases complete
```

---

## Phase Status

| Phase | Status | Completed |
|-------|--------|-----------|
| 1. Foundation | Not started | - |
| 2. Data Pipeline | Not started | - |
| 3. Moderator Training UI | Not started | - |
| 4. MARBERT Inference API | Not started | - |
| 5. AI Explanation Layer | Not started | - |
| 6. Calibration Scoring | Not started | - |
| 7. Admin Dashboard | Not started | - |
| 8. Demo Polish | Not started | - |

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| ML Model | MARBERT (HuggingFace), XLM-RoBERTa (fallback) |
| Frontend | React, Vite |
| Database | PostgreSQL |
| UI Direction | RTL Arabic (Tajawal / IBM Plex Arabic) |

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| MARBERT as primary model | Best dialectal Arabic performance (F1=84%), trained on 1B Arabic tweets |
| XLM-RoBERTa fallback | Handles code-mixed Arabic-English inputs |
| FastAPI backend | PyTorch + HuggingFace require Python; FastAPI is fast to build |
| React + Vite frontend | RTL support, component ecosystem, fast iteration |
| PostgreSQL | Relational data fits annotation schema; flexible queries for calibration |
| Single demo account v1 auth | Simplifies build; multi-tenant can be added post-hackathon |
| Extended OSACT5 schema | 6 standard types + 3 Jordanian-specific (tribalism, refugee, political) |

---

## Accumulated Context

### Decisions Log
*(Populated as plans complete)*

### Todos Carried Forward
*(Populated during plan execution)*

### Blockers
*(None yet)*

---

## Session Continuity

**Last updated**: 2026-03-02
**Last action**: Roadmap created (8 phases, 26 requirements mapped)
**Next action**: Run `/gsd:plan-phase 1` to plan Foundation phase

---

## Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Requirements covered | 26/26 | 26/26 |
| Phases defined | 8 | 8 |
| Plans written | TBD | 0 |
| Plans complete | TBD | 0 |
| Demo path working | Yes (Phase 8) | No |

---

*Initialized: 2026-03-02*
