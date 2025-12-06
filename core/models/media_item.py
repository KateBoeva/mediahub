from django.db import models

from core.models import User


class MediaType(models.IntegerChoices):
    IMAGE = 1, 'image'
    VIDEO = 2, 'video'
    AUDIO = 3, 'audio'


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
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец медиафайла'
    )
    file = models.FileField(
        verbose_name='Файл медиа',
        upload_to='media_items/'
    )
    media_type = models.IntegerField(
        verbose_name='Тип медиа',
        choices=MediaType.choices
    )
