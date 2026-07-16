import os
import re
from pathlib import Path
from typing import Optional

import openai
from dotenv import load_dotenv
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db import models


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _get_api_key() -> str | None:
    return (os.getenv("OPENAI_API_KEY") or "").strip() or None


def _get_model_candidates() -> list[str]:
    configured = (os.getenv("OPENAI_MODEL") or "").strip()
    if configured:
        return [configured]
    return ["gpt-5-mini", "gpt-4o-mini"]


def _search_posts(db: Optional[Session], keyword: str):
    if db is None:
        return []

    like = f"%{keyword.strip()}%"
    return (
        db.query(models.Post)
        .filter(
            or_(
                models.Post.title.ilike(like),
                models.Post.content.ilike(like),
                models.Post.nickname.ilike(like),
            )
        )
        .order_by(models.Post.created_at.desc())
        .limit(3)
        .all()
    )


def _search_locations(db: Optional[Session], keyword: str):
    if db is None:
        return []

    like = f"%{keyword.strip()}%"
    return (
        db.query(models.Location)
        .filter(
            or_(
                models.Location.title.ilike(like),
                models.Location.addr1.ilike(like),
                models.Location.addr2.ilike(like),
            )
        )
        .limit(3)
        .all()
    )


def _extract_keyword(message: str) -> str:
    cleaned = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", message).strip()
    tokens = [token for token in cleaned.split() if len(token) > 1]
    if not tokens:
        return ""

    for token in tokens:
        if token in {"추천", "가볼만한", "관광지", "명소", "여행지"}:
            continue
        return token
    return tokens[0]


def _is_course_request(message: str) -> bool:
    lowered = message.lower()
    course_markers = ["코스", "루트", "일정", "오전", "오후", "시간", "근처", "친구", "데이트", "혼자", "놀고", "놀러", "가고", "가볼"]
    return any(marker in lowered for marker in course_markers)


def _extract_location(message: str) -> str:
    lowered = message.lower()
    location_candidates = [
        "홍대",
        "강남",
        "이태원",
        "명동",
        "성수",
        "연남",
        "잠실",
        "한강",
        "광화문",
        "경복궁",
        "인사동",
        "여의도",
        "압구정",
        "신촌",
        "건대",
    ]

    for candidate in location_candidates:
        if candidate in lowered:
            return candidate

    if "근처" in lowered or "에서" in lowered:
        return "서울"
    return "서울"


def _extract_start_hour(message: str) -> int:
    lowered = message.lower()
    if "오후" in lowered:
        if "12시" in lowered or "12" in lowered:
            return 12
        if "1시" in lowered or "1" in lowered:
            return 13
        if "2시" in lowered or "2" in lowered:
            return 14
        if "3시" in lowered or "3" in lowered:
            return 15
        if "4시" in lowered or "4" in lowered:
            return 16
        if "5시" in lowered or "5" in lowered:
            return 17
        if "6시" in lowered or "6" in lowered:
            return 18
    if "오전" in lowered:
        if "10시" in lowered or "10" in lowered:
            return 10
        if "11시" in lowered or "11" in lowered:
            return 11
    for pattern in [r"(\d{1,2})시"]:
        match = re.search(pattern, message)
        if match:
            hour = int(match.group(1))
            return hour if 0 <= hour <= 23 else 14
    return 14


def _build_course_reply(message: str) -> str:
    lowered = message.lower()
    location = _extract_location(message)
    start_hour = _extract_start_hour(message)
    vibe = "친구와 즐기기 좋은" if "친구" in lowered else "데이트하기 좋은" if "데이트" in lowered else "여유로운"

    steps = [
        {
            "time": start_hour,
            "title": f"{location} 감성 카페",
            "description": "사진과 대화가 잘 어울리는 분위기 있는 곳에서 시작해요.",
        },
        {
            "time": start_hour + 2,
            "title": f"{location} 산책 스팟",
            "description": "둘러보기 좋은 거리나 공원을 천천히 즐겨요.",
        },
        {
            "time": start_hour + 4,
            "title": f"{location} 맛집 거리",
            "description": "저녁 식사나 디저트로 마무리하면 만족도가 높아요.",
        },
    ]

    lines = [f"🎵 {location} {vibe} 코스 추천", ""]
    for step in steps:
        lines.append(f"{step['time']:02d}:00 {step['title']}")
        lines.append(f"- {step['description']}")
    lines.append("")
    lines.append("원하면 인원, 예산, 비 오는 날 여부까지 반영해서 더 세밀하게 바꿔드릴게요.")
    return "\n".join(lines)


