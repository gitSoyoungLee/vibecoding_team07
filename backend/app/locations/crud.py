"""장소(Location) DB 조회 함수 모음.
router.py가 이 함수들을 호출해 실제 쿼리를 실행한다.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db import models


def get_locations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    content_type_ids: Optional[List[int]] = None,
    keyword: Optional[str] = None,
) -> List[models.Location]:
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

    return query.offset(skip).limit(limit).all()
