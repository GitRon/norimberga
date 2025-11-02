import pytest
from django.urls import reverse


# CityMessagesView Tests
@pytest.mark.django_db
def test_city_messages_view_response(authenticated_client):
    """Test CityMessagesView responds correctly."""
    response = authenticated_client.get(reverse("city:city-messages"))

    assert response.status_code == 200
    assert "city/partials/city/_messages.html" in [t.name for t in response.templates]
