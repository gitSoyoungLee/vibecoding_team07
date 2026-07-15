import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


def test_chat_message_endpoint_returns_reply():
    client = TestClient(app)
    response = client.post(
        "/chat/message",
        json={"message": "안녕, 챗봇아"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert isinstance(body["reply"], str)
    assert body["reply"]
