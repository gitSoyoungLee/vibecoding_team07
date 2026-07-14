





- - -
## DATA PARSING
* 패키지 설치:
python -m pip install -r requirements.txt
* 서버 실행:
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
* 테스트 요청:
curl "http://127.0.0.1:8000/locations?limit=5"


* 총 수집 건수 -> 8,150건으로 나오지만 실제 데이터는 음식점 1,632건 빠진 6,518건 입니다.