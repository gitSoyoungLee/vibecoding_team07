"""장소(Location) DB 조회 함수 모음.
router.py가 이 함수들을 호출해 실제 쿼리를 실행한다.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db import models


def get_location_by_content_id(db: Session, content_id: str) -> Optional[models.Location]:
    return (
        db.query(models.Location)
        .filter(models.Location.content_id == content_id)
        .first()
    )


def _filtered_query(
    db: Session,
    content_type_ids: Optional[List[int]] = None,
    keyword: Optional[str] = None,
):
    query = db.query(models.Location).filter(
        models.Location.latitude.isnot(None),
        models.Location.longitude.isnot(None),
    )

    if content_type_ids:
        query = query.filter(models.Location.content_type_id.in_(content_type_ids))

    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            (models.Location.title.like(like_pattern))
            | (models.Location.addr1.like(like_pattern))
        )

    return query


def get_locations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    content_type_ids: Optional[List[int]] = None,
    keyword: Optional[str] = None,
) -> List[models.Location]:
    query = _filtered_query(db, content_type_ids=content_type_ids, keyword=keyword)
    return query.offset(skip).limit(limit).all()


def count_locations(
    db: Session,
    content_type_ids: Optional[List[int]] = None,
    keyword: Optional[str] = None,
) -> int:
    query = _filtered_query(db, content_type_ids=content_type_ids, keyword=keyword)
    return query.count()
