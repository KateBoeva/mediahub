from typing import Optional

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.services.auth import AuthService


def _get_bearer_token(request: HttpRequest) -> Optional[str]:
    scheme, _, token = request.headers.get('Authorization', '').partition(' ')
    return token.strip() if scheme.lower() == 'bearer' and token.strip() else None


class LoginRequiredJsonMixin:
    """
    Авторизует запрос только по заголовку Authorization: Bearer <token>

    CSRF отключён, потому что браузер не подставляет этот заголовок сам.
    По этой же причине сессионная кука здесь не принимается
    """

    auth_service = AuthService()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        token = _get_bearer_token(request)
        user = self.auth_service.get_user_by_token(token) if token else None

        if not user:
            response = JsonResponse({'error': 'Authentication required'}, status=401)
            response['WWW-Authenticate'] = 'Bearer'
            return response

        request.user = user
        request.auth_token = token

        return super().dispatch(request, *args, **kwargs)
