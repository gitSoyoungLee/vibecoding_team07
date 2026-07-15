from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db import models

def get_posts(db: Session, skip: int = 0, limit: int = 100, search: str | None = None):
    q = db.query(models.Post)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(models.Post.title.ilike(like),
                         models.Post.content.ilike(like),
                         models.Post.nickname.ilike(like)))
    return q.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def create_post(db: Session, data):
    obj = models.Post(
        category_id = data.category_id,
        nickname = data.nickname,
        title = data.title,
        content = data.content,
        password = data.password
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update_post(db: Session, post_id:int, title:str, content:str, category_id:int):
    db.query(models.Post).filter(models.Post.id==post_id).update({
        "title": title,
        "content": content,
        "category_id": category_id
    })
    db.commit()
    return get_post(db, post_id)

def delete_post(db: Session, post_id:int):
    db.query(models.Post).filter(models.Post.id==post_id).delete()
    db.commit()
    return True

# comments
def get_comments(db: Session, post_id:int):
    return db.query(models.Comment).filter(models.Comment.post_id==post_id).order_by(models.Comment.created_at).all()

def create_comment(db: Session, post_id:int, data):
    obj = models.Comment(post_id=post_id, nickname=data.nickname, content=data.content, password=data.password)
    db.add(obj)
    post = db.query(models.Post).filter(models.Post.id==post_id).first()
    if post:
        post.comment_count = (post.comment_count or 0) + 1
    db.commit(); db.refresh(obj)
    return obj

def update_comment(db: Session, comment_id:int, content:str):
    db.query(models.Comment).filter(models.Comment.id==comment_id).update({"content": content})
    db.commit()
    return db.query(models.Comment).filter(models.Comment.id==comment_id).first()

def delete_comment(db: Session, comment_id:int):
    comment = db.query(models.Comment).filter(models.Comment.id==comment_id).first()
    if comment:
        post = db.query(models.Post).filter(models.Post.id==comment.post_id).first()
        db.delete(comment)
        if post:
            post.comment_count = max(0, (post.comment_count or 1) - 1)
        db.commit()
        return True
    return False