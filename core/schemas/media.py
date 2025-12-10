from pydantic import BaseModel
from typing import Optional, List


class MediaItemDetailItem(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: str
    file_path: str
    media_type: str


class MediaItemListResponse(BaseModel):
    items: List[MediaItemDetailItem]


class MediaItemUpdateItem(BaseModel):
    title: str
    description: Optional[str]
    media_type: str


class MediaItemCreateItem(BaseModel):
    title: str
    description: Optional[str]
    owner_id: int
    media_type: int
