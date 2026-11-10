from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from core.models import AuthToken, User
from core.services.auth import AuthService
from tests.files import JPEG_BYTES

STRONG_PASSWORD = 'S3cure-pass-42'


def bearer_client(token, **kwargs):
    return Client(headers={'Authorization': f'Bearer {token}'}, **kwargs)


@pytest.mark.django_db
class TestRegisterView:
    @pytest.fixture
    def url(self):
        return reverse('core:auth-register')

    @pytest.fixture
    def payload(self):
        return {'email': 'new_user@test.ru', 'password': STRONG_PASSWORD}

    def test_ok(self, url, payload):
        resp = Client().post(url, data=payload)

        assert resp.status_code == 201
        user = User.objects.get(email=payload['email'])
        assert user.is_active
        assert user.check_password(payload['password'])

        media_resp = bearer_client(resp.json()['token']).get(reverse('core:media-list'))
        assert media_resp.status_code == 200

    def test_token_is_stored_hashed(self, url, payload):
        token = Client().post(url, data=payload).json()['token']

        stored = AuthToken.objects.get()
        assert stored.token_hash != token
        assert len(stored.token_hash) == 64

    def test_duplicate_email(self, url, payload, plain_user):
        payload['email'] = plain_user.email
        resp = Client().post(url, data=payload)

        assert resp.status_code == 409
        assert User.objects.count() == 1

    @pytest.mark.parametrize('email', ['', 'not-an-email', f'{"x" * 250}@test.ru'])
    def test_invalid_email(self, url, payload, email):
        payload['email'] = email
        resp = Client().post(url, data=payload)

        assert resp.status_code == 400
        assert User.objects.count() == 0

    @pytest.mark.parametrize('password', ['', '123', 'password', 'x' * 129])
    def test_weak_password(self, url, payload, password):
        payload['password'] = password
        resp = Client().post(url, data=payload)

        assert resp.status_code == 400
        assert User.objects.count() == 0

    def test_password_not_echoed_in_errors(self, url, payload):
        payload['password'] = '123'
        resp = Client().post(url, data=payload)

        assert resp.json()['errors'][0]['loc'] == ['password']
        assert 'input' not in resp.json()['errors'][0]


@pytest.mark.django_db
class TestLoginView:
    @pytest.fixture
    def url(self):
        return reverse('core:auth-login')

    def test_ok(self, url, plain_user):
        resp = Client().post(url, data={'email': plain_user.email, 'password': 'testpass'})

        assert resp.status_code == 200
        media_resp = bearer_client(resp.json()['token']).get(reverse('core:media-list'))
        assert media_resp.status_code == 200

    def test_each_login_issues_new_token(self, url, plain_user):
        data = {'email': plain_user.email, 'password': 'testpass'}

        assert Client().post(url, data=data).json()['token'] != Client().post(url, data=data).json()['token']

    def test_wrong_password(self, url, plain_user):
        resp = Client().post(url, data={'email': plain_user.email, 'password': 'wrong'})

        assert resp.status_code == 401
        assert resp.json() == {'error': 'Invalid email or password'}

    def test_unknown_user(self, url):
        resp = Client().post(url, data={'email': 'nobody@test.ru', 'password': 'testpass'})

        assert resp.status_code == 401
        assert resp.json() == {'error': 'Invalid email or password'}

    def test_inactive_user(self, url, plain_user):
        plain_user.is_active = False
        plain_user.save()
        resp = Client().post(url, data={'email': plain_user.email, 'password': 'testpass'})

        assert resp.status_code == 401

    def test_missing_password(self, url, plain_user):
        resp = Client().post(url, data={'email': plain_user.email})

        assert resp.status_code == 400

    @staticmethod
    def fail_logins(url, email, times, ip='127.0.0.1'):
        for _ in range(times):
            resp = Client(REMOTE_ADDR=ip).post(url, data={'email': email, 'password': 'wrong'})
            assert resp.status_code == 401

    def test_too_many_failures_blocks_even_correct_password(self, url, plain_user, settings):
        self.fail_logins(url, plain_user.email, settings.LOGIN_FAILURE_LIMIT)

        resp = Client().post(url, data={'email': plain_user.email, 'password': 'testpass'})

        assert resp.status_code == 429
        assert resp.json() == {'error': 'Too many login attempts, try again later'}
        assert resp['Retry-After'] == str(int(settings.LOGIN_FAILURE_WINDOW.total_seconds()))

    def test_email_case_does_not_bypass_limit(self, url, plain_user, settings):
        self.fail_logins(url, plain_user.email.upper(), settings.LOGIN_FAILURE_LIMIT)

        resp = Client().post(url, data={'email': plain_user.email, 'password': 'testpass'})

        assert resp.status_code == 429

    def test_successful_login_resets_counter(self, url, plain_user, settings):
        self.fail_logins(url, plain_user.email, settings.LOGIN_FAILURE_LIMIT - 1)
        assert Client().post(url, data={'email': plain_user.email, 'password': 'testpass'}).status_code == 200

        self.fail_logins(url, plain_user.email, settings.LOGIN_FAILURE_LIMIT - 1)
        assert Client().post(url, data={'email': plain_user.email, 'password': 'testpass'}).status_code == 200

    def test_other_ip_is_not_blocked(self, url, plain_user, settings):
        self.fail_logins(url, plain_user.email, settings.LOGIN_FAILURE_LIMIT, ip='10.0.0.1')

        resp = Client(REMOTE_ADDR='10.0.0.2').post(url, data={'email': plain_user.email, 'password': 'testpass'})

        assert resp.status_code == 200

    def test_ip_limit_across_emails(self, url, plain_user, settings):
        settings.LOGIN_FAILURE_IP_LIMIT = 3
        for i in range(settings.LOGIN_FAILURE_IP_LIMIT):
            self.fail_logins(url, f'user{i}@test.ru', 1)

        resp = Client().post(url, data={'email': plain_user.email, 'password': 'testpass'})

        assert resp.status_code == 429


