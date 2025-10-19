import pytest

from apps.savegame.context_processors.savegame import get_current_savegame
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_get_current_savegame_returns_existing_savegame(request_factory, user):
    """Test get_current_savegame returns existing active savegame for authenticated user."""
    existing_savegame = SavegameFactory(user=user, city_name="Test City", is_active=True, is_enclosed=True)

    request = request_factory.get("/")
    request.user = user

    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] == existing_savegame
    assert result["savegame"].city_name == "Test City"
    assert "is_enclosed" in result
    assert result["is_enclosed"] is True
    assert "max_housing_space" in result
    assert isinstance(result["max_housing_space"], int)


@pytest.mark.django_db
def test_get_current_savegame_returns_none_when_no_savegame(request_factory, user):
    """Test get_current_savegame returns None if user has no savegame."""
    request = request_factory.get("/")
    request.user = user

    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] is None
    assert "is_enclosed" in result
    assert result["is_enclosed"] is False
    assert "max_housing_space" in result
    assert result["max_housing_space"] == 0


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

    # Should be a dictionary with 'savegame', 'is_enclosed', and 'max_housing_space' keys
    assert isinstance(result, dict)
    assert len(result) == 3
    assert "savegame" in result
    assert "is_enclosed" in result
    assert "max_housing_space" in result

    # Value should be None when no savegame exists
    assert result["savegame"] is None
    assert result["is_enclosed"] is False
    assert result["max_housing_space"] == 0


def test_get_current_savegame_returns_none_for_unauthenticated_user(request_factory):
    """Test get_current_savegame returns None for unauthenticated user."""
    from django.contrib.auth.models import AnonymousUser

    request = request_factory.get("/")
    request.user = AnonymousUser()

    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] is None
    assert "is_enclosed" in result
    assert result["is_enclosed"] is False
    assert "max_housing_space" in result
    assert result["max_housing_space"] == 0


def test_get_current_savegame_returns_none_when_no_user_attribute(request_factory):
    """Test get_current_savegame returns None when request has no user attribute."""
    request = request_factory.get("/")

    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] is None
    assert "is_enclosed" in result
    assert result["is_enclosed"] is False
    assert "max_housing_space" in result
    assert result["max_housing_space"] == 0
