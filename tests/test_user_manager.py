import pytest

from django.test.client import Client

from core.models import User


@pytest.mark.django_db
class TestUserManager:
    def test_create_superuser(self):
        user = User.objects.create_superuser('admin@test.ru', 'testpass')

        assert user.is_active
        assert user.is_superuser
        assert user.is_staff

    def test_superuser_can_login(self):
        user = User.objects.create_superuser('admin@test.ru', 'testpass')

        assert Client().login(username=user.email, password='testpass')

    def test_create_user_is_inactive(self):
        user = User.objects.create_user('user@test.ru', 'testpass')

        assert not user.is_active
