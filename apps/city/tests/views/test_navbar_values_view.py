import pytest
from django.urls import reverse

from apps.savegame.tests.factories import SavegameFactory


# NavbarValuesView Tests
@pytest.mark.django_db
def test_navbar_values_view_response(authenticated_client, user):
    """Test NavbarValuesView returns correct template."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:navbar-values"))

    assert response.status_code == 200
    assert "partials/_navbar_values.html" in [t.name for t in response.templates]
