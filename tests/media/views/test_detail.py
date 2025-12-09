import pytest
from django.core.files.base import ContentFile

from django.urls import reverse
from model_bakery.recipe import Recipe

from core.models import MediaItem
from core.schemas.media import MediaItemDetailItem


@pytest.mark.django_db
class TestMediaItemRetrieveView:
    media_item_recipe = Recipe(MediaItem, file=ContentFile(b"fake data", name="test.jpg"))

    @pytest.fixture
    def media_item(self):
        return self.media_item_recipe.make()

    @pytest.fixture
    def url(self, media_item):
        return reverse('core:media-retrieve', args=(media_item.id,))

    def test_ok(self, user_client, url, media_item):
        media_item.owner = user_client.user
        media_item.save()
        resp = user_client.get(url)

        assert resp.status_code == 200
        item = resp.json()
        assert len(item) == len(MediaItemDetailItem.__pydantic_fields__)
        assert item['id'] == media_item.id
        assert item['title'] == media_item.title
        assert item['description'] == media_item.description
        assert item['media_type'] == media_item.get_media_type_display()
        assert item['file_path'].endswith(media_item.file.url)
        assert item['created_at'] == media_item.created_at.strftime('%d.%m.%Y %H:%M:%S')

    def test_media_item_does_not_exist(self, user_client):
        resp = user_client.get(reverse('core:media-retrieve', args=(999,)))
        assert resp.status_code == 404
        assert resp.json() == {'error': 'Media item not found'}

    def test_user_does_not_have_access(self, anonymous_client, url, media_item):
        resp = anonymous_client.get(url)
        print(media_item.owner_id)
        print(resp.json())
        assert resp.status_code == 404
        assert resp.json() == {'error': 'Media item not found'}
