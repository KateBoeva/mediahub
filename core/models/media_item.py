import re
import uuid
from pathlib import Path

from django.db import models

from core.models import User


class MediaType(models.IntegerChoices):
    IMAGE = 1, 'image'
    VIDEO = 2, 'video'
    AUDIO = 3, 'audio'


def media_item_upload_to(instance: 'MediaItem', filename: str) -> str:
    """
    Кладёт файл под случайным именем в папку владельца,
    чтобы адрес файла нельзя было угадать по исходному имени
    """
    suffix = Path(filename).suffix.lower()
    if not re.fullmatch(r'\.[a-z0-9]{1,10}', suffix):
        suffix = ''

    return f'media_items/{instance.owner_id}/{uuid.uuid4().hex}{suffix}'


class MediaItem(models.Model):
    title = models.CharField(
        verbose_name='Наименование медиафайла',
        max_length=255
    )
    description = models.TextField(
        verbose_name='Описание медиафайла',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата и время изменения',
        auto_now=True
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец медиафайла'
    )
    file = models.FileField(
        verbose_name='Файл медиа',
        upload_to=media_item_upload_to
    )
    media_type = models.IntegerField(
        verbose_name='Тип медиа',
        choices=MediaType.choices
    )

    class Meta:
        db_table = 'media_item'
        verbose_name = 'Медиа объект'
        verbose_name_plural = 'Медиа объекты'

    def __str__(self):
        return f'{self.get_media_type_display()} "{self.title}"'
