import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.content_example import ContentExample, ContentLabel, HateType
from app.models.bias_audit import BiasAuditRun

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/audit", tags=["audit"])

MAX_FP_SAMPLES = 10

# Arabic labels for hate categories
CATEGORY_LABELS_AR = {
    "race": "عنصرية",
    "religion": "ديني",
    "ideology": "أيديولوجي",
    "gender": "جنساني",
    "disability": "إعاقة",
    "social_class": "طبقي",
    "tribalism": "عشائري",
    "refugee_related": "لاجئين",
    "political_affiliation": "سياسي",
    "unknown": "غير مصنف",
}


def _compute_metrics(tp: int, fp: int, fn: int) -> dict:
    """Compute precision, recall, F1 from confusion counts."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def _build_results_from_stats(
    overall_tp: int,
    overall_fp: int,
    overall_fn: int,
    overall_tn: int,
    total: int,
    category_stats: dict,
    category_confidences: dict,
    source_stats: dict,
    overall_confidences: list,
    false_positive_samples: list,
) -> dict:
    """Build the enriched results dict from accumulated loop statistics.

    Both run_audit() and run_audit_stream() call this after their inference loops
    to avoid duplicating the post-loop construction logic.
    """
    # Per-category results (with confidence_scores)
    per_category = []
    for cat_value in HateType:
        cat = cat_value.value
        stats = category_stats.get(cat, {"tp": 0, "fp": 0, "fn": 0, "total": 0})
        metrics = _compute_metrics(stats["tp"], stats.get("fp", 0), stats["fn"])
        per_category.append({
            "category": cat,
            "category_ar": CATEGORY_LABELS_AR.get(cat, cat),
            "sample_count": stats["total"],
            "tp": stats["tp"],
            "fp": stats.get("fp", 0),
            "fn": stats["fn"],
            **metrics,
            "confidence_scores": [round(s, 4) for s in category_confidences.get(cat, [])],
        })

    # Sort by F1 ascending (weakest first)
    per_category.sort(key=lambda x: x["f1"])

    # Per-source breakdown
    per_source = []
    for src, stats in source_stats.items():
        metrics = _compute_metrics(stats["tp"], stats["fp"], stats["fn"])
        fpr = stats["fp"] / (stats["fp"] + stats["tn"]) if (stats["fp"] + stats["tn"]) > 0 else 0.0
        per_source.append({
            "source": src,
            "total": stats["total"],
            **metrics,
            "false_positive_rate": round(fpr, 4),
        })
    # Sort by F1 ascending (weakest first)
    per_source.sort(key=lambda x: x["f1"])

    # Confidence distributions per category
    confidence_dist: dict = {}
    for cat_value in HateType:
        cat = cat_value.value
        scores = category_confidences.get(cat, [])
        confidence_dist[cat] = {
            "scores": [round(s, 4) for s in scores],
            "count": len(scores),
        }
    confidence_dist["_overall"] = {
        "scores": [round(s, 4) for s in overall_confidences],
        "count": len(overall_confidences),
    }

    overall_metrics = _compute_metrics(overall_tp, overall_fp, overall_fn)

    return {
        "overall": {
            **overall_metrics,
            "total": total,
            "tp": overall_tp,
            "fp": overall_fp,
            "fn": overall_fn,
            "tn": overall_tn,
        },
        "per_category": per_category,
        "per_source": per_source,
        "confidence_dist": confidence_dist,
        "false_positives": false_positive_samples,
    }


@router.post("/run")
def run_audit(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Run MARBERT inference on all content_examples and compute per-category metrics."""
    from app.main import model_manager
    from app.core.config import settings

    if model_manager is None or not model_manager.is_loaded:
        raise HTTPException(status_code=503, detail="النموذج غير جاهز بعد")

    examples = db.query(ContentExample).all()
    if not examples:
        raise HTTPException(status_code=404, detail="لا توجد أمثلة في قاعدة البيانات")

    start_time = time.perf_counter()

    # Tracking structures — all updated in a single pass
    category_stats: dict[str, dict] = {}
    source_stats: dict[str, dict] = {}
    category_confidences: dict[str, list] = {}
    overall_confidences: list[float] = []
    false_positive_samples: list[dict] = []
    overall_tp = 0
    overall_fp = 0
    overall_fn = 0
    overall_tn = 0

    for ex in examples:
        # Ground truth binary mapping (same as training router)
        gt = ex.ground_truth_label.value
        if gt in ("hate", "offensive"):
            gt_binary = "hate"
        else:
            gt_binary = "not_hate"

        # Run MARBERT classification
        result = model_manager.classify(
            ex.text, code_mixed_threshold=settings.code_mixed_threshold
        )
        predicted = result["label"]
        confidence = result["confidence"]

        # --- Overall confusion ---
        if gt_binary == "hate" and predicted == "hate":
            overall_tp += 1
        elif gt_binary == "not_hate" and predicted == "hate":
            overall_fp += 1
        elif gt_binary == "hate" and predicted == "not_hate":
            overall_fn += 1
        else:
            overall_tn += 1

        # --- Per-category confusion (only for hate examples with a category) ---
        if gt_binary == "hate" and ex.hate_type is not None:
            cat = ex.hate_type.value
            if cat not in category_stats:
                category_stats[cat] = {"tp": 0, "fp": 0, "fn": 0, "total": 0}
            category_stats[cat]["total"] += 1
            if predicted == "hate":
                category_stats[cat]["tp"] += 1
            else:
                category_stats[cat]["fn"] += 1
            # Confidence tracking per category
            if cat not in category_confidences:
                category_confidences[cat] = []
            category_confidences[cat].append(confidence)

        # --- Per-source breakdown ---
        src = ex.source_dataset
        if src not in source_stats:
            source_stats[src] = {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "total": 0}
        source_stats[src]["total"] += 1
        if gt_binary == "hate" and predicted == "hate":
            source_stats[src]["tp"] += 1
        elif gt_binary == "not_hate" and predicted == "hate":
            source_stats[src]["fp"] += 1
        elif gt_binary == "hate" and predicted == "not_hate":
            source_stats[src]["fn"] += 1
        else:
            source_stats[src]["tn"] += 1

        # --- Overall confidence tracking ---
        overall_confidences.append(confidence)

        # --- False positive samples (cap at MAX_FP_SAMPLES) ---
        if gt_binary == "not_hate" and predicted == "hate":
            if len(false_positive_samples) < MAX_FP_SAMPLES:
                false_positive_samples.append({
                    "text": ex.text[:200],
                    "source_dataset": ex.source_dataset,
                    "confidence": round(confidence, 4),
                    "ground_truth": gt,
                })

    duration_ms = round((time.perf_counter() - start_time) * 1000)

    results = _build_results_from_stats(
        overall_tp=overall_tp,
        overall_fp=overall_fp,
        overall_fn=overall_fn,
        overall_tn=overall_tn,
        total=len(examples),
        category_stats=category_stats,
        category_confidences=category_confidences,
        source_stats=source_stats,
        overall_confidences=overall_confidences,
        false_positive_samples=false_positive_samples,
    )

    # Cache the run
    run = BiasAuditRun(
        id=uuid.uuid4(),
        computed_at=datetime.utcnow(),
        total_examples=len(examples),
        duration_ms=duration_ms,
        results=results,
    )
    db.add(run)
    db.commit()

    return {
        "id": str(run.id),
        "computed_at": run.computed_at,
        "total_examples": run.total_examples,
        "duration_ms": run.duration_ms,
        "results": results,
    }


