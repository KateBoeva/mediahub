from typing import Optional

from django.core.files.uploadedfile import UploadedFile

from core.models import MediaItem
from core.schemas.media import MediaItemCreateItem, MediaItemUpdateItem


class MediaItemRepo:
    def list(self, user_id: int):
        return MediaItem.objects.filter(owner_id=user_id)

    def get_by_id(self, media_id: int, owner_id: int) -> Optional[MediaItem]:
        return MediaItem.objects.filter(id=media_id, owner_id=owner_id).first()

    def create(self, init: MediaItemCreateItem, file: UploadedFile, owner_id: int) -> MediaItem:
        init_data = init.model_dump()
        init_data['file'] = file
        init_data['owner_id'] = owner_id
        media_item = MediaItem.objects.create(**init_data)

        return media_item

    def update(
        self, media_id: int, owner_id: int, init: MediaItemUpdateItem, file: Optional[UploadedFile]
    ) -> Optional[MediaItem]:
        item = self.get_by_id(media_id, owner_id)
        if not item:
            return None

        for field, value in init.model_dump().items():
            setattr(item, field, value)

        if file:
            item.file.delete(save=False)
            item.file.save(file.name, file, save=False)

        item.save()
        item.refresh_from_db()

        return item

    def delete(self, media_id: int, owner_id: int) -> bool:
        item = self.get_by_id(media_id, owner_id)
        if not item:
            return False

        item.file.delete(save=False)
        item.delete()

        return True
