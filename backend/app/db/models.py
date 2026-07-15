from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String, unique=True, index=True)
    content_type_id = Column(Integer)

    title = Column(Text)
    addr1 = Column(Text)
    addr2 = Column(Text)
    zipcode = Column(String)
    tel = Column(String)

    longitude = Column(String)
    latitude = Column(String)

    category1 = Column(String)
    category2 = Column(String)
    category3 = Column(String)

    image_url = Column(Text)
    thumbnail_url = Column(Text)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(Integer, nullable=False)

    nickname = Column(String(50), nullable=False)

    title = Column(String(200), nullable=False)

    content = Column(Text, nullable=False)

    password = Column(Text, nullable=False)

    views = Column(Integer, default=0)

    comment_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now(ZoneInfo("Asia/Seoul")))

    updated_at = Column(
        DateTime,
        default=datetime.now(ZoneInfo("Asia/Seoul")),
        onupdate=datetime.now(ZoneInfo("Asia/Seoul")),
    )

    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    post_id = Column(
        Integer,
        ForeignKey("posts.id"),
        nullable=False,
    )

    nickname = Column(String(50), nullable=False)

    content = Column(Text, nullable=False)

    password = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.now(ZoneInfo("Asia/Seoul")))

    updated_at = Column(
        DateTime,
        default=datetime.now(ZoneInfo("Asia/Seoul")),
        onupdate=datetime.now(ZoneInfo("Asia/Seoul")),
    )

    post = relationship(
        "Post",
        back_populates="comments",
    )