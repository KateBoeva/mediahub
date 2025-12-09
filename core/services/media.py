from typing import Dict, List, Optional

from django.core.files.uploadedfile import UploadedFile

from core.repos.media import MediaItemRepo
from core.schemas.media import MediaItemDetailItem, MediaItemCreateItem, MediaItemUpdateItem


class MediaItemService:
    def __init__(self):
        self.repo = MediaItemRepo()

    def get_user_media_list(self, user_id: int) -> List[Dict]:
        medias = self.repo.list(user_id)
        return [
            MediaItemDetailItem(
                id=m.id,
                title=m.title,
                description=m.description,
                created_at=m.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                file_path=m.file.url,
                media_type=m.get_media_type_display(),
            ).model_dump() for m in medias
        ]

    def get_media_item(self, media_id: int, owner_id: int) -> Dict:
        media = self.repo.get_by_id(media_id, owner_id)
        if not media:
            return {}

        return MediaItemDetailItem(
            id=media.id,
            title=media.title,
            description=media.description,
            created_at=media.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            file_path=media.file.url,
            media_type=media.get_media_type_display(),
        ).model_dump()

    def create_media_item(self, init: MediaItemCreateItem, file: UploadedFile) -> Dict:
        media = self.repo.create(init, file)
        return MediaItemDetailItem(
            id=media.id,
            title=media.title,
            description=media.description,
            created_at=media.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            file_path=media.file.url,
            media_type=media.get_media_type_display(),
        ).model_dump()

    def update_media_item(self, media_id: int, init: MediaItemUpdateItem, file: Optional[UploadedFile]) -> Dict:
        media = self.repo.update(media_id, init, file)
        return MediaItemDetailItem(
            id=media.id,
            title=media.title,
            description=media.description,
            created_at=media.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            file_path=media.file.url,
            media_type=media.get_media_type_display(),
        ).model_dump()

    def delete_media_item(self, media_id: int) -> None:
        self.repo.delete(media_id)
