import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from django.urls import reverse
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
        payload['owner_id'] = user_client.user.id
        resp = user_client.post(url, data=payload)
        assert resp.status_code == 201

        actual_item = resp.json()
        assert MediaItem.objects.all().count() == 1
        assert len(actual_item) == len(MediaItemDetailItem.__pydantic_fields__)
        assert actual_item['title'] == payload['title']
        assert actual_item['description'] == payload['description']
        assert actual_item['media_type'] == MediaType(payload['media_type']).name.lower()
        assert actual_item['file_path'].endswith('new_test.jpg')

