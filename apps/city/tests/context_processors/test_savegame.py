import pytest

from apps.city.context_processors.savegame import get_current_savegame
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_get_current_savegame_returns_existing_savegame(request_factory, user):
    """Test get_current_savegame returns existing active savegame for authenticated user."""
    existing_savegame = SavegameFactory(user=user, city_name="Test City", is_active=True)

    request = request_factory.get("/")
    request.user = user

    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] == existing_savegame
    assert result["savegame"].city_name == "Test City"


@pytest.mark.django_db
def test_get_current_savegame_returns_none_when_no_savegame(request_factory, user):
    """Test get_current_savegame returns None if user has no savegame."""
    request = request_factory.get("/")
    request.user = user

    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] is None


@pytest.mark.django_db
def test_get_current_savegame_consistent_results(request_factory, user):
    """Test get_current_savegame returns same savegame across calls for same user."""
    savegame = SavegameFactory(user=user, is_active=True)

    request = request_factory.get("/")
    request.user = user

    # First call should return savegame
    result1 = get_current_savegame(request)
    savegame1 = result1["savegame"]

    # Second call should return same savegame
    result2 = get_current_savegame(request)
    savegame2 = result2["savegame"]

    assert savegame1.id == savegame2.id
    assert savegame1 == savegame2
    assert savegame1 == savegame


@pytest.mark.django_db
def test_get_current_savegame_return_structure(request_factory, user):
    """Test get_current_savegame returns correct dictionary structure."""
    request = request_factory.get("/")
    request.user = user

    result = get_current_savegame(request)

    # Should be a dictionary with 'savegame' key
    assert isinstance(result, dict)
    assert len(result) == 1
    assert "savegame" in result

    # Value should be None when no savegame exists
    assert result["savegame"] is None


def test_get_current_savegame_returns_none_for_unauthenticated_user(request_factory):
    """Test get_current_savegame returns None for unauthenticated user."""
    from django.contrib.auth.models import AnonymousUser

    request = request_factory.get("/")
    request.user = AnonymousUser()

    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] is None


def test_get_current_savegame_returns_none_when_no_user_attribute(request_factory):
    """Test get_current_savegame returns None when request has no user attribute."""
    request = request_factory.get("/")

    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] is None
