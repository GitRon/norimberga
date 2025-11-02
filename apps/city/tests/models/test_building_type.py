import pytest

from apps.city.tests.factories import (
    BuildingTypeFactory,
    HouseBuildingTypeFactory,
    TerrainFactory,
    UniqueBuildingTypeFactory,
    WallBuildingTypeFactory,
)


# BuildingType Model Tests
@pytest.mark.django_db
def test_building_type_str_representation():
    """Test __str__ method returns building type name."""
    building_type = BuildingTypeFactory(name="House")
    assert str(building_type) == "House"


@pytest.mark.django_db
def test_building_type_default_values():
    """Test building type creation with default values."""
    building_type = BuildingTypeFactory.create()
    assert building_type.is_country is False
    assert building_type.is_city is True
    assert building_type.is_house is False
    assert building_type.is_wall is False
    assert building_type.is_unique is False


@pytest.mark.django_db
def test_building_type_with_allowed_terrains():
    """Test building type with allowed terrains."""
    terrain1 = TerrainFactory(name="Grass")
    terrain2 = TerrainFactory(name="Forest")
    building_type = BuildingTypeFactory(allowed_terrains=[terrain1, terrain2])

    assert building_type.allowed_terrains.count() == 2
    assert terrain1 in building_type.allowed_terrains.all()
    assert terrain2 in building_type.allowed_terrains.all()


@pytest.mark.django_db
def test_wall_building_type():
    """Test wall building type creation."""
    wall_type = WallBuildingTypeFactory.create()
    assert wall_type.name == "Wall"
    assert wall_type.is_wall is True
    assert wall_type.is_city is True


@pytest.mark.django_db
def test_house_building_type():
    """Test house building type creation."""
    house_type = HouseBuildingTypeFactory.create()
    assert house_type.name == "House"
    assert house_type.is_house is True
    assert house_type.is_city is True


@pytest.mark.django_db
def test_unique_building_type():
    """Test unique building type creation."""
    unique_type = UniqueBuildingTypeFactory.create()
    assert unique_type.name == "Cathedral"
    assert unique_type.is_unique is True
    assert unique_type.is_city is True
