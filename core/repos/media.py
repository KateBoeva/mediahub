from core.models import MediaItem


class MediaItemRepo:
    def list(self, user_id: int):
        return MediaItem.objects.filter(owner_id=user_id)
