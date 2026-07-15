import os
from pathlib import Path

import openai
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")
API_KEY = os.getenv("OPENAI_API_KEY")


def get_chat_reply(message: str) -> str:
    if not message or not message.strip():
        return "질문을 입력해 주세요."

    if not API_KEY:
        return "OpenAI API 키가 설정되지 않아 기본 응답으로 답변합니다. 질문: " + message

    try:
        client = openai.OpenAI(api_key=API_KEY)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": message}],
        )
        return response.output_text.strip() or "응답을 생성하지 못했습니다."
    except Exception as exc:
        return f"OpenAI 호출 중 오류가 발생했습니다: {exc}"
