from typing import Dict, List

from core.repos.media import MediaItemRepo
from core.schemas.media import MediaItemListItem


class MediaListService:
    def __init__(self):
        self.repo = MediaItemRepo()

    def list_media_for_user(self, user_id: int) -> List[Dict]:
        medias = self.repo.list(user_id)
        return [
            MediaItemListItem(
                id=m.id,
                title=m.title,
                description=m.description,
                created_at=m.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                file_path=m.file.url,
                media_type=m.get_media_type_display(),
            ).model_dump() for m in medias
        ]
