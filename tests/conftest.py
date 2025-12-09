import pytest

from django.conf import settings
from django.test.client import Client

from core.models import User



@pytest.fixture
def plain_user():
    user = User.objects.create(
        is_active=True,
        email='test_email@test.ru'
    )
    user.set_password('testpass')
    user.save()

    return user


@pytest.fixture
def user_client(plain_user):
    client = Client()
    client.login(username=plain_user.email, password='testpass')
    client.user = plain_user

    return client


@pytest.fixture
def anonymous_client(plain_user):
    return Client()


# фикстура для изменения папки медиа файлов на временную в тестах
@pytest.fixture(autouse=True)
def temp_media_dir(tmp_path):
    temp_dir = tmp_path / "media"
    temp_dir.mkdir()
    settings.MEDIA_ROOT = temp_dir
    yield
