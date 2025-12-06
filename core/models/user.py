from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import QuerySet


class UserManager(BaseUserManager):
    def get_queryset(self):
        return QuerySet(self.model, using=self._db)

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def search(self, q):
        qs = super().get_queryset()
        if not q:
            return qs

        return qs.filter(models.Q(email__icontains=q) | models.Q(name__icontains=q))


class User(AbstractBaseUser):
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    email = models.EmailField(
        verbose_name='Email пользователя',
        max_length=255,
        unique=True,
    )

    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
