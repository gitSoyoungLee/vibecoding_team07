import os
from pathlib import Path

import openai
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _get_api_key() -> str | None:
    return (os.getenv("OPENAI_API_KEY") or "").strip() or None


def _get_model_candidates() -> list[str]:
    configured = (os.getenv("OPENAI_MODEL") or "").strip()
    if configured:
        return [configured]
    return ["gpt-5-mini", "gpt-4o-mini"]


def get_chat_reply(message: str) -> str:
    if not message or not message.strip():
        return "질문을 입력해 주세요."

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
