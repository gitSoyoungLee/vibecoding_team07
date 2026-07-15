"""서버 시작 시 1회 실행되어 models.py에 정의된 테이블을 SQLite에 생성한다.
main.py의 startup 이벤트에서 호출됨.
"""

from app.db.session import engine
from app.db import models

def init_db():
    models.Base.metadata.create_all(bind=engine)