def _format_post_results(posts) -> str:
    if not posts:
        return "관련 커뮤니티 게시글이 아직 없어요."

    lines = [f"커뮤니티 게시글 검색 결과 {len(posts)}건:"]
    for post in posts:
        title = getattr(post, "title", "") or "제목 없음"
        content = getattr(post, "content", "") or ""
        snippet = re.sub(r"\s+", " ", content)[:80]
        lines.append(f"- {title}: {snippet}")
    return "\n".join(lines)


def _format_location_results(locations) -> str:
    if not locations:
        return "관련된 장소 정보를 찾지 못했습니다. 다른 키워드로 다시 물어봐 주세요."

    lines = [f"관련 장소 추천 {len(locations)}건:"]
    for location in locations:
        title = getattr(location, "title", "") or "장소"
        addr = getattr(location, "addr1", "") or ""
        lines.append(f"- {title} / {addr}")
    return "\n".join(lines)


def get_chat_reply(message: str, db: Optional[Session] = None) -> str:
    if not message or not message.strip():
        return "질문을 입력해 주세요."

    text = message.strip()
    lowered = text.lower()

    if _is_course_request(text):
        return _build_course_reply(text)

    if any(keyword in lowered for keyword in ["게시글", "커뮤니티", "글", "후기", "검색"]):
        keyword = _extract_keyword(text) or "여행"
        posts = _search_posts(db, keyword)
        if posts:
            return _format_post_results(posts)

    if any(keyword in lowered for keyword in ["맛집", "음식점", "식당", "모범음식점", "먹거리"]):
        keyword = _extract_keyword(text) or "맛집"
        locations = _search_locations(db, keyword)
        if locations:
            return _format_location_results(locations)

    if any(keyword in lowered for keyword in ["축제", "행사", "공연", "일정", "이벤트"]):
        keyword = _extract_keyword(text) or "축제"
        locations = _search_locations(db, keyword)
        if locations:
            return _format_location_results(locations)

    if any(keyword in lowered for keyword in ["관광지", "추천", "명소", "가볼만한", "여행지"]):
        keyword = _extract_keyword(text) or "관광"
        locations = _search_locations(db, keyword)
        if locations:
            return _format_location_results(locations)

    if db is not None:
        keyword = _extract_keyword(text) or "서울"
        locations = _search_locations(db, keyword)
        if locations:
            return _format_location_results(locations)

    api_key = _get_api_key()
    model_candidates = _get_model_candidates()

    if not api_key:
        return "OpenAI API 키가 설정되지 않아 기본 응답으로 답변합니다. 질문: " + message

    client = openai.OpenAI(api_key=api_key)

    last_error: Exception | None = None
    for model_name in model_candidates:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": message}],
            )
            content = response.choices[0].message.content
            if isinstance(content, list):
                content = "".join(str(part) for part in content)
            return (content or "응답을 생성하지 못했습니다.").strip()
        except Exception as exc:
            last_error = exc
            error_text = str(exc).lower()
            if "429" in str(exc) or "quota" in error_text or "insufficient_quota" in error_text:
                return "OpenAI API 사용량이 부족합니다. 계정의 quota 또는 크레딧 상태를 확인해 주세요."
            if "model" in error_text and "not" in error_text:
                continue
            return f"OpenAI 호출 중 오류가 발생했습니다: {exc}"

    if last_error is not None:
        return f"OpenAI 호출 중 오류가 발생했습니다: {last_error}"
    return "응답을 생성하지 못했습니다."
