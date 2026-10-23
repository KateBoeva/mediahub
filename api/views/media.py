from django.views import View
from django.http import JsonResponse, HttpRequest, HttpResponse

from core.schemas.media import MediaItemListResponse, MediaItemCreateItem, MediaItemUpdateItem
from core.services.media import MediaItemService
from utils.decorators import with_payload
from utils.mixins import LoginRequiredJsonMixin

NOT_FOUND_RESPONSE = {'error': 'Media item not found'}


class MediaListView(LoginRequiredJsonMixin, View):
    service = MediaItemService()

    def get(self, request: HttpRequest):
        media_list = self.service.get_user_media_list(request.user.id)
        for item in media_list:
            item['file_path'] = request.build_absolute_uri(item['file_path'])

        return JsonResponse(MediaItemListResponse(items=media_list).model_dump())


class MediaRetrieveView(LoginRequiredJsonMixin, View):
    service = MediaItemService()

    def get(self, request: HttpRequest, media_id: int):
        media_item = self.service.get_media_item(media_id, request.user.id)

        if not media_item:
            return JsonResponse(NOT_FOUND_RESPONSE, status=404)

        media_item['file_path'] = request.build_absolute_uri(media_item['file_path'])
        return JsonResponse(media_item)

    @with_payload
    def post(self, request: HttpRequest, media_id: int, payload: MediaItemUpdateItem):
        file = request.FILES.get('file')
        updated_media = self.service.update_media_item(media_id, request.user.id, payload, file)

        if not updated_media:
            return JsonResponse(NOT_FOUND_RESPONSE, status=404)

        updated_media['file_path'] = request.build_absolute_uri(updated_media['file_path'])
        return JsonResponse(updated_media)

    def delete(self, request: HttpRequest, media_id: int):
        if not self.service.delete_media_item(media_id, request.user.id):
            return JsonResponse(NOT_FOUND_RESPONSE, status=404)

        return HttpResponse(status=204)


class MediaCreateView(LoginRequiredJsonMixin, View):
    service = MediaItemService()

    @with_payload
    def post(self, request: HttpRequest, payload: MediaItemCreateItem):
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'errors': {'file': 'File is required'}}, status=400)

        new_media = self.service.create_media_item(payload, file, request.user.id)
        new_media['file_path'] = request.build_absolute_uri(new_media['file_path'])

        return JsonResponse(new_media, status=201)
