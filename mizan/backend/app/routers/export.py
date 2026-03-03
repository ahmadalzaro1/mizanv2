import csv
import io
import json
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import require_admin
from app.models.content_example import ContentExample
from app.models.user import User

router = APIRouter(prefix="/api/export", tags=["export"])

EXPORT_COLUMNS = [
    "example_id", "text", "source_dataset", "dialect",
    "ground_truth_label", "hate_type",
]


@router.get("")
def export_content_examples(
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    examples = db.query(ContentExample).all()

    rows = []
    for ex in examples:
        rows.append({
            "example_id": str(ex.id),
            "text": ex.text,
            "source_dataset": ex.source_dataset,
            "dialect": ex.dialect,
            "ground_truth_label": ex.ground_truth_label.value if ex.ground_truth_label else None,
            "hate_type": ex.hate_type.value if ex.hate_type else None,
        })

    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=content_examples.csv"},
        )
    else:
        content = json.dumps(rows, ensure_ascii=False, indent=2)
        return StreamingResponse(
            iter([content]),
            media_type="application/json; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=content_examples.json"},
        )
