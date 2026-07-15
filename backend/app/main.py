"""FastAPI 진입점. 앱 생성, CORS 설정, 도메인별 라우터 등록을 담당.
실행: cd backend && uvicorn app.main:app --reload
각 도메인(locations, posts, chat 등)은 자기 폴더의 router.py를 만들고
여기서 app.include_router(...) 한 줄만 추가하면 된다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db
from app.db.seed import seed
from app.locations.router import router as locations_router

app = FastAPI(title="LocalHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations_router)


@app.on_event("startup")
def startup():  # 서버 시작 시
    init_db()   # DB 테이블 생성
    seed()      # 공공 데이터 - 장소 데이터 적재
