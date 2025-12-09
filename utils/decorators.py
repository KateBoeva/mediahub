import inspect

from functools import wraps
from pydantic import ValidationError

from django.http import JsonResponse


def endpoint(view_func):
    """ Декоратор для вьюх, автоматом вытаскивает pydantic-модель из аннотации параметра payload """
    sig = inspect.signature(view_func)
    if view_func.__name__ in ('post', 'put', 'patch'):
        payload_param = sig.parameters.get("payload")
        if payload_param is None:
            raise ValueError(f"Метод {view_func.__name__} должен иметь параметр payload с pydantic-моделью")

        model_class = payload_param.annotation
        print(type(model_class))
        if model_class is getattr(inspect, "_empty"):
            raise ValueError(f"Параметр payload в view {view_func.__name__} должен быть аннотирован pydantic-моделью")

    @wraps(view_func)
    def _wrapped(self, request, *args, **kwargs):
        data = {**request.POST.dict(), **request.FILES.dict()}
        try:
            payload = model_class(**data)
        except ValidationError as e:
            return JsonResponse({"errors": e.json()}, status=400)
        return view_func(self, request, payload, *args, **kwargs)

    return _wrapped
