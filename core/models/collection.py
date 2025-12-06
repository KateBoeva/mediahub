from django.db import models


class Collection(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Название коллекции'
    )
    description = models.TextField(
        verbose_name='Описание коллекции',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'collection'
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'

