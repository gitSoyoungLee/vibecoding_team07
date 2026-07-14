import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

DATA_DIR = Path("data")

def to_float(s: Optional[str]) -> Optional[float]:
    if s in (None, "", "null"):
        return None
    try:
        return float(s)
    except Exception:
        return None

def to_int(s: Optional[str]) -> Optional[int]:
    if s in (None, "", "null"):
        return None
    try:
        return int(s)
    except Exception:
        return None

def load_all_items(data_dir: Path = DATA_DIR) -> List[Dict[str, Any]]:
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

def build_locations_df(items: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for r in items:
        contentid = r.get("contentid")
        # id: 내부 PK로 numeric 가능하면 사용, 아니면 None (DB 자동생성)
        id_val = to_int(contentid) if contentid is not None and str(contentid).isdigit() else None

        row = {
            "id": id_val,
            "content_id": str(contentid) if contentid is not None else None,
            "content_type_id": to_int(r.get("contenttypeid")),
            "title": r.get("title") or None,
            "addr1": r.get("addr1") or None,
            "addr2": r.get("addr2") or None,
            "zipcode": r.get("zipcode") or None,
            "tel": r.get("tel") or None,
            "longitude": to_float(r.get("mapx")),
            "latitude": to_float(r.get("mapy")),
            "map_level": to_int(r.get("mlevel")),
            "area_code": r.get("areacode") or None,
            "sigungu_code": r.get("sigungucode") or None,
            "category1": r.get("cat1") or None,
            "category2": r.get("cat2") or None,
            "category3": r.get("cat3") or None,
            "image_url": r.get("firstimage") or None,
            "thumbnail_url": r.get("firstimage2") or None,
            "copyright_code": r.get("cpyrhtDivCd") or None,
            "created_time": r.get("createdtime") or None,
            "modified_time": r.get("modifiedtime") or None,
        }
        rows.append(row)

    cols = [
        "id","content_id","content_type_id","title","addr1","addr2","zipcode","tel",
        "longitude","latitude","map_level","area_code","sigungu_code",
        "category1","category2","category3",
        "image_url","thumbnail_url","copyright_code",
        "created_time","modified_time"
    ]
    df = pd.DataFrame(rows, columns=cols)
    return df

def insert_to_db(df: pd.DataFrame, engine):
    """
    DB 준비되면 사용하세요.
    예:
        from sqlalchemy import create_engine
        engine = create_engine("mysql+pymysql://user:pass@host/dbname?charset=utf8mb4")
        insert_to_db(df, engine)
    현재는 템플릿 (실행 전 관련 패키지 설치 필요: SQLAlchemy, 드라이버)
    """
    df_to_write = df.copy()
    # 만약 DB에서 id를 자동 생성하려면 id 컬럼 제거:
    # df_to_write = df_to_write.drop(columns=["id"])
    df_to_write.to_sql("locations", con=engine, if_exists="append", index=False)

if __name__ == "__main__":
    items = load_all_items()
    df = build_locations_df(items)

    print("총 레코드:", len(df))
    print(df.info())
    print(df.head(10))