@router.post("/run/stream")
async def run_audit_stream(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Stream MARBERT inference progress via SSE as each example is classified.

    Returns text/event-stream with per-example progress events and a final
    done event containing the complete enriched results.
    """
    from app.main import model_manager
    from app.core.config import settings

    if model_manager is None or not model_manager.is_loaded:
        raise HTTPException(status_code=503, detail="النموذج غير جاهز بعد")

    examples = db.query(ContentExample).all()
    if not examples:
        raise HTTPException(status_code=404, detail="لا توجد أمثلة في قاعدة البيانات")

    total = len(examples)

    async def event_generator():
        # Tracking structures — all updated in a single pass
        category_stats: dict[str, dict] = {}
        source_stats: dict[str, dict] = {}
        category_confidences: dict[str, list] = {}
        overall_confidences: list[float] = []
        false_positive_samples: list[dict] = []
        overall_tp = 0
        overall_fp = 0
        overall_fn = 0
        overall_tn = 0

        start_time = time.perf_counter()

        try:
            loop = asyncio.get_event_loop()

            for i, ex in enumerate(examples):
                # Ground truth binary mapping
                gt = ex.ground_truth_label.value
                if gt in ("hate", "offensive"):
                    gt_binary = "hate"
                else:
                    gt_binary = "not_hate"

                # classify() is synchronous — run in executor to avoid blocking
                result = await loop.run_in_executor(
                    None,
                    lambda text=ex.text: model_manager.classify(
                        text, code_mixed_threshold=settings.code_mixed_threshold
                    ),
                )
                predicted = result["label"]
                confidence = result["confidence"]

                # --- Overall confusion ---
                if gt_binary == "hate" and predicted == "hate":
                    overall_tp += 1
                elif gt_binary == "not_hate" and predicted == "hate":
                    overall_fp += 1
                elif gt_binary == "hate" and predicted == "not_hate":
                    overall_fn += 1
                else:
                    overall_tn += 1

                # --- Per-category confusion ---
                if gt_binary == "hate" and ex.hate_type is not None:
                    cat = ex.hate_type.value
                    if cat not in category_stats:
                        category_stats[cat] = {"tp": 0, "fp": 0, "fn": 0, "total": 0}
                    category_stats[cat]["total"] += 1
                    if predicted == "hate":
                        category_stats[cat]["tp"] += 1
                    else:
                        category_stats[cat]["fn"] += 1
                    if cat not in category_confidences:
                        category_confidences[cat] = []
                    category_confidences[cat].append(confidence)

                # --- Per-source breakdown ---
                src = ex.source_dataset
                if src not in source_stats:
                    source_stats[src] = {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "total": 0}
                source_stats[src]["total"] += 1
                if gt_binary == "hate" and predicted == "hate":
                    source_stats[src]["tp"] += 1
                elif gt_binary == "not_hate" and predicted == "hate":
                    source_stats[src]["fp"] += 1
                elif gt_binary == "hate" and predicted == "not_hate":
                    source_stats[src]["fn"] += 1
                else:
                    source_stats[src]["tn"] += 1

                # --- Overall confidence tracking ---
                overall_confidences.append(confidence)

                # --- False positive samples ---
                if gt_binary == "not_hate" and predicted == "hate":
                    if len(false_positive_samples) < MAX_FP_SAMPLES:
                        false_positive_samples.append({
                            "text": ex.text[:200],
                            "source_dataset": ex.source_dataset,
                            "confidence": round(confidence, 4),
                            "ground_truth": gt,
                        })

                # Yield SSE progress event for every example
                yield f"data: {json.dumps({'progress': round((i + 1) / total * 100), 'current': i + 1, 'total': total})}\n\n"

            duration_ms = round((time.perf_counter() - start_time) * 1000)

            results = _build_results_from_stats(
                overall_tp=overall_tp,
                overall_fp=overall_fp,
                overall_fn=overall_fn,
                overall_tn=overall_tn,
                total=total,
                category_stats=category_stats,
                category_confidences=category_confidences,
                source_stats=source_stats,
                overall_confidences=overall_confidences,
                false_positive_samples=false_positive_samples,
            )

            # Cache the run
            run = BiasAuditRun(
                id=uuid.uuid4(),
                computed_at=datetime.utcnow(),
                total_examples=total,
                duration_ms=duration_ms,
                results=results,
            )
            db.add(run)
            db.commit()

            # Final SSE event with complete enriched results
            yield f"data: {json.dumps({'done': True, 'id': str(run.id), 'computed_at': run.computed_at.isoformat(), 'total_examples': run.total_examples, 'duration_ms': run.duration_ms, 'results': results})}\n\n"

        except Exception as e:
            logger.exception("SSE audit stream error")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/results")
def get_results(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Return the latest cached audit run."""
    run = (
        db.query(BiasAuditRun)
        .order_by(BiasAuditRun.computed_at.desc())
        .first()
    )
    if not run:
        raise HTTPException(
            status_code=404,
            detail="لم يتم تشغيل التدقيق بعد. استخدم POST /api/audit/run أولاً",
        )

    return {
        "id": str(run.id),
        "computed_at": run.computed_at,
        "total_examples": run.total_examples,
        "duration_ms": run.duration_ms,
        "results": run.results,
    }


@router.get("/results/csv")
def download_csv(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Download the latest audit results as CSV."""
    run = (
        db.query(BiasAuditRun)
        .order_by(BiasAuditRun.computed_at.desc())
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="لم يتم تشغيل التدقيق بعد")

    import io
    import csv

    output = io.StringIO()
    # Add UTF-8 BOM for Excel Arabic compatibility
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow(["category", "category_ar", "sample_count", "precision", "recall", "f1", "tp", "fp", "fn"])

    for cat in run.results["per_category"]:
        writer.writerow([
            cat["category"],
            cat["category_ar"],
            cat["sample_count"],
            cat["precision"],
            cat["recall"],
            cat["f1"],
            cat["tp"],
            cat["fp"],
            cat["fn"],
        ])

    # Overall row
    o = run.results["overall"]
    writer.writerow(["overall", "إجمالي", o["total"], o["precision"], o["recall"], o["f1"], o["tp"], o["fp"], o["fn"]])

    csv_bytes = output.getvalue().encode("utf-8")

    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=mizan-bias-audit.csv"},
    )
