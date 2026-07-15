import os
import sys
from types import SimpleNamespace

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.chat import crud
from app.main import app


def test_chat_message_endpoint_returns_reply(monkeypatch):
    monkeypatch.setattr(crud, "get_chat_reply", lambda message: "mocked reply")

    client = TestClient(app)
    response = client.post(
        "/chat/message",
        json={"message": "안녕, 챗봇아"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert body["reply"] == "mocked reply"


def test_quota_error_is_reported_plainly(monkeypatch):
    def mock_get_chat_reply(message: str) -> str:
        return "OpenAI 호출 중 오류가 발생했습니다: Error code: 429"

    monkeypatch.setattr(crud, "get_chat_reply", mock_get_chat_reply)

    client = TestClient(app)
    response = client.post(
        "/chat/message",
        json={"message": "왜안됨?"},
    )

    assert response.status_code == 200
    assert "429" in response.json()["reply"]


def test_chat_uses_configured_model(monkeypatch):
    captured = {}

    class DummyCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="테스트 응답"))]
            )

    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.chat = SimpleNamespace(completions=DummyCompletions())

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
    monkeypatch.setattr(crud.openai, "OpenAI", DummyClient)

    reply = crud.get_chat_reply("모델 테스트")

    assert reply == "테스트 응답"
    assert captured["model"] == "gpt-5-mini"
