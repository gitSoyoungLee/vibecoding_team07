# vibecoding_team07

FastAPI + SQLite + Vue.js 기반 프로젝트

## 프로젝트 구조

```
backend/   FastAPI + SQLite
frontend/  Vue.js (Vite)
data/      원본 데이터 (서울시 공공데이터)
```

## 백엔드 실행

```bash
cd backend
python -m venv venv
# Windows
source venv/Scripts/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

서버는 `http://localhost:8000` 에서 실행됩니다. (`app.db`는 서버 시작 시 자동으로 생성되며 git에는 포함되지 않습니다.)

## 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

프론트엔드는 `http://localhost:5173` 에서 실행됩니다.

## 브랜치 전략

- `master`: 배포 가능한 안정 버전
- 기능 작업은 `feature/기능명` 브랜치를 만들어 진행 후 PR로 병합합니다.

---

## DATA PARSING

* 패키지 설치 (repo 루트에서, pandas 등 파싱용 의존성):
  python -m pip install -r requirements.txt
* 파싱 스크립트 실행 예시:
  python gps_data_parsing.py

## API 동작 확인

`cd backend && uvicorn app.main:app --reload` 로 서버를 띄운 뒤:

curl "http://127.0.0.1:8000/locations?limit=5"

* 총 수집 건수 -> 8,150건으로 나오지만 실제 데이터는 음식점 1,632건 빠진 6,518건 입니다.
