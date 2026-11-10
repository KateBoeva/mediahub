from typing import Optional

from django.core.files.uploadedfile import UploadedFile
from django.db import DatabaseError

from core.models import MediaItem
from core.repos.base import BaseDBRepo
from core.schemas.media import MediaItemCreateItem, MediaItemUpdateItem


class MediaItemRepo(BaseDBRepo):
    def list(self, user_id: int):
        return MediaItem.objects.filter(owner_id=user_id).order_by('-created_at', '-id')

    def get_by_id(self, media_id: int, owner_id: int) -> Optional[MediaItem]:
        return MediaItem.objects.filter(id=media_id, owner_id=owner_id).first()

    def create(self, init: MediaItemCreateItem, file: UploadedFile, owner_id: int) -> MediaItem:
        init_data = init.model_dump()
        init_data['file'] = file
        init_data['owner_id'] = owner_id
        media_item = MediaItem(**init_data)

        try:
            media_item.save()
        except DatabaseError:
            media_item.file.delete(save=False)
            raise

        return media_item

    def update(
        self, media_id: int, owner_id: int, init: MediaItemUpdateItem, file: Optional[UploadedFile]
    ) -> Optional[MediaItem]:
        item = self.get_by_id(media_id, owner_id)
        if not item:
            return None

        for field, value in init.model_dump(exclude_unset=True).items():
            setattr(item, field, value)

        old_file_name = item.file.name
        if file:
            item.file.save(file.name, file, save=False)

        try:
            item.save()
        except DatabaseError:
            if file:
                item.file.delete(save=False)
            raise

        if file:
            self.delete_file_on_commit(item.file.storage, old_file_name)

        item.refresh_from_db()

        return item

    def delete(self, media_id: int, owner_id: int) -> bool:
        item = self.get_by_id(media_id, owner_id)
        if not item:
            return False

        item.delete()
        self.delete_file_on_commit(item.file.storage, item.file.name)

        return True
