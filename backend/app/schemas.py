from pydantic import BaseModel
from typing import Optional

class LocationBase(BaseModel):
    content_id: Optional[str]
    content_type_id: Optional[int]
    title: Optional[str]
    addr1: Optional[str]
    addr2: Optional[str]
    zipcode: Optional[str]
    tel: Optional[str]
    longitude: Optional[float]
    latitude: Optional[float]
    map_level: Optional[int]
    area_code: Optional[str]
    sigungu_code: Optional[str]
    category1: Optional[str]
    category2: Optional[str]
    category3: Optional[str]
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    copyright_code: Optional[str]
    created_time: Optional[str]
    modified_time: Optional[str]

class LocationOut(LocationBase):
    id: int

    class Config:
        orm_mode = True