"""장소(Location) API 요청/응답 형태 정의 (Pydantic). DB 테이블 구조는 db/models.py 참고.
여기 필드를 바꾸면 API 응답 모양이 바뀌고, DB 컬럼을 바꾸려면 db/models.py를 고쳐야 한다.
"""

from pydantic import BaseModel
from typing import List, Optional

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
    event_start_date: Optional[str]
    event_end_date: Optional[str]

class LocationOut(LocationBase):
    id: int

    class Config:
        from_attributes = True


class LocationListOut(BaseModel):
    items: List[LocationOut]
    total: int
