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

- [ ] **DATA-01**: Platform ships with 100+ pre-seeded Arabic examples sourced from JHSC (Jordanian dialect), OSACT5 (fine-grained schema), L-HSAB (Levantine), and Let-Mi (Levantine gender hate)
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

### Observatory — Trend Analysis (OBS)

- [ ] **OBS-01**: JHSC temporal data (2014–2022, aggregated by month/year and category) is loaded into the database and queryable via API
- [ ] **OBS-02**: Observatory displays a timeline chart of Jordanian hate speech volume broken down by hate type category
- [ ] **OBS-03**: Observatory marks real Jordanian historical events on the timeline (refugee influx 2015–2016, elections 2020, etc.)

### Bias Auditor (BIAS)

- [x] **BIAS-01**: System runs MARBERT inference on a categorized JHSC sample and records performance metrics per hate category
- [x] **BIAS-02**: Bias Auditor displays F1/precision/recall breakdown by all 9 hate categories, highlighting weakest categories
- [x] **BIAS-03**: Researcher can download a bias report (PDF or CSV) summarizing model performance by category and target group

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

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 1: Foundation | Pending |
| AUTH-02 | Phase 1: Foundation | Pending |
| AUTH-03 | Phase 1: Foundation | Pending |
| AUTH-04 | Phase 1: Foundation | Pending |
| DATA-01 | Phase 2: Data Pipeline | Pending |
| DATA-02 | Phase 2: Data Pipeline | Pending |
| DATA-03 | Phase 2: Data Pipeline | Pending |
| DATA-04 | Phase 2: Data Pipeline | Pending |
| TRAIN-01 | Phase 3: Moderator Training UI | Pending |
| TRAIN-02 | Phase 3: Moderator Training UI | Pending |
| TRAIN-05 | Phase 3: Moderator Training UI | Pending |
| TRAIN-07 | Phase 3: Moderator Training UI | Pending |
| UI-01 | Phase 3: Moderator Training UI | Pending |
| UI-02 | Phase 3: Moderator Training UI | Pending |
| UI-03 | Phase 3: Moderator Training UI | Pending |
| AI-01 | Phase 4: MARBERT Inference API | Pending |
| AI-03 | Phase 4: MARBERT Inference API | Pending |
| AI-04 | Phase 4: MARBERT Inference API | Pending |
| AI-02 | Phase 5: AI Explanation Layer | Pending |
| TRAIN-03 | Phase 5: AI Explanation Layer | Pending |
| TRAIN-04 | Phase 5: AI Explanation Layer | Pending |
| TRAIN-06 | Phase 6: Calibration Scoring | Pending |
| ADMIN-01 | Phase 7: Admin Dashboard | Pending |
| ADMIN-02 | Phase 7: Admin Dashboard | Pending |
| ADMIN-03 | Phase 7: Admin Dashboard | Pending |
| ADMIN-04 | Phase 7: Admin Dashboard | Pending |
