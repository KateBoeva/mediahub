import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from model_bakery.recipe import Recipe
from pydantic import ValidationError

from core.models import MediaItem
from core.models.media_item import MediaType
from core.repos.media import MediaItemRepo
from core.schemas.media import MediaItemCreateItem, MediaItemUpdateItem


@pytest.mark.django_db
class TestMediaItemRepo:
    media_item_recipe = Recipe(MediaItem, file=ContentFile(b"fake data", name="test.jpg"))

    @pytest.fixture
    def media_item(self):
        return self.media_item_recipe.make()

    @pytest.fixture
    def repo(self):
        return MediaItemRepo()

    def test_list(self, repo, plain_user):
        quantity = 3
        media_items = self.media_item_recipe.make(_quantity=quantity, owner_id=plain_user.id)

        items = repo.list(user_id=plain_user.id)
        assert len(items) == quantity
        assert sorted([item.id for item in items]) == sorted([item.id for item in media_items])

    def test_list_empty(self, repo, plain_user):
        items = repo.list(user_id=plain_user.id)
        assert len(items) == 0

    def test_get_by_id(self, repo, media_item):
        item = repo.get_by_id(media_id=media_item.id, owner_id=media_item.owner_id)
        assert item is not None
        assert item.id == media_item.id

    def test_get_by_id_not_found(self, repo):
        item = repo.get_by_id(media_id=999, owner_id=1)
        assert item is None

    def test_get_by_id_other_owner(self, repo, media_item, plain_user):
        item = repo.get_by_id(media_id=media_item.id, owner_id=plain_user.id)
        assert item is None

    def test_update(self, repo, media_item):
        init = MediaItemUpdateItem(title='Updated', description='Updated desc', media_type=MediaType.VIDEO)
        item = repo.update(media_id=media_item.id, owner_id=media_item.owner_id, init=init, file=None)

        assert item.title == 'Updated'
        assert item.description == 'Updated desc'
        assert item.media_type == MediaType.VIDEO
        assert item.file.name == media_item.file.name

    def test_update_with_file(self, repo, media_item):
        init = MediaItemUpdateItem(title='Updated', media_type=MediaType.IMAGE)
        file = SimpleUploadedFile("updated.jpg", b"updated data")
        item = repo.update(media_id=media_item.id, owner_id=media_item.owner_id, init=init, file=file)

        assert item.file.name.endswith('updated.jpg')

    def test_update_other_owner(self, repo, media_item, plain_user):
        init = MediaItemUpdateItem(title='Updated', media_type=MediaType.IMAGE)
        item = repo.update(media_id=media_item.id, owner_id=plain_user.id, init=init, file=None)

        assert item is None
        media_item.refresh_from_db()
        assert media_item.title != 'Updated'

    def test_delete(self, repo, media_item):
        assert repo.delete(media_id=media_item.id, owner_id=media_item.owner_id) is True
        assert not MediaItem.objects.filter(id=media_item.id).exists()

    def test_delete_other_owner(self, repo, media_item, plain_user):
        assert repo.delete(media_id=media_item.id, owner_id=plain_user.id) is False
        assert MediaItem.objects.filter(id=media_item.id).exists()

    def test_create(self, repo, plain_user):
        init = {
            'title': 'Test Media',
            'description': 'Test Description',
            'media_type': MediaType.IMAGE.value,
        }

        file = SimpleUploadedFile("test.jpg", b"fake data")
        item = repo.create(init=MediaItemCreateItem(**init), file=file, owner_id=plain_user.id)
        assert item is not None
        assert item.id is not None
        assert item.title == init['title']
        assert item.description == init['description']
        assert item.media_type == init['media_type']
        assert item.owner_id == plain_user.id

    def test_create_invalid_data(self, repo, plain_user):
        init = {
            'description': 'Test Description',
            'media_type': 999,
        }

        file = SimpleUploadedFile("test.jpg", b"fake data")

        with pytest.raises(ValidationError):
            repo.create(init=MediaItemCreateItem(**init), file=file, owner_id=plain_user.id)
