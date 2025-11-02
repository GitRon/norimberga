import pytest
from django.urls import reverse


# CityMapView Tests
@pytest.mark.django_db
def test_city_map_view_response(authenticated_client):
    """Test CityMapView responds correctly."""
    response = authenticated_client.get(reverse("city:city-map"))

    assert response.status_code == 200
    assert "city/partials/city/_city_map.html" in [t.name for t in response.templates]
