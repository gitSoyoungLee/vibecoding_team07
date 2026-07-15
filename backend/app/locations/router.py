"""장소(Location) 관련 엔드포인트. main.py에서 include_router로 등록된다."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.locations import crud, schemas

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=schemas.LocationListOut)
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

    items = crud.get_locations(
        db,
        skip=skip,
        limit=limit,
        content_type_ids=content_type_ids,
        keyword=keyword,
    )
    total = crud.count_locations(
        db,
        content_type_ids=content_type_ids,
        keyword=keyword,
    )
    return schemas.LocationListOut(items=items, total=total)


@router.get("/{content_id}", response_model=schemas.LocationOut)
def read_location(content_id: str, db: Session = Depends(get_db)):
    location = crud.get_location_by_content_id(db, content_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location
