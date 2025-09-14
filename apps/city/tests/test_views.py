import pytest
from django.test import Client

from apps.city.tests.factories import SavegameFactory


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.mark.django_db
def test_city_index_view_requires_active_savegame(client):
    """Test city index view redirects when no active savegame exists."""
    response = client.get("/")
    # Add appropriate assertion based on the actual behavior
    # This is a placeholder test structure


@pytest.mark.django_db
def test_city_index_view_with_active_savegame(client):
    """Test city index view renders with active savegame."""
    savegame = SavegameFactory(is_active=True)
    response = client.get("/")
    # Add appropriate assertions based on the actual view behavior
    # This is a placeholder test structure