import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from django.urls import reverse
from model_bakery.recipe import Recipe

from core.models import MediaItem
from core.models.media_item import MediaType
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

    def test_other_owner(self, user_client, url):
        resp = user_client.get(url)
        assert resp.status_code == 404
        assert resp.json() == {'error': 'Media item not found'}

    def test_anonymous(self, anonymous_client, url):
        resp = anonymous_client.get(url)
        assert resp.status_code == 401


@pytest.mark.django_db
class TestMediaItemUpdateView:
    media_item_recipe = Recipe(MediaItem, file=ContentFile(b"fake data", name="test.jpg"))

    @pytest.fixture
    def media_item(self, user_client):
        return self.media_item_recipe.make(owner=user_client.user, media_type=MediaType.IMAGE)

    @pytest.fixture
    def url(self, media_item):
        return reverse('core:media-retrieve', args=(media_item.id,))

    @pytest.fixture
    def payload(self):
        return {
            'title': 'Updated Media',
            'description': 'Updated Description',
            'media_type': MediaType.VIDEO.value,
        }

    def test_ok_without_file(self, user_client, url, payload, media_item):
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 200
        item = resp.json()
        assert item['title'] == payload['title']
        assert item['description'] == payload['description']
        assert item['media_type'] == MediaType.VIDEO.label
        assert item['file_path'].endswith(media_item.file.url)

    def test_ok_with_file(self, user_client, url, payload):
        payload['file'] = SimpleUploadedFile("updated.jpg", b"updated data")
        resp = user_client.post(url, data=payload)

        assert resp.status_code == 200
        assert resp.json()['file_path'].endswith('updated.jpg')

    def test_invalid_data(self, user_client, url, payload):
        del payload['title']
        resp = user_client.post(url, data=payload)
        assert resp.status_code == 400

    def test_other_owner(self, user_client, payload):
        other_item = self.media_item_recipe.make()
        resp = user_client.post(reverse('core:media-retrieve', args=(other_item.id,)), data=payload)

        assert resp.status_code == 404
        other_item.refresh_from_db()
        assert other_item.title != payload['title']

    def test_anonymous(self, anonymous_client, url, payload):
        resp = anonymous_client.post(url, data=payload)
        assert resp.status_code == 401


@pytest.mark.django_db
class TestMediaItemDeleteView:
    media_item_recipe = Recipe(MediaItem, file=ContentFile(b"fake data", name="test.jpg"))

    @pytest.fixture
    def media_item(self, user_client):
        return self.media_item_recipe.make(owner=user_client.user)

    @pytest.fixture
    def url(self, media_item):
        return reverse('core:media-retrieve', args=(media_item.id,))

    def test_ok(self, user_client, url, media_item):
        resp = user_client.delete(url)

        assert resp.status_code == 204
        assert not MediaItem.objects.filter(id=media_item.id).exists()

    def test_does_not_exist(self, user_client):
        resp = user_client.delete(reverse('core:media-retrieve', args=(999,)))
        assert resp.status_code == 404

    def test_other_owner(self, user_client):
        other_item = self.media_item_recipe.make()
        resp = user_client.delete(reverse('core:media-retrieve', args=(other_item.id,)))

        assert resp.status_code == 404
        assert MediaItem.objects.filter(id=other_item.id).exists()

    def test_anonymous(self, anonymous_client, url, media_item):
        resp = anonymous_client.delete(url)

        assert resp.status_code == 401
        assert MediaItem.objects.filter(id=media_item.id).exists()
