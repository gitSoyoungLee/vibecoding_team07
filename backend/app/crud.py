"""DB 조회/조작 함수 모음 (Create/Read/Update/Delete).
라우트 함수(main.py)가 이 함수들을 호출해 실제 쿼리를 실행한다.
"""

from sqlalchemy.orm import Session
from typing import List
from app.db import models

def get_locations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Location]:
    return db.query(models.Location).offset(skip).limit(limit).all()