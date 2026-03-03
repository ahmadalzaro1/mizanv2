from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/observatory", tags=["observatory"])

# Historical events in Jordan (2014-2022) -- for timeline markers
JORDANIAN_EVENTS = [
    {"year": 2014, "month": 6, "label_ar": "داعش يسيطر على الموصل", "label_en": "ISIS captures Mosul"},
    {"year": 2015, "month": 2, "label_ar": "حرق الطيار معاذ الكساسبة", "label_en": "Muath al-Kasasbeh killed by ISIS"},
    {"year": 2016, "month": 6, "label_ar": "هجوم مكتب المخابرات — البقعة", "label_en": "Baqaa intelligence office attack"},
    {"year": 2017, "month": 12, "label_ar": "اعتراف ترمب بالقدس عاصمة لإسرائيل", "label_en": "Trump Jerusalem recognition"},
    {"year": 2018, "month": 6, "label_ar": "إضراب المعلمين واحتجاجات اقتصادية", "label_en": "Teachers strike and economic protests"},
    {"year": 2019, "month": 10, "label_ar": "احتجاجات اتفاقية الغاز مع إسرائيل", "label_en": "Israel gas deal protests"},
    {"year": 2020, "month": 11, "label_ar": "الانتخابات البرلمانية الأردنية", "label_en": "Jordanian parliamentary elections"},
    {"year": 2021, "month": 4, "label_ar": "قضية الأمير حمزة / «الفتنة»", "label_en": "Prince Hamzah sedition case"},
]


@router.get("/trends")
def get_trends(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Return monthly hate speech counts from JHSC (2014-2022) with event markers."""
    # Use raw SQL to bypass SQLAlchemy enum mapping issue
    # (PG enum value 'very positive' has a space, Python enum name is 'very_positive')
    rows = db.execute(
        text("""
            SELECT tweet_year, tweet_month, label::text, COUNT(*)
            FROM jhsc_tweets
            WHERE tweet_year IS NOT NULL
            GROUP BY tweet_year, tweet_month, label
            ORDER BY tweet_year, tweet_month
        """)
    ).fetchall()

    # Aggregate into monthly buckets
    monthly_map: dict[tuple[int, int], dict] = {}
    for year, month, label, count in rows:
        key = (year, month)
        if key not in monthly_map:
            monthly_map[key] = {
                "year": year,
                "month": month,
                "hate_count": 0,
                "total_count": 0,
            }
        monthly_map[key]["total_count"] += count
        if label == "negative":
            monthly_map[key]["hate_count"] += count

    monthly = sorted(monthly_map.values(), key=lambda x: (x["year"], x["month"]))

    return {
        "monthly": monthly,
        "events": JORDANIAN_EVENTS,
    }
