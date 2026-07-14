# data_parsing_to_pandas.py
import subprocess
import sys
import importlib

packages = {
    "pandas": "pandas"
}

for module, package in packages.items():
    try:
        importlib.import_module(module)
    except ImportError:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            package
        ])

import json
from pathlib import Path
from datetime import datetime
import pandas as pd

DATA_DIR = Path("data")

def parse_time(ts):
    if not ts:
        return None
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d"):
        try:
            return datetime.strptime(ts, fmt)
        except Exception:
            continue
    return None

def load_items_from_jsons(data_dir=DATA_DIR):
    items = []
    for p in sorted(data_dir.glob("*.json")):
        try:
            with p.open(encoding="utf-8") as f:
                doc = json.load(f)
            doc_items = doc.get("items") or []
            items.extend(doc_items)
        except Exception as e:
            print(f"skip {p}: {e}")
    return items

def build_posts_dataframe(items):
    rows = []
    for r in items:
        contentid = r.get("contentid")
        try:
            id_val = int(contentid) if contentid not in (None, "") else None
        except:
            id_val = None

        # 조합된 본문: 주소, 전화, 이미지, 분류 정보 등
        parts = []
        if r.get("addr1"):
            parts.append(f"주소: {r.get('addr1')}")
        if r.get("addr2"):
            parts.append(r.get("addr2"))
        if r.get("tel"):
            parts.append(f"전화: {r.get('tel')}")
        if r.get("firstimage"):
            parts.append(f"이미지: {r.get('firstimage')}")
        if r.get("lclsSystm1") or r.get("lclsSystm2") or r.get("lclsSystm3"):
            parts.append("분류: " + "/".join(filter(None, [r.get("lclsSystm1"), r.get("lclsSystm2"), r.get("lclsSystm3")])))
        content_text = "\n".join(parts) if parts else (r.get("overview") or r.get("intro") or "")

        row = {
            "id": id_val,
            "category_id": int(r.get("contenttypeid")) if r.get("contenttypeid") else None,
            "nickname": "importer",
            "title": r.get("title") or "",
            "content": content_text or "",
            "password": "changeme",
            "views": 0,
            "created_at": parse_time(r.get("createdtime")),
            "updated_at": parse_time(r.get("modifiedtime")),
            "comment_count": 0,
        }
        rows.append(row)

    df = pd.DataFrame(rows, columns=[
        "id","category_id","nickname","title","content","password",
        "views","created_at","updated_at","comment_count"
    ])
    # id가 PK로 비어있으면 DB에서 자동생성 가능하도록 None 유지
    return df

def insert_to_db(df, engine):
    """
    DB가 준비되면 사용할 함수 템플릿.
    - engine: SQLAlchemy engine 또는 DBAPI 연결
    예시:
        from sqlalchemy import create_engine
        engine = create_engine("mysql+pymysql://user:pass@host/dbname?charset=utf8mb4")
        insert_to_db(df, engine)
    """
    df_to_write = df.copy()
    # SQL용으로 날짜 컬럼을 문자열/타입 맞춤 필요 시 변환
    # df_to_write['created_at'] = df_to_write['created_at'].astype('datetime64[ns]')
    df_to_write.to_sql("posts", con=engine, if_exists="append", index=False)

# if __name__ == "post_data_parsing":
if __name__ == "__main__":
    items = load_items_from_jsons()
    df = build_posts_dataframe(items)

    # 결과 확인
    print("총 레코드:", len(df))
    print(df.info())
    print(df.head(10))

    # DB 준비되면 아래 예시처럼 사용:
    # from sqlalchemy import create_engine
    # engine = create_engine("sqlite:///mydb.sqlite3")  # 예시
    # insert_to_db(df, engine)