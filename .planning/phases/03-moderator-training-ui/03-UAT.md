# Phase 3 — Moderator Training UI: UAT Criteria

## Acceptance Tests

### AT-01: RTL Arabic rendering (UI-01)
- [ ] All Arabic text renders right-to-left throughout the training interface
- [ ] Tajawal font loads and displays correctly
- [ ] No LTR bleed on any element (navigation, labels, buttons, tweet text)
- [ ] Arabic numerals display correctly in progress indicators

### AT-02: Start training session (TRAIN-07)
- [ ] Moderator clicks "Start Training" on /train page
- [ ] System creates a session with 20 random examples
- [ ] Moderator is navigated to the first example
- [ ] Examples come from the 560 seeded content_examples

### AT-03: Label submission — hate (TRAIN-01, TRAIN-02)
- [ ] Moderator sees Arabic tweet text clearly
- [ ] Moderator selects "خطاب كراهية" (hate)
- [ ] 9 category buttons appear
- [ ] Moderator selects one category (e.g., "ديني" / religion)
- [ ] Moderator clicks "إرسال" (Submit)
- [ ] Label is saved to the database

### AT-04: Label submission — not hate (TRAIN-01)
- [ ] Moderator selects "ليس كراهية" (not hate)
- [ ] No category selection required
- [ ] Moderator clicks "إرسال" (Submit)
- [ ] Label is saved to the database

### AT-05: Ground truth feedback
- [ ] After submitting, the correct answer (ground truth) is revealed
- [ ] Green checkmark shown when moderator matches ground truth
- [ ] Red X shown when moderator doesn't match
- [ ] Ground truth label and hate type displayed clearly

### AT-06: Navigation — forward and backward
- [ ] "Next" button advances to the next example
- [ ] "Previous" button goes back to the previous example
- [ ] Previous answers are visible when navigating back
- [ ] Moderator can change a previous answer
- [ ] Progress bar updates correctly

### AT-07: Session completion
- [ ] After all 20 examples labeled, session auto-completes
- [ ] Moderator is redirected to summary page
- [ ] Summary shows correct count (e.g., "14/20") and percentage ("70%")
- [ ] Score indicator shows appropriate message (excellent/good/needs improvement)

### AT-08: Session history
- [ ] /train page shows list of past sessions
- [ ] Each session shows date, status, and score
- [ ] Completed sessions have "Review" link → summary page
- [ ] In-progress sessions have "Continue" link → labeling view

### AT-09: Second session excludes used examples
- [ ] Starting a second session assigns different examples
- [ ] No overlap with examples from the first session

### AT-10: Cross-browser (UI-02)
- [ ] Training flow works in Chrome desktop
- [ ] Training flow works in Firefox desktop
- [ ] Training flow works in Safari desktop

---

## Non-functional
- Tailwind CSS is installed and active
- Shared Layout component wraps all protected pages
- Backend API endpoints are authenticated (JWT required)
- Moderators only see their own sessions

---

*Phase 3 UAT — 2026-03-02*
