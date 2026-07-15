"""repo 루트의 data/*.json(TourAPI 원본)을 gps_data_parsing.py로 파싱해
locations 테이블에 적재하는 1회성 스크립트.
실행: cd backend && python -m app.db.seed
재실행해도 이미 있는 content_id는 건너뛰므로 안전하게 다시 돌릴 수 있다.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import gps_data_parsing as parsing  # repo 루트 모듈

from app.db.init_db import init_db
from app.db.models import Location
from app.db.session import SessionLocal


def seed():
    init_db()
    items = parsing.load_all_items(data_dir=REPO_ROOT / "data")
    df = parsing.build_locations_df(items)

    db = SessionLocal()
    try:
        existing_ids = {row[0] for row in db.query(Location.content_id).all()}
        inserted = 0
        for row in df.to_dict(orient="records"):
            content_id = row["content_id"]
            if content_id is None or content_id in existing_ids:
                continue
            row.pop("id", None)  # PK는 자동 생성에 맡김
            db.add(Location(**row))
            existing_ids.add(content_id)
            inserted += 1
        db.commit()
        print(f"파싱 {len(df)}건 중 신규 {inserted}건 삽입, 기존 {len(df) - inserted}건 스킵")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
