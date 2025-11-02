import pytest
from django.core.exceptions import ValidationError

from apps.savegame.tests.factories import SavegameFactory


# Savegame Model Tests
@pytest.mark.django_db
def test_savegame_str_representation():
    """Test __str__ method returns city name."""
    savegame = SavegameFactory(city_name="Test City")
    assert str(savegame) == "Test City"


@pytest.mark.django_db
def test_savegame_creation_with_defaults():
    """Test savegame creation with default values."""
    savegame = SavegameFactory.create()

    assert savegame.coins == 1000
    assert savegame.population == 50
    assert savegame.current_year == 1150
    assert savegame.is_active is True


@pytest.mark.django_db
def test_savegame_unrest_validation_minimum():
    """Test unrest cannot be less than 0."""
    savegame = SavegameFactory.build(unrest=-1)
    with pytest.raises(ValidationError) as exc_info:
        savegame.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)


@pytest.mark.django_db
def test_savegame_unrest_validation_maximum():
    """Test unrest cannot be more than 100."""
    savegame = SavegameFactory.build(unrest=101)
    with pytest.raises(ValidationError) as exc_info:
        savegame.full_clean()
    assert "Ensure this value is less than or equal to 100" in str(exc_info.value)


@pytest.mark.django_db
def test_savegame_unrest_valid_range():
    """Test unrest accepts valid values 0-100."""
    savegame = SavegameFactory(unrest=50)
    savegame.full_clean()  # Should not raise
    assert savegame.unrest == 50


@pytest.mark.django_db
def test_savegame_default_related_name():
    """Test savegame uses correct related name."""
    savegame = SavegameFactory.create()
    assert hasattr(savegame, "savegames") is False  # Should not have reverse relation to itself
