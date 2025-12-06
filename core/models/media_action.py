from django.db import models


class MediaAction(models.Model):
    media_item = models.ForeignKey(
        to='MediaItem',
        verbose_name='Медиафайл',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        to='User',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'media_action'
        verbose_name = 'Действие с медиафайлом'
        verbose_name_plural = 'Действия с медиафайлами'
        abstract = True


class MediaLike(MediaAction):
    liked_at = models.DateTimeField(
        verbose_name='Дата и время лайка',
        auto_now_add=True
    )

    class Meta:
        db_table = 'media_like'
        verbose_name = 'Лайк медиафайла'
        verbose_name_plural = 'Лайки медиафайлов'


class MediaComment(MediaAction):
    comment_text = models.TextField(
        verbose_name='Текст комментария'
    )
    commented_at = models.DateTimeField(
        verbose_name='Дата и время комментария',
        auto_now_add=True
    )

    class Meta:
        db_table = 'media_comment'
        verbose_name = 'Комментарий к медиафайлу'
        verbose_name_plural = 'Комментарии к медиафайлам'
