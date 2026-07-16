"""서버 시작 시 1회 실행되어 models.py에 정의된 테이블을 SQLite에 생성한다.
main.py의 startup 이벤트에서 호출됨.
"""

from sqlalchemy import inspect, text

from app.db.session import engine
from app.db import models

def init_db():
    models.Base.metadata.create_all(bind=engine)
    _add_missing_columns()


def _add_missing_columns():
    """create_all은 기존 테이블에 새 컬럼을 추가하지 않으므로, models.py에 추가된
    컬럼 중 실제 테이블에 없는 것을 ALTER TABLE로 보정한다."""
    inspector = inspect(engine)
    existing_columns = {col["name"] for col in inspector.get_columns("locations")}
    with engine.begin() as conn:
        for column in models.Location.__table__.columns:
            if column.name not in existing_columns:
                col_type = column.type.compile(engine.dialect)
                conn.execute(text(f"ALTER TABLE locations ADD COLUMN {column.name} {col_type}"))
