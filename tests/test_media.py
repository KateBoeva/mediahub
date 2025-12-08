import pytest

from model_bakery import baker

from core.models import MediaItem


@pytest.mark.django_db
class TestMediaListView:
    def test_ok(self):
        baker.make('core.MediaItem')

        assert len(MediaItem.objects.all()) == 1
