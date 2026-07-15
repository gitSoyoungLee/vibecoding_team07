from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommentCreate(BaseModel):
    nickname: str
    content: str
    password: str

class CommentOut(BaseModel):
    id: int
    post_id: int
    nickname: str
    content: str
    created_at: Optional[datetime]
    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    category_id: Optional[int] = None
    nickname: str
    title: str
    content: str
    password: str

class PostOut(BaseModel):
    id: int
    category_id: Optional[int]
    nickname: str
    title: str
    content: str
    views: int
    comment_count: int
    created_at: Optional[datetime]
    class Config:
        orm_mode = True