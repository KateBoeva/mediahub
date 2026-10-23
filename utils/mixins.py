from django.http import JsonResponse


class LoginRequiredJsonMixin:

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        return super().dispatch(request, *args, **kwargs)
