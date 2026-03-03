# Mizan Dataset Curation Pipeline

Pipeline for curating a high-quality Arabic hate speech benchmark dataset from multiple sources.

## Overview

This pipeline creates a balanced, high-quality dataset for the Mizan moderator training platform by:

1. **Loading** source datasets (JHSC, Let-Mi, MLMA)
2. **Mapping** labels to Mizan's 9-category schema
3. **Balancing** classes to 50/50 hate/not_hate
4. **Checking** quality and generating reports
5. **Exporting** to CSV, JSON, and Mizan DB formats
6. **Cleaning** encoding issues, removing duplicates, flagging borderline cases
7. **Re-balancing** after cleaning
8. **Final quality check**
9. **Exporting** cleaned dataset

---

## Final Dataset (After Cleaning)

| Metric | Value |
|--------|-------|
| **Total examples** | 392 |
| **Hate** | 196 (50%) |
| **Not hate** | 196 (50%) |
| **Encoding quality** | 99% |

### Hate Type Distribution
| Type | Count | Percentage |
|------|-------|------------|
| gender | 162 | 82.7% |
| race | 34 | 17.3% |

### Source Distribution
| Source | Count | Percentage |
|--------|-------|------------|
| jhsc | 196 | 50% |
| letmi | 160 | 40.8% |
| mlma | 36 | 9.2% |

### Dialect Distribution
| Dialect | Count | Percentage |
|---------|-------|------------|
| jordanian | 196 | 50% |
| levantine | 160 | 40.8% |
| mixed | 36 | 9.2% |

---

## Quality Improvements Made

1. **Encoding fixes:** Removed 49 examples with corrupted Unicode characters
2. **Duplicate removal:** Near-duplicates removed using text similarity
3. **Borderline review:** Flagged 5 examples with offensive terms in `not_hate` for manual review
4. **Balanced distribution:** 50/50 hate vs not_hate

---

## Output Files

```
output/
├── mizan_benchmark_v1.csv              # Original (before cleaning)
├── mizan_benchmark_v1.json             # Original (before cleaning)
├── mizan_content_examples.csv          # Original for Mizan DB
├── mizan_benchmark_v1_cleaned.csv      # ✅ Final cleaned dataset (CSV)
├── mizan_benchmark_v1_cleaned.json     # ✅ Final cleaned dataset (JSON)
├── mizan_content_examples_cleaned.csv  # ✅ Ready for Mizan DB import
├── flagged_examples.pkl                # Examples flagged for manual review
└── stats/
    ├── distribution_report.txt         # Original quality report
    └── final_quality_report.txt        # Final quality report
```

---

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline
python scripts/run_all.py

# Or run individual steps
python scripts/01_load_sources.py
python scripts/02_map_labels.py
python scripts/03_balance_dataset.py
python scripts/04_quality_check.py
python scripts/05_export.py
python scripts/06_clean_dataset.py
python scripts/07_rebalance_cleaned.py
python scripts/08_final_quality_check.py
python scripts/09_export_cleaned.py
```

---

## Import into Mizan

```bash
# Copy the cleaned file to Mizan's data directory
cp output/mizan_content_examples_cleaned.csv ../mizan/backend/data/seed_data.csv

# Then run Mizan's seed script
cd ../mizan
docker compose exec backend python -m scripts.seed_content
```

---

## Configuration

Edit `config.py` to adjust:
- `TARGET_TOTAL` - Total examples target (default: 500)
- `HATE_TYPE_TARGETS` - Distribution within hate categories
- Quality thresholds for cleaning

---

## Label Schema

### Labels
- `hate` - Content containing hate speech
- `not_hate` - Normal content without hate speech

### Hate Types (9 categories)
```python
HATE_TYPES = [
    "race",
    "religion",
    "ideology",
    "gender",
    "disability",
    "social_class",
    "tribalism",
    "refugee_related",
    "political_affiliation",
]
```

---

## Data Sources

| Dataset | Size | Dialect | License | Use |
|---------|------|---------|---------|-----|
| JHSC | 403K+ tweets | Jordanian | CC BY 4.0 | not_hate examples (dialect diversity) |
| Let-Mi | 5K tweets | Levantine | Research | gender-based hate |
| MLMA | 3K tweets | Mixed | Research | multi-target hate |

---

## Current Limitations

1. **Limited hate type coverage:** Only gender (82.7%) and race (17.3%) are represented
2. **Missing categories:** No examples for religion, ideology, disability, social_class, tribalism, refugee_related, political_affiliation
3. **Dataset size:** 392 examples is modest for ML training

---

## Recommendations for Expansion

1. **Add more datasets** with religion, tribalism, refugee-related hate types
2. **Use LLM augmentation** to generate synthetic examples for underrepresented categories
3. **Manual annotation** of JHSC negative examples to add fine-grained hate types
4. **Crowdsourced annotation** through Mizan platform

---

## License & Attribution

This dataset combines data from multiple sources:
- JHSC: CC BY 4.0
- Let-Mi: Research use
- MLMA: Research use

**Important:** Include source attribution when publishing or sharing this dataset.

---

*Last updated: 2026-03-03*