@pytest.mark.django_db
class TestLogoutView:
    @pytest.fixture
    def url(self):
        return reverse('core:auth-logout')

    def test_ok_revokes_token(self, url, user_client):
        resp = user_client.post(url)

        assert resp.status_code == 204
        assert user_client.get(reverse('core:media-list')).status_code == 401

    def test_other_tokens_stay_valid(self, url, user_client, plain_user):
        other_token = AuthService().create_token(plain_user.id)['token']

        user_client.post(url)

        assert bearer_client(other_token).get(reverse('core:media-list')).status_code == 200

    def test_anonymous(self, url, anonymous_client):
        assert anonymous_client.post(url).status_code == 401


@pytest.mark.django_db
class TestTokenAuthentication:
    @pytest.fixture
    def url(self):
        return reverse('core:media-list')

    @pytest.mark.parametrize('header', ['Token abc', 'Bearer', 'Bearer ', 'Bearer wrong', 'abc'])
    def test_invalid_header(self, url, header, plain_user):
        resp = Client(headers={'Authorization': header}).get(url)

        assert resp.status_code == 401
        assert resp['WWW-Authenticate'] == 'Bearer'

    def test_expired_token(self, url, user_client):
        AuthToken.objects.update(expires_at=timezone.now() - timedelta(seconds=1))

        assert user_client.get(url).status_code == 401

    def test_inactive_user(self, url, user_client, plain_user):
        plain_user.is_active = False
        plain_user.save()

        assert user_client.get(url).status_code == 401

    def test_session_cookie_is_not_accepted(self, url, plain_user):
        client = Client()
        client.force_login(plain_user)

        assert client.get(url).status_code == 401

    def test_token_request_does_not_need_csrf(self, plain_user):
        token = AuthService().create_token(plain_user.id)['token']
        resp = bearer_client(token, enforce_csrf_checks=True).post(reverse('core:media-create'), data={
            'title': 'Title',
            'media_type': 1,
            'file': SimpleUploadedFile('a.jpg', JPEG_BYTES),
        })

        assert resp.status_code == 201

    @pytest.mark.parametrize('name', ['core:auth-register', 'core:auth-login'])
    def test_public_endpoints_do_not_need_csrf(self, name):
        resp = Client(enforce_csrf_checks=True).post(reverse(name), data={})

        assert resp.status_code == 400
