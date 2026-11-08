from django.db import models


class AuthToken(models.Model):
    token_hash = models.CharField(
        verbose_name='Хеш токена',
        max_length=64,
        unique=True,
    )
    user = models.ForeignKey(
        to='User',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        verbose_name='Дата и время истечения',
    )

    def __str__(self):
        return "Токен пользователя {0}".format(self.user.email)

    class Meta:
        db_table = 'auth_token'
        verbose_name = 'Токен авторизации'
        verbose_name_plural = 'Токены авторизации'
