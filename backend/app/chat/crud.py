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
