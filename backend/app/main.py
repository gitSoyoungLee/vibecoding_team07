"""FastAPI 진입점. 앱 생성, CORS 설정, 도메인별 라우터 등록을 담당.
실행: cd backend && uvicorn app.main:app --reload
각 도메인(locations, posts, chat 등)은 자기 폴더의 router.py를 만들고
여기서 app.include_router(...) 한 줄만 추가하면 된다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
## ai chat
from app import crud, schemas
from app.chat.router import router as chat_router
##
from app.db.init_db import init_db
from app.db.seed import seed
from app.db.session import get_db

# 도메인별 라우터 (각 도메인이 router.py를 갖고 있어야 함)
from app.posts.router import router as posts_router
from app.locations.router import router as locations_router
# chat 라우터가 있으면 주석 해제
# from app.chat.router import router as chat_router

app = FastAPI(title="LocalHub API")

# ai chat
app.include_router(chat_router)

# CORS 설정 (프론트 개발 주소 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 도메인 라우터 등록 (main.py는 라우터 include만 담당)
app.include_router(posts_router)
app.include_router(locations_router)
# app.include_router(chat_router)  # 필요시 추가

@app.on_event("startup")
def startup():  # 서버 시작 시
    init_db()   # DB 테이블 생성
    seed()      # 공공 데이터 등 초기 적재 (있으면)