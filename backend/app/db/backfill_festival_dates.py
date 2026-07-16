"""축제공연행사(content_type_id=15)의 실제 시작일/종료일을 TourAPI detailIntro2로 채워 넣는
1회성 백필 스크립트. 원본 areaBasedList 수집 데이터에는 날짜 필드가 없어서 별도로 보강한다.

실행: cd backend && python -m app.db.backfill_festival_dates

.env에 TOUR_API_KEY(공공데이터포털 일반 인증키, Decoding 값)가 있어야 한다.
재실행해도 안전 — 매번 최신 날짜로 덮어쓴다.
"""

import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.db.models import Location
from app.db.session import SessionLocal

API_BASE = "https://apis.data.go.kr/B551011/KorService2/detailIntro2"
FESTIVAL_CONTENT_TYPE_ID = 15
REQUEST_DELAY_SEC = 0.15

# data.go.kr 응답 서버 인증서가 사내망 TLS 검사 프록시를 거치면서 검증에 실패하는
# 로컬 개발 환경이 있어, 이 1회성 스크립트에 한해 인증서 검증을 끈다.
_SSL_CONTEXT = ssl.create_default_context()
_SSL_CONTEXT.check_hostname = False
_SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def fetch_event_dates(service_key: str, content_id: str) -> tuple[str | None, str | None]:
    params = {
        "serviceKey": service_key,
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "_type": "json",
        "contentId": content_id,
        "contentTypeId": FESTIVAL_CONTENT_TYPE_ID,
    }
    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=15, context=_SSL_CONTEXT) as res:
        body = json.loads(res.read().decode("utf-8"))

    header = body.get("response", {}).get("header", {})
    if header.get("resultCode") != "0000":
        raise RuntimeError(f"API error: {header.get('resultMsg')}")

    items = body.get("response", {}).get("body", {}).get("items", "")
    if not items:
        return None, None
    item = items["item"][0]
    return item.get("eventstartdate") or None, item.get("eventenddate") or None


def backfill():
    service_key = os.environ.get("TOUR_API_KEY")
    if not service_key:
        raise SystemExit("TOUR_API_KEY가 .env에 설정되어 있지 않습니다.")

    db = SessionLocal()
    try:
        festivals = (
            db.query(Location)
            .filter(Location.content_type_id == FESTIVAL_CONTENT_TYPE_ID)
            .all()
        )
        print(f"대상 {len(festivals)}건")

        updated, skipped, failed = 0, 0, 0
        for i, loc in enumerate(festivals, start=1):
            if not loc.content_id:
                skipped += 1
                continue
            try:
                start, end = fetch_event_dates(service_key, loc.content_id)
            except Exception as e:
                failed += 1
                print(f"[{i}/{len(festivals)}] {loc.title} - 실패: {e}")
                time.sleep(REQUEST_DELAY_SEC)
                continue

            if start or end:
                loc.event_start_date = start
                loc.event_end_date = end
                updated += 1
            else:
                skipped += 1

            if i % 20 == 0:
                db.commit()
                print(f"[{i}/{len(festivals)}] 진행 중... (갱신 {updated}, 스킵 {skipped}, 실패 {failed})")

            time.sleep(REQUEST_DELAY_SEC)

        db.commit()
        print(f"완료: 갱신 {updated}건 / 날짜 없음 {skipped}건 / 실패 {failed}건")
    finally:
        db.close()


if __name__ == "__main__":
    backfill()
