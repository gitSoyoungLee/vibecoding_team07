"""장소(Location) 관련 엔드포인트. main.py에서 include_router로 등록된다."""

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.locations import crud, schemas

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=List[schemas.LocationOut])
def read_locations(
    skip: int = 0,
    limit: int = 100,
    content_type_id: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    content_type_ids = None
    if content_type_id:
        content_type_ids = [int(v) for v in content_type_id.split(",") if v.strip()]

    return crud.get_locations(
        db,
        skip=skip,
        limit=limit,
        content_type_ids=content_type_ids,
        keyword=keyword,
    )
