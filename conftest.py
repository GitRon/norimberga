import pytest
from django.conf import settings


@pytest.fixture(scope="session", autouse=True)
def _fast_password_hasher(django_db_setup, django_db_blocker):
    """Use fast password hasher for all tests to speed up user creation."""
    with django_db_blocker.unblock():
        settings.PASSWORD_HASHERS = [
            "django.contrib.auth.hashers.MD5PasswordHasher",
        ]


@pytest.fixture
def client():
    """Provide Django test client."""
    from django.test import Client

    return Client()


@pytest.fixture
def request_factory():
    """Provide Django request factory."""
    from django.test import RequestFactory

    return RequestFactory()


@pytest.fixture
def user():
    """Provide a test user."""
    from apps.account.tests.factories import UserFactory

    return UserFactory(username="testuser")


@pytest.fixture
def authenticated_client(client, user):
    """Provide authenticated Django test client."""
    client.force_login(user)
    return client
