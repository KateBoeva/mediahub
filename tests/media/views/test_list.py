import pytest
from django.core.files.base import ContentFile

from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe

from core.models import MediaItem
from core.schemas.media import MediaItemDetailItem


@pytest.mark.django_db
class TestMediaItemListView:
    media_item_recipe = Recipe(MediaItem, file=ContentFile(b"fake data", name="test.jpg"))

    @pytest.fixture
    def media_item(self):
        return self.media_item_recipe.make()

    def test_ok(self, user_client, media_item):
        media_item.owner = user_client.user
        media_item.save()

        resp = user_client.get(reverse('core:media-list'))

        assert resp.status_code == 200
        data = resp.json()
        item = data['items'][0]
        assert len(data['items']) == 1
        assert len(item) == len(MediaItemDetailItem.__pydantic_fields__)
        assert item['id'] == media_item.id
        assert item['title'] == media_item.title
        assert item['description'] == media_item.description
        assert item['media_type'] == media_item.get_media_type_display()
        assert item['file_path'].endswith(media_item.file.url)
        assert item['created_at'] == media_item.created_at.strftime('%d.%m.%Y %H:%M:%S')

    def test_ok_empty_items(self, user_client):
        user = baker.make('core.User')
        self.media_item_recipe.make(_quantity=3, owner_id=user.id)
        resp = user_client.get(reverse('core:media-list'))
        assert resp.status_code == 200
        assert resp.json() == {'items': []}

    def test_anonymous(self, anonymous_client, media_item):
        resp = anonymous_client.get(reverse('core:media-list'))
        assert resp.status_code == 200
        assert resp.json() == {'items': []}
