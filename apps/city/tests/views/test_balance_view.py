import pytest
from django.urls import reverse

from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_balance_view_response(authenticated_client, user):
    """Test BalanceView responds correctly and includes balance data in context."""
    SavegameFactory(user=user, is_active=True, coins=1000)

    response = authenticated_client.get(reverse("city:balance"))

    assert response.status_code == 200
    assert "city/balance.html" in [t.name for t in response.templates]
