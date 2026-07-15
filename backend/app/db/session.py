"""DB 연결 설정. engine/SessionLocal 생성과 요청별 세션을 내려주는 get_db()를 제공.
DB 파일 경로를 바꾸려면 DATABASE_URL 환경변수를 설정하거나 기본값을 수정.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
