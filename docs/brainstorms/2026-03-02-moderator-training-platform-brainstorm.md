---
date: 2026-03-02
topic: moderator-training-platform
hackathon: JYIF Generative AI National Social Hackathon – Together for the Future
---

# Arabic Hate Speech Moderator Training Platform

## Context

Participant in the JYIF Generative AI National Social Hackathon (Jordan).
Hackathon themes: hate speech, misinformation, responsible GenAI in youth work.
Goal: build something with a strong demo, a research contribution, and a deployable platform.

---

## Core Concept (One Sentence)

> A moderator simulation platform that uses Jordanian-dialect hate speech data to train human moderators through AI-assisted labeling exercises — while simultaneously generating a validated, publishable Arabic hate speech corpus as a byproduct.

**Key insight:** The platform IS the research pipeline. Every label a moderator applies is a ground-truth annotation that builds the dataset automatically.

---

## Users

| User | Who | Pain |
|------|-----|------|
| Online Moderators | Employees at media, NGOs, platforms, gov | Untrained, inconsistent, burning out |
| Institutions | HR/Training at those orgs | No structured moderation training exists |
| Researchers / Civil Society | Academia, advocacy groups | No Jordanian Arabic hate speech dataset |

---

## POV Statement

> Jordanian institutions need a way to train content moderators consistently and rapidly because Arabic hate speech — especially in Jordanian dialect — is nuanced, culturally loaded, and massively underrepresented in AI tools, meaning moderators today rely on gut instinct, burn out quickly, and make contradictory decisions.

---

## How Might We

- HMW train moderators faster using AI feedback loops?
- HMW build a Jordanian Arabic hate speech dataset as a byproduct of platform usage?
- HMW make AI decisions explainable enough that moderators actually learn from them?
- HMW measure whether a moderator's judgment is improving over time?

---

## Platform Architecture (4 Core Screens)

### 1. Admin Dashboard (Institution side)
- Upload content batches for training sessions
- See moderator performance analytics
- Track team calibration scores over time

### 2. Moderator Training Interface
- Display a post/comment in Jordanian Arabic
- Moderator labels it (hate/not hate + category)
- AI reveals: reasoning + explanation → explainability layer
- Moderator learns from disagreements

### 3. AI Copilot (real-time assist)
- As moderator makes decisions, AI flags uncertainty
- Highlights contradictions with their own past decisions
- Builds consistency over time

### 4. Calibration Report
- Inter-annotator agreement scores
- Hardest cases (where humans and AI disagree)
- Exportable PDF report for institutions

---

## Research Contribution

- Curate existing datasets (OSACT, AJGT, Levantine Arabic sources)
- Augment with Jordanian-specific examples
- Multi-label annotation schema: hate speech type, dialect, severity, target group
- Output: **Jordanian Arabic Hate Speech Benchmark** — small, high-quality, citable
- Document annotation schema + curation methodology (2-page paper format minimum)

---

## Demo Story (3-min pitch)

> "Let me show you a real comment from a Jordanian social platform. Our platform shows it to a new moderator. They label it. The AI explains its reasoning. The moderator learns. After 20 examples, their accuracy improves by X%. And every label they give feeds back into our growing national dataset — the first of its kind for Jordanian Arabic."

---

## MVP Scope (for hackathon demo)

**Must-have:**
- [ ] Moderator training interface (labeling UX)
- [ ] AI explanation layer (Arabic NLP model reasoning)
- [ ] Basic progress/score tracker
- [ ] 50–100 pre-labeled Jordanian Arabic examples loaded in

**Nice-to-have:**
- [ ] Admin dashboard
- [ ] Calibration report export

**Research parallel track:**
- [ ] Annotation schema documentation
- [ ] Dataset curation methodology writeup

---

## Tech Stack (deferred — pending ML requirements)

Likely direction: Python backend (PyTorch, HuggingFace, Arabic NLP models like
CAMeL or AraBERT) + React/Next.js frontend. Stack decision deferred to planning phase.

---

## Open Questions

- Which existing datasets are available and accessible?
- What Arabic NLP models work best for Jordanian dialect specifically?
- Is the annotation schema multilabel or hierarchical?
- What's the institution onboarding flow?

## Next Steps

→ Research available Jordanian Arabic datasets and existing Arabic NLP models
→ Decide tech stack once ML requirements are clearer
→ `/gsd:new-project` to initialize project structure and roadmap
