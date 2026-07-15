from fastapi import APIRouter

from app.chat.crud import get_chat_reply
from app.chat.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
def create_chat_message(request: ChatRequest):
    reply = get_chat_reply(request.message)
    return ChatResponse(reply=reply)
