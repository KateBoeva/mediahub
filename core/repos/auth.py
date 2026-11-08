from datetime import datetime
from typing import Optional

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.models import AuthToken, User
from core.repos.base import BaseDBRepo
from core.schemas.auth import RegisterItem


class AuthRepo(BaseDBRepo):
    def create_user(self, init: RegisterItem) -> Optional[User]:
        try:
            with transaction.atomic():
                return User.objects.create_user(init.email, password=init.password, is_active=True)
        except IntegrityError:
            return None

    def create_token(self, user_id: int, token_hash: str, expires_at: datetime) -> AuthToken:
        return AuthToken.objects.create(user_id=user_id, token_hash=token_hash, expires_at=expires_at)

    def get_active_token(self, token_hash: str) -> Optional[AuthToken]:
        return AuthToken.objects.select_related('user').filter(
            token_hash=token_hash,
            expires_at__gt=timezone.now(),
            user__is_active=True,
        ).first()

    def delete_token(self, token_hash: str) -> None:
        AuthToken.objects.filter(token_hash=token_hash).delete()
