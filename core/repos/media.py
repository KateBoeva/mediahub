from typing import Optional

from django.core.files.uploadedfile import UploadedFile

from core.models import MediaItem
from core.schemas.media import MediaItemCreateItem, MediaItemUpdateItem


class MediaItemRepo:
    def list(self, user_id: int):
        return MediaItem.objects.filter(owner_id=user_id)

    def get_by_id(self, media_id: int, owner_id: int):
        item = MediaItem.objects.filter(id=media_id, owner_id=owner_id)
        return item.first() if item.exists() else None

    def create(self, init: MediaItemCreateItem, file: UploadedFile) -> MediaItem:
        init_data = init.model_dump()
        init_data['file'] = file
        media_item = MediaItem.objects.create(**init_data)

        return media_item

    def update(self, media_id: int, init: MediaItemUpdateItem, file: Optional[UploadedFile]) -> MediaItem:
        item = MediaItem.objects.get(id=media_id)

        for field, value in init.model_dump().items():
            setattr(item, field, value)

        if file:
            item.file.save(file.name, file, save=False)

        item.save()

        return self.get_by_id(media_id, item.owner_id)

    def delete(self, media_id: int) -> None:
        MediaItem.objects.filter(id=media_id).delete()
