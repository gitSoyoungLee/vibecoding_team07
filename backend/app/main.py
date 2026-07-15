"""FastAPI 진입점. 앱 생성, CORS 설정, 라우트(엔드포인트) 정의를 담당.
실행: cd backend && uvicorn app.main:app --reload
"""

from typing import List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.init_db import init_db
from app.db.session import get_db
from app.posts.router import router as posts_router

app = FastAPI(title="Locations API")

app.include_router(posts_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/locations", response_model=List[schemas.LocationOut])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_locations(db, skip=skip, limit=limit)


