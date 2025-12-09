from django.views import View
from django.http import JsonResponse, HttpRequest

from core.schemas.media import MediaItemListResponse, MediaItemCreateItem, MediaItemUpdateItem
from core.services.media import MediaItemService
from utils.decorators import endpoint


class MediaListView(View):
    service = MediaItemService()

    def get(self, request: HttpRequest):
        media_list = self.service.get_user_media_list(request.user.id)
        for item in media_list:
            item['file_path'] = request.build_absolute_uri(item['file_path'])

        return JsonResponse(MediaItemListResponse(items=media_list).model_dump())


class MediaRetrieveView(View):
    service = MediaItemService()

    def get(self, request: HttpRequest, media_id: int):
        media_item = self.service.get_media_item(media_id, request.user.id)

        if not media_item:
            return JsonResponse({'error': 'Media item not found'}, status=404)

        media_item['file_path'] = request.build_absolute_uri(media_item['file_path'])
        return JsonResponse(media_item)

    def put(self, request: HttpRequest, media_id: int, payload: MediaItemUpdateItem):
        file = self.request.FILES['file']
        updated_media = self.service.update_media_item(media_id, payload, file)
        updated_media['file_path'] = request.build_absolute_uri(updated_media['file_path'])
        return JsonResponse(updated_media)


class MediaCreateView(View):
    service = MediaItemService()

    @endpoint
    def post(self, request, payload: MediaItemCreateItem):
        file = request.FILES['file']
        new_media = self.service.create_media_item(payload, file)
        new_media['file_path'] = request.build_absolute_uri(new_media['file_path'])

        return JsonResponse(new_media, status=201)
