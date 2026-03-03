"""
Configuration for dataset curation pipeline.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List

# Base paths
BASE_DIR = Path(__file__).parent
SOURCES_DIR = BASE_DIR / "sources"
OUTPUT_DIR = BASE_DIR / "output"
STATS_DIR = OUTPUT_DIR / "stats"

# Source data paths (relative to project root)
PROJECT_ROOT = BASE_DIR.parent
MIZAN_DATA_DIR = PROJECT_ROOT / "mizan" / "backend" / "data"

# Source files
SOURCE_FILES = {
    "jhsc_train": MIZAN_DATA_DIR / "jhsc" / "annotated-hatetweets-4-classes_train.csv",
    "jhsc_test": MIZAN_DATA_DIR / "jhsc" / "annotated-hatetweets-4-classes_test.csv",
    "letmi": MIZAN_DATA_DIR / "let-mi" / "let-mi_train_part.csv",
    "mlma": MIZAN_DATA_DIR / "mlma" / "ar_dataset.csv",
    "aj_comments": MIZAN_DATA_DIR / "aj-comments" / "AJCommentsClassification-CF.xlsx",
}

# Output directories
SOURCES_DIR = BASE_DIR / "sources"
OUTPUT_DIR = BASE_DIR / "output"
STATS_DIR = OUTPUT_DIR / "stats"

# Mizan annotation schema
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


@dataclass
class MizanExample:
    """Unified schema for Mizan benchmark"""

    id: str
    text: str
    source_dataset: str
    dialect: str
    label: str  # "hate" or "not_hate"
    hate_type: str | None  # One of HATE_TYPES or None
    confidence: float
    original_label: str
    notes: str | None


# Dataset balance settings
TARGET_TOTAL = 500
TARGET_HATE_RATIO = 0.5  # 50% hate, 50% not_hate

# Hate type distribution (within hate examples)
HATE_TYPE_TARGETS = {
    "gender": 30,
    "religion": 25,
    "race": 20,
    "ideology": 15,
    "disability": 5,
    "social_class": 5,
}

# Output files
OUTPUT_CSV = OUTPUT_DIR / "mizan_benchmark_v1.csv"
OUTPUT_JSON = OUTPUT_DIR / "mizan_benchmark_v1.json"
STATS_REPORT = STATS_DIR / "distribution_report.txt"

# MLMA target column mapping
MLMA_TARGET_MAP = {
    "individual": None,
    "group": "social_class",
    "religious": "religion",
    "race": "race",
    "gender": "gender",
    "sexual_orientation": "ideology",
    "disability": "disability",
    "origin": "race",  # Map origin to race
    "other": None,
}
