# Requirements — Mizan

## v1 Requirements

### Moderator Training Interface (TRAIN)

- [ ] **TRAIN-01**: Moderator can view a piece of Arabic social media content (tweet/comment) and submit a hate speech label (hate / not hate)
- [ ] **TRAIN-02**: Moderator can select a hate speech type when labeling hate content (race, religion, ideology, gender, disability, social class, tribalism, refugee-related, political affiliation)
- [ ] **TRAIN-03**: After submitting a label, moderator sees the AI model's classification and confidence score
- [ ] **TRAIN-04**: After submitting a label, moderator sees an Arabic-language explanation of why the AI classified the content that way
- [ ] **TRAIN-05**: Moderator can mark whether they agree or disagree with the AI's classification
- [ ] **TRAIN-06**: Moderator sees a live calibration score (% agreement with ground truth) that updates after each labeled item
- [ ] **TRAIN-07**: Moderator can navigate through a training session of 10–50 examples in sequence

### Dataset & Content (DATA)

- [ ] **DATA-01**: Platform ships with 100+ pre-seeded Jordanian Arabic examples sourced from JHSC and OSACT5
- [ ] **DATA-02**: Each example has a ground-truth label from the annotation schema
- [ ] **DATA-03**: Examples are tagged with dialect (Jordanian/Levantine), content type, and hate speech category
- [ ] **DATA-04**: Admin can export all moderator annotations as JSON/CSV for dataset publication

### AI Copilot (AI)

- [ ] **AI-01**: MARBERT model classifies input text as hate/not-hate with a confidence score
- [ ] **AI-02**: System generates an Arabic-language natural language explanation of the model's decision (attention-based or LLM-generated)
- [ ] **AI-03**: Classification API returns a response within 3 seconds for a single text input
- [ ] **AI-04**: System falls back to XLM-RoBERTa for code-mixed (Arabic-English) inputs

### Admin Dashboard (ADMIN)

- [ ] **ADMIN-01**: Admin can view all moderators and their current calibration scores
- [ ] **ADMIN-02**: Admin can create a training session (select content batch, assign to moderator)
- [ ] **ADMIN-03**: Admin can see which content items have the most moderator disagreement
- [ ] **ADMIN-04**: Admin can download a calibration report (PDF or CSV) for their team

### Authentication & Institutions (AUTH)

- [ ] **AUTH-01**: User can create an account with email and password
- [ ] **AUTH-02**: User can log in and stay logged in across sessions (JWT or session cookie)
- [ ] **AUTH-03**: Institution admin can add moderator accounts to their organization
- [ ] **AUTH-04**: Moderators only see content and sessions assigned to their institution

### UI & Accessibility (UI)

- [ ] **UI-01**: All Arabic text renders correctly in RTL layout with appropriate font (Tajawal or IBM Plex Arabic)
- [ ] **UI-02**: Platform is usable on desktop web (Chrome, Firefox, Safari)
- [ ] **UI-03**: Interface language is Arabic (primary) with English option

---

## v2 Requirements (Deferred)

- Mobile-responsive layout
- OAuth (Google/Microsoft) login for institutions
- Real-time collaborative annotation (multiple annotators on same session)
- LLM-generated synthetic examples for underrepresented hate categories
- Dialect detection (auto-tag incoming content by dialect)
- Moderator fatigue detection (flag sessions where accuracy drops over time)
- Integration API for platforms to pipe content directly into training sessions
- Multi-language UI (French for North Africa expansion)

---

## Out of Scope

- **Mobile native app** — Desktop browser covers the demo use case; native app is a post-hackathon effort
- **Live moderation of external platforms** — Mizan trains humans; it is not a live content filter
- **Image/video moderation** — Text-only for v1; multimodal adds significant ML complexity
- **Billing/subscriptions** — Free tier for hackathon; monetization is a post-validation decision
- **Multi-dialect support beyond Jordanian/Levantine** — Other dialects dilute the focused research contribution
- **Model training in-platform** — Users cannot fine-tune the model through the UI; inference only

---

## Traceability

| REQ-ID | Phase |
|--------|-------|
| TRAIN-01 to TRAIN-07 | Phase 3 |
| DATA-01 to DATA-04 | Phase 2 |
| AI-01 to AI-04 | Phase 4 |
| ADMIN-01 to ADMIN-04 | Phase 7 |
| AUTH-01 to AUTH-04 | Phase 1 |
| UI-01 to UI-03 | Phase 3 |
