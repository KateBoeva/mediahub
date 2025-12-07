from pydantic import BaseModel
from typing import Optional, List


class MediaItemListItem(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: str
    file_path: str
    media_type: str


class MediaItemListResponse(BaseModel):
    items: List[MediaItemListItem]
