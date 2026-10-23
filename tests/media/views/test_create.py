import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe

from core.models import MediaItem
from core.models.media_item import MediaType
from core.schemas.media import MediaItemDetailItem


@pytest.mark.django_db
class TestMediaItemCreateView:
    media_item_recipe = Recipe(MediaItem, file=ContentFile(b"fake data", name="test.jpg"))

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
            'file': SimpleUploadedFile("new_test.jpg", b"new fake data"),
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
        assert actual_item['file_path'].endswith('new_test.jpg')
        assert MediaItem.objects.get().owner_id == user_client.user.id

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

    def test_invalid_media_type(self, user_client, payload, url):
        payload['media_type'] = 999
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 400
        assert MediaItem.objects.count() == 0

    def test_anonymous(self, anonymous_client, payload, url):
        resp = anonymous_client.post(url, data=payload)

        assert resp.status_code == 401
        assert MediaItem.objects.count() == 0
