from typing import IO, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import filetype
from django.conf import settings
from django.core import signing
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import FieldFile
from django.urls import reverse

from core.models import MediaItem
from core.models.media_item import MediaType
from core.repos.media import MediaItemRepo
from core.schemas.media import MediaItemDetailItem, MediaItemCreateItem, MediaItemUpdateItem

FILE_URL_SALT = 'core.media.file'
DEFAULT_CONTENT_TYPE = 'application/octet-stream'


class MediaFileError(Exception):
    """Файл не подходит для загрузки, текст ошибки отдаётся клиенту"""


class MediaItemService:
    def __init__(self):
        self.repo = MediaItemRepo()

    @staticmethod
    def _file_url(media: MediaItem) -> str:
        """
        Ссылка на файл, подписанная владельцем и именем файла:
        её можно отдать в <img src>, без заголовка Authorization
        """
        token = signing.dumps({'owner': media.owner_id, 'file': media.file.name}, salt=FILE_URL_SALT)
        return f"{reverse('core:media-file', args=(media.id,))}?{urlencode({'token': token})}"

    @classmethod
    def _to_detail(cls, media: MediaItem) -> Dict:
        return MediaItemDetailItem(
            id=media.id,
            title=media.title,
            description=media.description,
            created_at=media.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            file_path=cls._file_url(media),
            media_type=media.get_media_type_display(),
        ).model_dump()

    @staticmethod
    def _check_file_type(file: IO, media_type: MediaType) -> filetype.Type:
        kind = filetype.guess(file)
        if not kind or kind.mime.split('/')[0] != media_type.label:
            raise MediaFileError(f'File is not a valid {media_type.label}')

        return kind

    @classmethod
    def _check_upload(cls, file: UploadedFile, media_type: MediaType) -> None:
        if file.size > settings.MEDIA_MAX_FILE_SIZE:
            raise MediaFileError(f'File is too large, max size is {settings.MEDIA_MAX_FILE_SIZE // 1024 // 1024} MB')

        kind = cls._check_file_type(file, media_type)
        # расширение берём по содержимому, а не из имени, которое прислал клиент
        file.name = f'upload.{kind.extension}'

    def get_user_media_list(self, user_id: int) -> List[Dict]:
        return [self._to_detail(m) for m in self.repo.list(user_id)]

    def get_media_item(self, media_id: int, owner_id: int) -> Optional[Dict]:
        media = self.repo.get_by_id(media_id, owner_id)
        return self._to_detail(media) if media else None

    def get_media_file(self, media_id: int, token: str) -> Optional[Tuple[FieldFile, str]]:
        """Возвращает файл и его content type, если ссылка подписана и не истекла"""
        try:
            data = signing.loads(token, salt=FILE_URL_SALT, max_age=settings.MEDIA_FILE_URL_TTL)
        except signing.BadSignature:
            return None

        media = self.repo.get_by_id(media_id, data['owner'])
        # после замены файла старые ссылки перестают работать
        if not media or media.file.name != data['file']:
            return None

        kind = filetype.guess(media.file.open('rb'))
        return media.file, kind.mime if kind else DEFAULT_CONTENT_TYPE

    def create_media_item(self, init: MediaItemCreateItem, file: UploadedFile, owner_id: int) -> Dict:
        self._check_upload(file, init.media_type)
        media = self.repo.create(init, file, owner_id)
        return self._to_detail(media)

    def update_media_item(
        self, media_id: int, owner_id: int, init: MediaItemUpdateItem, file: Optional[UploadedFile]
    ) -> Optional[Dict]:
        if file:
            self._check_upload(file, init.media_type)
        else:
            media = self.repo.get_by_id(media_id, owner_id)
            if not media:
                return None

            # без нового файла смена типа допустима, только если старый файл ему соответствует
            if media.media_type != init.media_type:
                with media.file.open('rb') as stored:
                    self._check_file_type(stored, init.media_type)

        media = self.repo.update(media_id, owner_id, init, file)
        return self._to_detail(media) if media else None

    def delete_media_item(self, media_id: int, owner_id: int) -> bool:
        return self.repo.delete(media_id, owner_id)
