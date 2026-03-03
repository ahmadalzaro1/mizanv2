"""Pre-compute MARBERT confidence scores for all content_examples.

Run once after migration:
    cd mizan/backend
    PYTORCH_ENABLE_MPS_FALLBACK=1 \\
    DATABASE_URL=postgresql://mizan:mizan_dev@localhost:5433/mizan \\
    MARBERT_MODEL_ID=amitca71/marabert2-levantine-toxic-model-v4 \\
    XLM_MODEL_ID=Andrazp/multilingual-hate-speech-robacofi \\
    python3 -m scripts.precompute_confidence

Populates content_examples.ai_confidence with MARBERT confidence (0-1).
Examples with existing ai_confidence are skipped (idempotent).
"""
import os
import sys

# Ensure app module is importable when running as __main__
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.content_example import ContentExample
from app.services.ml_models import ModelManager
from app.core.config import settings

BATCH_SIZE = 50


def main() -> None:
    db = SessionLocal()
    try:
        manager = ModelManager()
        print("Loading MARBERT model...")
        manager.load_models(settings.marbert_model_id, settings.xlm_model_id)
        print("Model loaded.")

        examples = (
            db.query(ContentExample)
            .filter(ContentExample.ai_confidence.is_(None))
            .all()
        )
        total = len(examples)
        print(f"Pre-computing confidence for {total} examples...")

        if total == 0:
            print("All examples already have confidence scores. Nothing to do.")
            return

        errors = 0
        for i, ex in enumerate(examples):
            try:
                result = manager.classify(ex.text, settings.code_mixed_threshold)
                ex.ai_confidence = result["confidence"]
            except Exception as e:
                errors += 1
                print(f"  [WARN] Example {ex.id} failed: {e}")

            # Commit in batches to reduce memory pressure
            if (i + 1) % BATCH_SIZE == 0:
                db.commit()
                print(f"  {i + 1}/{total} done ({errors} errors so far)")

        db.commit()
        print(f"Done. {total - errors}/{total} examples scored. {errors} errors.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
