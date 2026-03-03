# Phase 7 Research — Analytics & Research Layer

> Research findings for Observatory + Bias Auditor implementation.

---

## Observatory — JHSC Temporal Data

### Data Available
- **403,688 JHSC tweets** in `jhsc_tweets` table (302,766 train + 100,923 test)
- Labels: negative (→ hate), neutral, positive, very_positive
- `tweet_year` and `tweet_month` columns exist but are **NULL** — deferred from Phase 2

### Twitter Snowflake ID → Timestamp
Twitter Snowflake IDs encode timestamp in the upper bits:
```python
TWITTER_EPOCH_MS = 1288834974657  # Nov 4, 2010 01:42:54.657 UTC
timestamp_ms = (tweet_id >> 22) + TWITTER_EPOCH_MS
```
This gives millisecond-precision timestamps for all tweets. JHSC covers 2014–2022.

### Backfill Strategy
Two approaches:
1. **Alembic migration with SQL** — Run `UPDATE jhsc_tweets SET tweet_year = ..., tweet_month = ...` using PostgreSQL bitwise ops. Fastest, no Python needed.
2. **Python script** — Read in chunks, compute in Python, bulk update. More readable but slower for 400K rows.

**Decision**: Use Alembic migration with raw SQL. PostgreSQL supports `>>` bitwise shift:
```sql
UPDATE jhsc_tweets
SET tweet_year = EXTRACT(YEAR FROM TO_TIMESTAMP(((id >> 22) + 1288834974657) / 1000.0)),
    tweet_month = EXTRACT(MONTH FROM TO_TIMESTAMP(((id >> 22) + 1288834974657) / 1000.0))
WHERE tweet_year IS NULL;
```

### Observatory API Shape
```json
GET /api/observatory/trends
Response: {
  "monthly": [
    {"year": 2014, "month": 1, "hate_count": 234, "total_count": 1200},
    ...
  ],
  "events": [
    {"year": 2015, "month": 9, "label_ar": "أزمة اللجوء السوري", "label_en": "Syrian refugee crisis"},
    ...
  ]
}
```

### Jordanian Historical Events (for timeline markers)
From published JHSC literature and Jordanian news:
1. **2014-06** — ISIS captures Mosul, regional refugee surge
2. **2015-02** — Muath al-Kasasbeh burned alive by ISIS (massive Jordanian reaction)
3. **2016-06** — Jordanian intelligence office attack in Baqaa camp
4. **2017-12** — Trump Jerusalem recognition (widespread protests)
5. **2018-06** — Jordanian teachers' strike + economic protests
6. **2019-10** — Gas deal with Israel protests
7. **2020-11** — Jordanian parliamentary elections
8. **2021-04** — Prince Hamzah incident / "sedition case"

---

## Bias Auditor — MARBERT Fairness Analysis

### Data Available
- **560 content_examples** with ground_truth_label + hate_type (10 categories)
- hate_type distribution: not all categories have equal representation
- Sources: JHSC (mapped to hate), Let-Mi (gender), MLMA (multi-label), AJ Comments

### Challenge: Running MARBERT Batch on 560 Examples
- Inference: ~250ms per example on MPS → ~140s for 560 examples
- Too slow for on-demand computation every page load
- Need caching strategy

### Approach: Precompute + Cache
1. **Backend endpoint `POST /api/audit/run`** — triggers batch inference on all content_examples
2. Stores results in a new `bias_audit_runs` table (run_id, computed_at, results JSON)
3. **`GET /api/audit/results`** — returns latest cached run
4. For hackathon demo: run once, cache indefinitely

### Metrics Per Category
For each hate_type:
- True Positives (TP): ground_truth=hate, predicted=hate
- False Positives (FP): ground_truth=not_hate, predicted=hate
- False Negatives (FN): ground_truth=hate, predicted=not_hate
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2 * (P * R) / (P + R)

**Binary mapping** (same as training): hate/offensive → hate, not_hate/spam → not_hate

### Bias Report Download
CSV format with columns: category, sample_count, precision, recall, f1, tp, fp, fn
Simple `text/csv` response from a dedicated endpoint.

---

## Frontend: D3.js Charts

### D3.js Choice
- D3.js v7 — ESM-compatible, TypeScript support via `@types/d3`
- Install: `npm install d3` + `npm install -D @types/d3`
- Use React refs for D3 mounting (hybrid React+D3 approach)

### Observatory Chart Design
- **Area/line chart** — X axis: months (2014–2022), Y axis: hate tweet count
- Stacked or layered area chart showing hate vs total volume
- Event markers: vertical dashed lines with Arabic labels
- Hover tooltip with month/count details

### Bias Auditor Chart Design
- **Horizontal bar chart** — categories on Y axis, F1 score on X axis (0–1)
- Color coding: red for low F1 (<0.5), amber (0.5–0.7), green (>0.7)
- Additional precision/recall bars as grouped bars
- Highlight weakest categories with Arabic labels

---

## Scope Decisions

| Item | In Scope | Rationale |
|------|----------|-----------|
| JHSC temporal backfill | Yes | Required for OBS-02 |
| Monthly aggregation API | Yes | Required for OBS-02 |
| Historical event markers | Yes | Required for OBS-03 (≥3 events) |
| D3.js timeline chart | Yes | Required for OBS-02 |
| MARBERT batch inference | Yes | Required for BIAS-01 |
| Per-category metrics | Yes | Required for BIAS-02 |
| Weakest category highlight | Yes | Required for BIAS-02 |
| CSV bias report download | Yes | Required for BIAS-03 |
| PDF report | No | CSV sufficient for v1; PDF adds complexity |

---

*Created: 2026-03-02*
