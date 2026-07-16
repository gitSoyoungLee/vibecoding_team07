import inspect

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.chat import crud
from app.chat.schemas import ChatRequest, ChatResponse
from app.db.session import get_db

router = APIRouter(prefix="/chat", tags=["chat"])
api_router = APIRouter(prefix="/api", tags=["chat"])


def _get_chat_reply(request_message: str, db: Session | None = None) -> str:
    signature = inspect.signature(crud.get_chat_reply)
    if "db" in signature.parameters or any(param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()):
        return crud.get_chat_reply(request_message, db=db)
    return crud.get_chat_reply(request_message)


@router.post("/message", response_model=ChatResponse)
def create_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    reply = _get_chat_reply(request.message, db=db)
    return ChatResponse(reply=reply)


@api_router.post("/chat", response_model=ChatResponse)
def create_api_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    reply = _get_chat_reply(request.message, db=db)
    return ChatResponse(reply=reply)
