from django.http import JsonResponse, HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.schemas.auth import LoginItem, RegisterItem
from core.services.auth import AuthService
from utils.decorators import with_payload
from utils.mixins import LoginRequiredJsonMixin


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    service = AuthService()

    @with_payload
    def post(self, request: HttpRequest, payload: RegisterItem):
        token = self.service.register(payload)
        if not token:
            return JsonResponse({'errors': {'email': 'User with this email already exists'}}, status=409)

        return JsonResponse(token, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    service = AuthService()

    @with_payload
    def post(self, request: HttpRequest, payload: LoginItem):
        token = self.service.login(payload)
        if not token:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)

        return JsonResponse(token)


class LogoutView(LoginRequiredJsonMixin, View):
    service = AuthService()

    def post(self, request: HttpRequest):
        self.service.logout(request.auth_token)
        return HttpResponse(status=204)
