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
