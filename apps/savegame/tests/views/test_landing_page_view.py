import pytest
from django.urls import reverse

from apps.savegame.models import Savegame
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_landing_page_view_redirects_to_savegame_list_when_no_active_savegame(authenticated_client, user):
    """Test LandingPageView redirects to savegame list when user has no active savegame."""
    Savegame.objects.filter(user=user).update(is_active=False)

    response = authenticated_client.get(reverse("city:landing-page"), follow=False)

    assert response.status_code == 302
    assert response.url == reverse("savegame:savegame-list")


@pytest.mark.django_db
def test_landing_page_view_displays_when_user_has_active_savegame(authenticated_client, user):
    """Test LandingPageView displays when user has an active savegame."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:landing-page"))

    assert response.status_code == 200
    assert "city/landing_page.html" in [t.name for t in response.templates]
