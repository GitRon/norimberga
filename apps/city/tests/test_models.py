import pytest
from django.core.exceptions import ValidationError

from apps.city.tests.factories import SavegameFactory, TerrainFactory


@pytest.mark.django_db
def test_savegame_str_representation():
    """Test __str__ method returns city name."""
    savegame = SavegameFactory(city_name="Test City")
    assert str(savegame) == "Test City"


@pytest.mark.django_db
def test_savegame_creation_with_defaults():
    """Test savegame creation with default values."""
    savegame = SavegameFactory()
    assert savegame.map_size == 5
    assert savegame.coins == 100
    assert savegame.population == 50
    assert savegame.current_year == 1150
    assert savegame.is_active is True


@pytest.mark.django_db
def test_savegame_unrest_validation_minimum():
    """Test unrest cannot be less than 0."""
    savegame = SavegameFactory.build(unrest=-1)
    with pytest.raises(ValidationError):
        savegame.full_clean()


@pytest.mark.django_db
def test_savegame_unrest_validation_maximum():
    """Test unrest cannot be more than 100."""
    savegame = SavegameFactory.build(unrest=101)
    with pytest.raises(ValidationError):
        savegame.full_clean()


@pytest.mark.django_db
def test_savegame_unrest_valid_range():
    """Test unrest accepts valid values 0-100."""
    savegame = SavegameFactory(unrest=50)
    savegame.full_clean()  # Should not raise
    assert savegame.unrest == 50


@pytest.mark.django_db
def test_terrain_str_representation():
    """Test __str__ method returns terrain name."""
    terrain = TerrainFactory(name="Forest")
    assert str(terrain) == "Forest"


@pytest.mark.django_db
def test_terrain_probability_validation_minimum():
    """Test probability cannot be less than 1."""
    terrain = TerrainFactory.build(probability=0)
    with pytest.raises(ValidationError):
        terrain.full_clean()


@pytest.mark.django_db
def test_terrain_probability_validation_maximum():
    """Test probability cannot be more than 100."""
    terrain = TerrainFactory.build(probability=101)
    with pytest.raises(ValidationError):
        terrain.full_clean()


@pytest.mark.django_db
def test_terrain_valid_probability_range():
    """Test probability accepts valid values 1-100."""
    terrain = TerrainFactory(probability=50)
    terrain.full_clean()  # Should not raise
    assert terrain.probability == 50