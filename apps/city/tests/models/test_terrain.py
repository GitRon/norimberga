import pytest
from django.core.exceptions import ValidationError

from apps.city.tests.factories import TerrainFactory


# Terrain Model Tests
@pytest.mark.django_db
def test_terrain_str_representation():
    """Test __str__ method returns terrain name."""
    terrain = TerrainFactory(name="Forest")
    assert str(terrain) == "Forest"


@pytest.mark.django_db
def test_terrain_probability_validation_minimum():
    """Test probability cannot be less than 1."""
    terrain = TerrainFactory.build(probability=0)
    with pytest.raises(ValidationError) as exc_info:
        terrain.full_clean()
    assert "Ensure this value is greater than or equal to 1" in str(exc_info.value)


@pytest.mark.django_db
def test_terrain_probability_validation_maximum():
    """Test probability cannot be more than 100."""
    terrain = TerrainFactory.build(probability=101)
    with pytest.raises(ValidationError) as exc_info:
        terrain.full_clean()
    assert "Ensure this value is less than or equal to 100" in str(exc_info.value)


@pytest.mark.django_db
def test_terrain_valid_probability_range():
    """Test probability accepts valid values 1-100."""
    terrain = TerrainFactory(probability=50)
    terrain.full_clean()  # Should not raise
    assert terrain.probability == 50


@pytest.mark.django_db
def test_terrain_creation():
    """Test terrain creation with all fields."""
    terrain = TerrainFactory(name="Forest", image_filename="forest.png", probability=75)
    assert terrain.name == "Forest"
    assert terrain.image_filename == "forest.png"
    assert terrain.probability == 75
