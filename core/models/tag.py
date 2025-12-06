from django.db import models


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название тега'
    )
    media_item = models.ManyToManyField(
        to='MediaItem',
        verbose_name='Медиафайлы',
        related_name='tags',
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tag'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
