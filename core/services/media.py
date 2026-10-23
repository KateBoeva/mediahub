from typing import Dict, List, Optional

from django.core.files.uploadedfile import UploadedFile

from core.models import MediaItem
from core.repos.media import MediaItemRepo
from core.schemas.media import MediaItemDetailItem, MediaItemCreateItem, MediaItemUpdateItem


class MediaItemService:
    def __init__(self):
        self.repo = MediaItemRepo()

    @staticmethod
    def _to_detail(media: MediaItem) -> Dict:
        return MediaItemDetailItem(
            id=media.id,
            title=media.title,
            description=media.description,
            created_at=media.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            file_path=media.file.url,
            media_type=media.get_media_type_display(),
        ).model_dump()

    def get_user_media_list(self, user_id: int) -> List[Dict]:
        return [self._to_detail(m) for m in self.repo.list(user_id)]

    def get_media_item(self, media_id: int, owner_id: int) -> Optional[Dict]:
        media = self.repo.get_by_id(media_id, owner_id)
        return self._to_detail(media) if media else None

    def create_media_item(self, init: MediaItemCreateItem, file: UploadedFile, owner_id: int) -> Dict:
        media = self.repo.create(init, file, owner_id)
        return self._to_detail(media)

    def update_media_item(
        self, media_id: int, owner_id: int, init: MediaItemUpdateItem, file: Optional[UploadedFile]
    ) -> Optional[Dict]:
        media = self.repo.update(media_id, owner_id, init, file)
        return self._to_detail(media) if media else None

    def delete_media_item(self, media_id: int, owner_id: int) -> bool:
        return self.repo.delete(media_id, owner_id)
