from pathlib import Path

import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe

from core.models import MediaItem
from core.models.media_item import MediaType
from core.schemas.media import MediaItemDetailItem
from tests.files import JPEG_BYTES, MP3_BYTES


@pytest.mark.django_db
class TestMediaItemCreateView:
    media_item_recipe = Recipe(MediaItem, file=ContentFile(JPEG_BYTES, name="test.jpg"), media_type=MediaType.IMAGE)

    @pytest.fixture
    def media_item(self):
        return self.media_item_recipe.make()

    @pytest.fixture
    def url(self):
        return reverse('core:media-create')

    @pytest.fixture
    def payload(self):
        return {
            'title': 'New Media',
            'description': 'New Description',
            'media_type': 1,
            'file': SimpleUploadedFile("new_test.jpg", JPEG_BYTES),
        }

    def test_ok(self, user_client, payload, url):
        resp = user_client.post(url, data=payload)
        assert resp.status_code == 201

        actual_item = resp.json()
        assert MediaItem.objects.all().count() == 1
        assert len(actual_item) == len(MediaItemDetailItem.__pydantic_fields__)
        assert actual_item['title'] == payload['title']
        assert actual_item['description'] == payload['description']
        assert actual_item['media_type'] == MediaType(payload['media_type']).name.lower()
        media_item = MediaItem.objects.get()
        file_url = reverse('core:media-file', args=(media_item.id,))
        assert actual_item['file_path'].startswith(f'http://testserver{file_url}?token=')
        assert media_item.owner_id == user_client.user.id
        assert media_item.file.read() == JPEG_BYTES

    def test_owner_id_in_payload_is_ignored(self, user_client, payload, url):
        other_user = baker.make('core.User')
        payload['owner_id'] = other_user.id
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 201
        assert MediaItem.objects.get().owner_id == user_client.user.id

    def test_without_file(self, user_client, payload, url):
        del payload['file']
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 400
        assert MediaItem.objects.count() == 0

    @pytest.mark.parametrize('media_type, content', [
        (MediaType.IMAGE, MP3_BYTES),
        (MediaType.AUDIO, JPEG_BYTES),
        (MediaType.IMAGE, b'<html><script>alert(1)</script></html>'),
        (MediaType.IMAGE, b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'),
    ])
    def test_file_does_not_match_media_type(self, user_client, payload, url, settings, media_type, content):
        payload['media_type'] = media_type.value
        payload['file'] = SimpleUploadedFile("file.jpg", content)
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 400
        assert resp.json() == {'errors': {'file': f'File is not a valid {media_type.label}'}}
        assert MediaItem.objects.count() == 0
        assert [path for path in Path(settings.MEDIA_ROOT).rglob('*') if path.is_file()] == []

    def test_file_too_large(self, user_client, payload, url, settings):
        settings.MEDIA_MAX_FILE_SIZE = len(JPEG_BYTES) - 1
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 400
        assert 'too large' in resp.json()['errors']['file']
        assert MediaItem.objects.count() == 0

    def test_extension_is_taken_from_content(self, user_client, payload, url):
        payload['file'] = SimpleUploadedFile("evil.html", JPEG_BYTES)
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 201
        assert MediaItem.objects.get().file.name.endswith('.jpg')

    def test_invalid_media_type(self, user_client, payload, url):
        payload['media_type'] = 999
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 400
        assert MediaItem.objects.count() == 0

    @pytest.mark.parametrize('title', ['', 'x' * 256])
    def test_invalid_title(self, user_client, payload, url, title):
        payload['title'] = title
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 400
        assert MediaItem.objects.count() == 0

    def test_title_max_length(self, user_client, payload, url):
        payload['title'] = 'x' * 255
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 201

    def test_anonymous(self, anonymous_client, payload, url):
        resp = anonymous_client.post(url, data=payload)

        assert resp.status_code == 401
        assert MediaItem.objects.count() == 0
