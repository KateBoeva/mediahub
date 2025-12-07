from django.views import View
from django.http import JsonResponse

from core.schemas.media import MediaItemListResponse
from core.services.media import MediaListService


class MediaListView(View):
    service = MediaListService()

    def get(self, request):
        media_list = self.service.list_media_for_user(request.user.id)
        for item in media_list:
            item['file_path'] = request.build_absolute_uri(item['file_path'])

        return JsonResponse(MediaItemListResponse(items=media_list).model_dump())
