import pytest
from django.urls import reverse

from apps.savegame.tests.factories import SavegameFactory


# LandingPageView Tests
@pytest.mark.django_db
def test_landing_page_view_response(authenticated_client, user):
    """Test LandingPageView responds correctly."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:landing-page"))

    assert response.status_code == 200
    assert "city/landing_page.html" in [t.name for t in response.templates]
