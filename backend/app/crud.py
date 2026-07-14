from sqlalchemy.orm import Session
from typing import List
from backend.db import models

def get_locations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Location]:
    return db.query(models.Location).offset(skip).limit(limit).all()