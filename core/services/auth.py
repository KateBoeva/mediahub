import hashlib
import secrets
from typing import Dict, Optional

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone

from core.models import User
from core.repos.auth import AuthRepo
from core.schemas.auth import AuthTokenResponse, LoginItem, RegisterItem


class TooManyLoginAttempts(Exception):
    """Лимит неудачных попыток входа исчерпан"""


class LoginThrottle:
    """
    Считает неудачные попытки входа в кэше: отдельно для пары IP + email
    и для IP целиком, чтобы с одного адреса нельзя было перебирать разные аккаунты.
    Лимит по одному email не вводится: иначе любой мог бы заблокировать чужой вход
    """

    def __init__(self, ip: str, email: str):
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        self.limits = {
            f'login-fail:ip-email:{ip}:{email_hash}': settings.LOGIN_FAILURE_LIMIT,
            f'login-fail:ip:{ip}': settings.LOGIN_FAILURE_IP_LIMIT,
        }
        self.pair_key = next(iter(self.limits))

    def is_blocked(self) -> bool:
        counts = cache.get_many(self.limits.keys())
        return any(counts.get(key, 0) >= limit for key, limit in self.limits.items())

    def register_failure(self) -> None:
        timeout = int(settings.LOGIN_FAILURE_WINDOW.total_seconds())
        for key in self.limits:
            # окно отсчитывается от первой неудачи и не продлевается следующими
            cache.add(key, 0, timeout)
            cache.incr(key)

    def reset(self) -> None:
        cache.delete(self.pair_key)


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

    def login(self, init: LoginItem, ip: str) -> Optional[Dict]:
        throttle = LoginThrottle(ip, init.email)
        if throttle.is_blocked():
            raise TooManyLoginAttempts

        user = authenticate(username=init.email, password=init.password)
        if not user:
            throttle.register_failure()
            return None

        throttle.reset()
        return self.create_token(user.id)

    def get_user_by_token(self, token: str) -> Optional[User]:
        auth_token = self.repo.get_active_token(self._hash_token(token))
        return auth_token.user if auth_token else None

    def logout(self, token: str) -> None:
        self.repo.delete_token(self._hash_token(token))
