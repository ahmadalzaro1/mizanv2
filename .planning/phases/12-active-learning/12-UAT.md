---
status: testing
phase: 12-active-learning
source: [12-01-SUMMARY.md, 12-02-SUMMARY.md, 12-03-SUMMARY.md]
started: 2026-03-03T19:00:00Z
updated: 2026-03-03T19:00:00Z
---

## Current Test

number: 1
name: Strategy Picker Visible on Training Page
expected: |
  Navigate to the Training page (/train). You should see three radio-style cards
  for choosing a sampling strategy: "تسلسلي" (Sequential), "عدم اليقين" (Uncertainty),
  and "عدم الاتفاق" (Disagreement). Each card should have an Arabic label and description.
awaiting: user response

## Tests

### 1. Strategy Picker Visible on Training Page
expected: Navigate to /train. Three radio-style cards appear for strategy selection: Sequential (تسلسلي), Uncertainty (عدم اليقين), and Disagreement (عدم الاتفاق) — each with Arabic label and description.
result: [pending]

### 2. Sequential Pre-Selected by Default
expected: On the Training page, the Sequential (تسلسلي) card is pre-selected with a green/highlighted border. The other two cards are not selected.
result: [pending]

### 3. Unavailable Strategies Show Disabled State
expected: If precompute_confidence has NOT been run, the Uncertainty card appears disabled/greyed with an Arabic message explaining why. If no moderator history exists, Disagreement also appears disabled with an Arabic reason.
result: [pending]

### 4. Start Session with Sequential Strategy
expected: With Sequential selected, click "ابدأ التدريب" (Start Training). A new training session starts normally — you see the first tweet to label.
result: [pending]

### 5. Strategy Badge During Session
expected: During a non-sequential session (uncertainty or disagreement), an amber or red badge appears above the progress bar showing the active strategy name. For sequential sessions, no badge appears.
result: [pending]

### 6. Strategy Chip in Session History
expected: After completing at least one session, return to /train. In the session history list, non-sequential sessions show a small strategy chip/tag next to the status badge. Sequential sessions do not show a chip.
result: [pending]

### 7. Strategy Availability API
expected: The backend returns strategy availability correctly — sequential always available, uncertainty available only if ai_confidence scores exist, disagreement available only if moderator label history exists.
result: [pending]

## Summary

total: 7
passed: 0
issues: 0
pending: 7
skipped: 0

## Gaps

[none yet]
