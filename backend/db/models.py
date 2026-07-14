from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base

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
    longitude = Column(Float)
    latitude = Column(Float)
    map_level = Column(Integer)
    area_code = Column(String)
    sigungu_code = Column(String)
    category1 = Column(String)
    category2 = Column(String)
    category3 = Column(String)
    image_url = Column(Text)
    thumbnail_url = Column(Text)
    copyright_code = Column(String)
    created_time = Column(String)
    modified_time = Column(String)