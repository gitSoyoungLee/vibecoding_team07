from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.posts import crud as posts_crud, schemas as posts_schemas
from app.db import models   # 변경: app에서 직접 import 하지 않고 db.models 사용

router = APIRouter(prefix="/api/posts", tags=["posts"])

@router.get("/", response_model=List[posts_schemas.PostOut])
def list_posts(search: str | None = Query(None), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return posts_crud.get_posts(db, skip=skip, limit=limit, search=search)

@router.get("/{post_id}")
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    post = posts_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Not found")
    post.views = (post.views or 0) + 1
    db.add(post); db.commit(); db.refresh(post)
    comments = posts_crud.get_comments(db, post_id)
    return {"post": post, "comments": comments}

@router.post("/", response_model=posts_schemas.PostOut, status_code=201)
def create_post(payload: posts_schemas.PostCreate, db: Session = Depends(get_db)):
    return posts_crud.create_post(db, payload)

@router.put("/{post_id}")
def update_post(post_id:int, payload: dict, db: Session = Depends(get_db)):
    post = posts_crud.get_post(db, post_id)
    if not post: raise HTTPException(status_code=404, detail="Not found")
    if post.password != payload.get("password"): raise HTTPException(status_code=403, detail="Invalid password")
    return posts_crud.update_post(db, post_id, payload.get("title"), payload.get("content"), payload.get("category_id"))

@router.delete("/{post_id}")
def delete_post(post_id:int, payload: dict, db: Session = Depends(get_db)):
    post = posts_crud.get_post(db, post_id)
    if not post: raise HTTPException(status_code=404, detail="Not found")
    if post.password != payload.get("password"): raise HTTPException(status_code=403, detail="Invalid password")
    posts_crud.delete_post(db, post_id)
    return {"ok": True}

@router.post("/{post_id}/comments", status_code=201)
def create_comment(post_id:int, payload: posts_schemas.CommentCreate, db: Session = Depends(get_db)):
    if not posts_crud.get_post(db, post_id): raise HTTPException(status_code=404, detail="Post not found")
    return posts_crud.create_comment(db, post_id, payload)

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    comment = db.query(models.Comment).filter(
        models.Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.password != payload.get("password"):
        raise HTTPException(status_code=403, detail="Invalid password")

    posts_crud.delete_comment(db, comment_id)

    return {"ok": True}