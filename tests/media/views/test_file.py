from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
from model_bakery.recipe import Recipe

from core.models import MediaItem
from core.models.media_item import MediaType
from tests.files import JPEG_BYTES


@pytest.mark.django_db
class TestMediaFileView:
    media_item_recipe = Recipe(MediaItem, file=ContentFile(JPEG_BYTES, name="test.jpg"), media_type=MediaType.IMAGE)

    @pytest.fixture
    def media_item(self, user_client):
        return self.media_item_recipe.make(owner=user_client.user)

    @pytest.fixture
    def file_url(self, user_client, media_item):
        return user_client.get(reverse('core:media-retrieve', args=(media_item.id,))).json()['file_path']

    @staticmethod
    def token_of(file_url):
        return parse_qs(urlparse(file_url).query)['token'][0]

    def test_ok_without_authorization(self, file_url):
        resp = Client().get(file_url)

        assert resp.status_code == 200
        assert resp['Content-Type'] == 'image/jpeg'
        assert b''.join(resp.streaming_content) == JPEG_BYTES

    def test_content_type_is_taken_from_content(self, user_client):
        # файл, загруженный до проверки типов, мог сохраниться с опасным расширением
        media_item = self.media_item_recipe.make(owner=user_client.user, file=ContentFile(JPEG_BYTES, name='x.html'))
        file_url = user_client.get(reverse('core:media-retrieve', args=(media_item.id,))).json()['file_path']

        resp = Client().get(file_url)

        assert resp.status_code == 200
        assert resp['Content-Type'] == 'image/jpeg'

    @pytest.mark.parametrize('query', ['', '?token=', '?token=garbage'])
    def test_invalid_token(self, media_item, query):
        resp = Client().get(reverse('core:media-file', args=(media_item.id,)) + query)

        assert resp.status_code == 404

    def test_tampered_token(self, file_url):
        resp = Client().get(file_url[:-1] + ('A' if file_url[-1] != 'A' else 'B'))

        assert resp.status_code == 404

    def test_expired_token(self, file_url, settings):
        settings.MEDIA_FILE_URL_TTL = timedelta(seconds=-1)

        assert Client().get(file_url).status_code == 404

    def test_token_of_another_item(self, file_url):
        other_item = self.media_item_recipe.make()
        url = reverse('core:media-file', args=(other_item.id,)) + '?token=' + self.token_of(file_url)

        assert Client().get(url).status_code == 404

    def test_old_link_stops_working_after_file_replaced(self, user_client, media_item, file_url):
        resp = user_client.post(reverse('core:media-retrieve', args=(media_item.id,)), data={
            'title': 'Updated',
            'media_type': MediaType.IMAGE.value,
            'file': SimpleUploadedFile('new.jpg', JPEG_BYTES),
        })

        assert resp.status_code == 200
        assert Client().get(file_url).status_code == 404
        assert Client().get(resp.json()['file_path']).status_code == 200

    def test_deleted_item(self, user_client, media_item, file_url):
        user_client.delete(reverse('core:media-retrieve', args=(media_item.id,)))

        assert Client().get(file_url).status_code == 404

    def test_media_root_is_not_served_directly(self, media_item):
        assert Client().get(f'/media/{media_item.file.name}').status_code == 404
