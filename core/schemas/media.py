from pydantic import BaseModel
from typing import Optional, List

from core.models.media_item import MediaType


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
    description: Optional[str] = None
    media_type: MediaType


class MediaItemCreateItem(BaseModel):
    title: str
    description: Optional[str] = None
    media_type: MediaType
