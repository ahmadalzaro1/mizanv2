# Mizan — Arabic Hate Speech Moderator Training Platform

## What This Is

Mizan (ميزان — "the scale") is a three-component Arabic hate speech platform serving
Jordan's researchers, policy makers, and content moderators through one unified system.

**Component 1 — Moderator Training (Khaled)**
Jordanian institutions train content moderators via AI-assisted labeling. Moderators
review real social media content, submit labels, and receive structured feedback from
a MARBERT-based AI copilot that explains its reasoning in Arabic. Every annotation
feeds a publishable Jordanian Arabic benchmark dataset — the first fine-grained one
with tribalism, refugee-related, and political affiliation categories.

**Component 2 — Observatory (Rania)**
A public-facing trend visualization showing 8 years of Jordanian hate speech data
(JHSC 2014–2022), broken down by category and correlated with real historical events
(refugee influx, elections, COVID). First longitudinal study of Jordanian hate speech.

**Component 3 — Bias Auditor (Lina)**
A research tool that runs MARBERT against categorized JHSC data and surfaces where
the model fails — by hate type, by target group. Provides the first published
performance breakdown of MARBERT on Jordanian dialect hate speech.

## Three Personas

| Persona | Role | Pain | What Mizan gives them |
|---------|------|------|----------------------|
| **Khaled**, 28 | Content moderator, Jordanian news platform | 400+ ambiguous posts/day, no training, no feedback | AI-assisted sessions, calibration score, Arabic explanations |
| **Rania**, 42 | Digital safety officer, Jordanian NGO | No evidence base to advocate for hate speech programs | 8-year trend data, event correlations, downloadable reports |
| **Lina**, 26 | NLP researcher, University of Jordan | Models don't work on Jordanian dialect, no honest benchmarks | MARBERT bias breakdown by category, citable performance data |

## Core Value

One platform generates the research contribution (Khaled's labels), validates the
model (Lina's audit), and makes the problem visible to funders (Rania's observatory).
The three outputs reinforce each other — the platform is the research pipeline.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Moderator can view Arabic/Jordanian dialect social media content and label it
- [ ] AI copilot displays classification + Arabic-language explanation of reasoning
- [ ] Moderator receives calibration score that updates as they label
- [ ] Platform ships with 50–100 pre-loaded Jordanian Arabic examples from JHSC/OSACT5
- [ ] Admin can view team-level calibration analytics
- [ ] Institution can create an account and add moderators
- [ ] Annotation schema covers: hate/not-hate + type (race, religion, ideology, gender, disability, social class, tribalism, refugee-related, political affiliation)
- [ ] UI renders Arabic text correctly (RTL, appropriate fonts)
- [ ] Researcher/admin can export annotations as structured dataset (JSON/CSV)

### Out of Scope (v1)

- Mobile app — desktop web only for now
- Real-time moderation of live platforms — this is a training tool, not a live filter
- Support for dialects other than Jordanian/Levantine — other dialects can be added later
- Full multi-tenant SSO/enterprise auth — simple email/password login for v1
- Payment or subscription billing — free for hackathon demo
- Video/image content moderation — text only for v1

## Context

### Hackathon
JYIF Generative AI National Social Hackathon — "Together for the Future" (Jordan).
Theme: hate speech in digital spaces, responsible GenAI in youth work.
Audience: jury of AI expert, youth sector professional, policy representative.
Pitch format: 3-minute live demo. Strong demo is critical.

### Research Findings (Deep Research — 2026-03-02)
Full report: `docs/research/2026-03-02-arabic-hatespeech-deep-research.md`

Key dataset: JHSC — 403,688 Jordanian tweets (2014–2022), κ=0.60, F1=0.62 max.
Key gap: No fine-grained Jordanian benchmark exists. No Arabic moderator training platform exists.
Target annotation quality: κ≥0.75 (beats current state of the art).

### The Dual-Output Design
The platform is the research pipeline. Every moderator label = a ground-truth
annotation for the benchmark dataset. The research contribution emerges from
normal platform usage, not a separate workstream.

## Constraints

- **ML Stack**: Python backend required — PyTorch and HuggingFace for MARBERT inference
- **Language**: Arabic RTL text rendering throughout the entire UI is non-negotiable
- **Model**: MARBERT as primary model (best for dialectal Arabic); XLM-RoBERTa for code-mixed text
- **Data**: Must seed from existing JHSC/OSACT5 data — cannot build cold
- **Demo**: Must have a working 3-minute demo path on pitch day
- **Buildability**: Solo developer using Claude Code + GSD workflow

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| MARBERT as primary model | Trained on 1B Arabic tweets, best dialectal performance (F1=84%) | — Pending |
| Python/FastAPI backend | PyTorch + HuggingFace require Python; FastAPI is fast to build | — Pending |
| React + Vite frontend | RTL support, component ecosystem, fast iteration | — Pending |
| PostgreSQL for data | Annotation data is relational; needs query flexibility for calibration scores | — Pending |
| Extended OSACT5 annotation schema | Covers standard 6 types + 3 Jordanian-specific (tribalism, refugee, political) | — Pending |
| Single demo account for v1 auth | Simplifies build, multi-tenant can be added post-hackathon | — Pending |

---
*Last updated: 2026-03-02 after initialization*
