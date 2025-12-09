from django.views import View
from django.http import JsonResponse, HttpRequest

from core.schemas.media import MediaItemListResponse, MediaItemCreateItem, MediaItemUpdateItem
from core.services.media import MediaItemService


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

    def post(self, request):
        data = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "media_type": request.POST.get("media_type"),
            "owner_id": request.user.id,
        }
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"error": "File is required"}, status=400)

        payload = MediaItemCreateItem(**data)

        new_media = self.service.create_media_item(payload, file)
        new_media['file_path'] = request.build_absolute_uri(new_media['file_path'])

        return JsonResponse(new_media, status=201)
