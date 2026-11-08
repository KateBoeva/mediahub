import hashlib
import secrets
from typing import Dict, Optional

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone

from core.models import User
from core.repos.auth import AuthRepo
from core.schemas.auth import AuthTokenResponse, LoginItem, RegisterItem


class AuthService:
    def __init__(self):
        self.repo = AuthRepo()

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def create_token(self, user_id: int) -> Dict:
        token = secrets.token_urlsafe(32)
        auth_token = self.repo.create_token(
            user_id, self._hash_token(token), timezone.now() + settings.AUTH_TOKEN_TTL
        )

        return AuthTokenResponse(token=token, expires_at=auth_token.expires_at.isoformat()).model_dump()

    def register(self, init: RegisterItem) -> Optional[Dict]:
        user = self.repo.create_user(init)
        return self.create_token(user.id) if user else None

    def login(self, init: LoginItem) -> Optional[Dict]:
        user = authenticate(username=init.email, password=init.password)
        return self.create_token(user.id) if user else None

    def get_user_by_token(self, token: str) -> Optional[User]:
        auth_token = self.repo.get_active_token(self._hash_token(token))
        return auth_token.user if auth_token else None

    def logout(self, token: str) -> None:
        self.repo.delete_token(self._hash_token(token))
