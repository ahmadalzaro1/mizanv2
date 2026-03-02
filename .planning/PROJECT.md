# Mizan — Arabic Hate Speech Moderator Training Platform

## What This Is

Mizan (ميزان — "the scale") is a web platform that helps Jordanian institutions
train their content moderators on Arabic/Jordanian dialect hate speech through
AI-assisted labeling exercises. Moderators review real social media content,
make judgments, and receive structured feedback from a MARBERT-based AI copilot
that explains its reasoning in Arabic. Every annotation moderators submit feeds
a publishable Jordanian Arabic benchmark dataset — the first fine-grained one of
its kind.

## Core Value

A moderator who finishes a Mizan training session makes faster, more consistent
hate speech decisions than one who didn't — and every session they complete makes
the underlying dataset stronger.

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
