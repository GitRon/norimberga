import pytest
from django.test import RequestFactory

from apps.city.context_processors.savegame import get_current_savegame
from apps.city.tests.factories import SavegameFactory


@pytest.fixture
def request_factory():
    """Provide Django request factory."""
    return RequestFactory()


@pytest.mark.django_db
def test_get_current_savegame_returns_existing_savegame(request_factory):
    """Test get_current_savegame returns existing savegame."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame
    Savegame.objects.filter(id=1).delete()

    # Create existing savegame with id=1
    existing_savegame = SavegameFactory(id=1, city_name="Test City")

    request = request_factory.get('/')
    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] == existing_savegame
    assert result["savegame"].city_name == "Test City"


@pytest.mark.django_db
def test_get_current_savegame_creates_new_savegame(request_factory):
    """Test get_current_savegame creates new savegame if doesn't exist."""
    request = request_factory.get('/')
    result = get_current_savegame(request)

    assert "savegame" in result
    assert result["savegame"] is not None
    assert result["savegame"].id == 1


@pytest.mark.django_db
def test_get_current_savegame_consistent_results(request_factory):
    """Test get_current_savegame returns same savegame across calls."""
    request = request_factory.get('/')

    # First call should create savegame
    result1 = get_current_savegame(request)
    savegame1 = result1["savegame"]

    # Second call should return same savegame
    result2 = get_current_savegame(request)
    savegame2 = result2["savegame"]

    assert savegame1.id == savegame2.id
    assert savegame1 == savegame2


@pytest.mark.django_db
def test_get_current_savegame_request_type_independence(request_factory):
    """Test get_current_savegame works with different request types."""
    # Test with GET request
    get_request = request_factory.get('/')
    get_result = get_current_savegame(get_request)

    # Test with POST request
    post_request = request_factory.post('/')
    post_result = get_current_savegame(post_request)

    # Should return same savegame regardless of request type
    assert get_result["savegame"] == post_result["savegame"]


@pytest.mark.django_db
def test_get_current_savegame_return_structure(request_factory):
    """Test get_current_savegame returns correct dictionary structure."""
    request = request_factory.get('/')
    result = get_current_savegame(request)

    # Should be a dictionary with 'savegame' key
    assert isinstance(result, dict)
    assert len(result) == 1
    assert "savegame" in result

    # Value should be a Savegame instance
    from apps.city.models import Savegame
    assert isinstance(result["savegame"], Savegame)