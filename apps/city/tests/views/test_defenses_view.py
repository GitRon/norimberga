import pytest
from django.urls import reverse

from apps.savegame.tests.factories import SavegameFactory


# DefensesView Tests
@pytest.mark.django_db
def test_defenses_view_response(authenticated_client, user):
    """Test DefensesView responds correctly and includes breakdown in context."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:defenses"))

    assert response.status_code == 200
    assert "city/defenses.html" in [t.name for t in response.templates]
    assert "breakdown" in response.context


@pytest.mark.django_db
def test_defenses_view_with_savegame(authenticated_client, user):
    """Test DefensesView includes defense breakdown when savegame exists."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:defenses"))

    assert response.status_code == 200
    assert "breakdown" in response.context
    breakdown = response.context["breakdown"]
    # Verify breakdown has expected attributes (from DefenseBreakdown dataclass)
    assert hasattr(breakdown, "is_enclosed")
    assert hasattr(breakdown, "base_defense")
    assert hasattr(breakdown, "shape_bonus")
    assert hasattr(breakdown, "spike_malus")
    assert hasattr(breakdown, "potential_total")
    assert hasattr(breakdown, "actual_total")


@pytest.mark.django_db
def test_defenses_view_without_savegame(authenticated_client, user):
    """Test DefensesView redirects when no active savegame exists."""
    # Don't create a savegame for this user
    response = authenticated_client.get(reverse("city:defenses"))

    # View should redirect to savegame list (SavegameRequiredMixin behavior)
    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"
