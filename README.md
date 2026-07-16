# ExploreSeoul (LocalHub)

서울을 여행하는 사람들이 관광 정보를 한곳에서 확인하고, 경험을 게시판으로 공유할 수 있는 지역 커뮤니티 서비스입니다.

- 배포 URL: [exploreseoul.netlify.app](https://exploreseoul.netlify.app/)

## 목차

1. [팀 구성 및 역할 분담](#팀-구성-및-역할-분담)
2. [기술 스택](#기술-스택)
3. [폴더 구조](#폴더-구조)
4. [로컬 실행 방법](#로컬-실행-방법)
5. [환경변수](#환경변수)
6. [주요 기능](#주요-기능)
7. [API 문서](#api-문서)
8. [데이터 출처 및 라이선스](#데이터-출처-및-라이선스)
9. [배포](#배포)

## 팀 구성 및 역할 분담

| 역할         | 담당자 | 주요 작업                                                                  |
| ------------ | ------ | -------------------------------------------------------------------------- |
| 장소 · 지도 | 이소영 | 장소 목록/상세 API, 카카오맵 지도 시각화, 축제 캘린더, 통합 검색, 홈페이지 |
| 게시판       | 한영서 | 게시판 CRUD, 댓글                                                          |
| AI 챗봇      | 문석표 | 챗봇 API 연동, 채팅 UI                                                     |

## 기술 스택

- **프론트엔드**: Vue.js 3 (Vite, SPA), Vue Router
- **백엔드**: FastAPI, SQLAlchemy, SQLite
- **지도**: Kakao Maps JavaScript SDK
- **AI**: OpenAI API
- **데이터**: 한국관광공사 TourAPI 4.0 (서울 권역)
- **배포**: Netlify(프론트) / Render(백엔드)

## 폴더 구조

```
backend/
  app/
    main.py          FastAPI 진입점, 도메인별 라우터 등록
    db/               DB 연결 설정(session.py), 테이블 정의(models.py), 초기화/시딩
    locations/        장소 도메인 (crud/schemas/router)
    posts/            게시판 도메인 (crud/schemas/router)
    chat/             AI 챗봇 도메인 (crud/schemas/router)
  requirements.txt
frontend/
  src/
    views/            공용 페이지 (HomeView 등)
    features/         도메인별 화면 (locations, posts, chat, festivals, search)
    router/           라우트 정의
    App.vue           공통 레이아웃(헤더, 챗봇 위젯) + RouterView
data/                 TourAPI 원본 JSON, 스키마/출처 문서
```

각 도메인은 자기 폴더 안에서만 작업하고, `main.py`/`router/index.js`에는 라우터를 등록하는 한 줄만 추가하는 컨벤션을 따릅니다.

## 로컬 실행 방법

### 백엔드

```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
```

`http://localhost:8000` 에서 실행됩니다. 서버 시작 시 `app.db`가 자동 생성되고, `data/*.json`의 관광지 데이터가 자동으로 적재됩니다 (재실행해도 중복 삽입되지 않습니다).

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:5173` 에서 실행됩니다.

두 서버 모두 실행 중이어야 프론트에서 실제 데이터를 볼 수 있습니다.

## 환경변수

`.env` 파일은 git에 포함되지 않으므로, 아래 값을 각자 채워서 로컬에 만들어야 합니다. 각 프로젝트의 `.env.example`을 참고하세요.

### `backend/.env`

| 변수               | 필수    | 설명                                                      |
| ------------------ | ------- | --------------------------------------------------------- |
| `OPENAI_API_KEY` | 필수    | 챗봇 기능용 OpenAI API 키                                 |
| `OPENAI_MODEL`   | 선택    | 사용할 모델 (기본값 있음)                                 |
| `TOUR_API_KEY`   | 선택    | 축제 날짜 백필 스크립트(`backfill_festival_dates.py`)용 |
| `DATABASE_URL`   | 선택    | 기본값`sqlite:///./app.db`                              |
| `CORS_ORIGINS`   | 배포 시 | 프론트 배포 도메인 (콤마로 여러 개 가능)                  |

### `frontend/.env`

| 변수                   | 필수 | 설명                                         |
| ---------------------- | ---- | -------------------------------------------- |
| `VITE_KAKAO_MAP_KEY` | 필수 | Kakao Maps JavaScript 키                     |
| `VITE_API_BASE_URL`  | 필수 | 백엔드 주소 (로컬:`http://127.0.0.1:8000`) |

## 주요 기능

- **홈**: 검색창, 카테고리 바로가기, 게시판 미리보기
- **장소 목록/지도 탐색**: 카테고리·키워드 필터, 카드 갤러리, 카카오맵 기반 지도 탐색
- **장소 상세**: 이미지, 주소, 전화번호, 카카오맵 위치 표시 (모달)
- **게시판**: 카테고리별 CRUD, 댓글, 비밀번호 기반 수정/삭제
- **AI 챗봇**: 여행 관련 질의응답 플로팅 위젯
- **축제 캘린더**: 월별 캘린더에서 진행 중인 축제 확인
- **통합 검색**: 장소 + 게시글 동시 검색

## API 문서

백엔드 실행 후 `http://localhost:8000/docs` 에서 Swagger UI로 전체 API 명세를 확인할 수 있습니다.

## 데이터 출처 및 라이선스

- 제공기관: 한국관광공사 (Tour API 4.0), 공공데이터포털
- 라이선스: 공공누리 제3유형 (출처 표시, 변경 금지, 상업적 이용/재배포 허용)
- 상세: [`data/SOURCE.md`](data/SOURCE.md), 필드 정의: [`data/SCHEMA.md`](data/SCHEMA.md)

> 이 서비스는 한국관광공사 Tour API(TourAPI 4.0)의 데이터를 활용하였습니다.
> 출처: 한국관광공사 (https://www.data.go.kr/data/15101578/openapi.do), 라이선스: 공공누리 제3유형

## 배포

- 프론트엔드(Netlify): [exploreseoul.netlify.app](https://exploreseoul.netlify.app/)
