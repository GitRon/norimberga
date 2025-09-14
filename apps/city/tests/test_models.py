from unittest import mock

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    HouseBuildingTypeFactory,
    SavegameFactory,
    TerrainFactory,
    TileFactory,
    UniqueBuildingTypeFactory,
    WallBuildingTypeFactory,
)


# Savegame Model Tests
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
    savegame = SavegameFactory()
    assert hasattr(savegame, "savegames") is False  # Should not have reverse relation to itself


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
    terrain = TerrainFactory(name="Forest", color_class="bg-green-400", probability=75)
    assert terrain.name == "Forest"
    assert terrain.color_class == "bg-green-400"
    assert terrain.probability == 75


# BuildingType Model Tests
@pytest.mark.django_db
def test_building_type_str_representation():
    """Test __str__ method returns building type name."""
    building_type = BuildingTypeFactory(name="House")
    assert str(building_type) == "House"


@pytest.mark.django_db
def test_building_type_default_values():
    """Test building type creation with default values."""
    building_type = BuildingTypeFactory()
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
    wall_type = WallBuildingTypeFactory()
    assert wall_type.name == "Wall"
    assert wall_type.is_wall is True
    assert wall_type.is_city is True


@pytest.mark.django_db
def test_house_building_type():
    """Test house building type creation."""
    house_type = HouseBuildingTypeFactory()
    assert house_type.name == "House"
    assert house_type.is_house is True
    assert house_type.is_city is True


@pytest.mark.django_db
def test_unique_building_type():
    """Test unique building type creation."""
    unique_type = UniqueBuildingTypeFactory()
    assert unique_type.name == "Cathedral"
    assert unique_type.is_unique is True
    assert unique_type.is_city is True


# Building Model Tests
@pytest.mark.django_db
def test_building_str_representation():
    """Test __str__ method returns building name."""
    building = BuildingFactory(name="Test House")
    assert str(building) == "Test House"


@pytest.mark.django_db
def test_building_creation_with_all_fields():
    """Test building creation with all fields."""
    building_type = BuildingTypeFactory()
    building = BuildingFactory(
        name="Manor",
        building_type=building_type,
        level=2,
        taxes=20,
        building_costs=100,
        maintenance_costs=10,
        housing_space=4,
    )

    assert building.name == "Manor"
    assert building.building_type == building_type
    assert building.level == 2
    assert building.taxes == 20
    assert building.building_costs == 100
    assert building.maintenance_costs == 10
    assert building.housing_space == 4


@pytest.mark.django_db
def test_building_validator_minimum_values():
    """Test building validators prevent negative values."""
    # Test taxes validator
    building = BuildingFactory.build(taxes=-1)
    with pytest.raises(ValidationError) as exc_info:
        building.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)

    # Test building_costs validator
    building = BuildingFactory.build(building_costs=-1)
    with pytest.raises(ValidationError) as exc_info:
        building.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)

    # Test maintenance_costs validator
    building = BuildingFactory.build(maintenance_costs=-1)
    with pytest.raises(ValidationError) as exc_info:
        building.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)

    # Test housing_space validator
    building = BuildingFactory.build(housing_space=-1)
    with pytest.raises(ValidationError) as exc_info:
        building.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)


# Tile Model Tests
@pytest.mark.django_db
def test_tile_str_representation():
    """Test __str__ method returns coordinates."""
    tile = TileFactory(x=3, y=4)
    assert str(tile) == "3/4"


@pytest.mark.django_db
def test_tile_creation():
    """Test tile creation with all fields."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()
    building = BuildingFactory()

    tile = TileFactory(savegame=savegame, terrain=terrain, x=2, y=3, building=building)

    assert tile.savegame == savegame
    assert tile.terrain == terrain
    assert tile.x == 2
    assert tile.y == 3
    assert tile.building == building


@pytest.mark.django_db
def test_tile_unique_together_constraint():
    """Test tile unique_together constraint for savegame, x, y."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create first tile
    TileFactory(savegame=savegame, terrain=terrain, x=1, y=1)

    # Try to create second tile with same savegame and coordinates
    with pytest.raises(IntegrityError):
        TileFactory(savegame=savegame, terrain=terrain, x=1, y=1)


@pytest.mark.django_db
def test_tile_content_property_with_building():
    """Test content property returns building when present."""
    building = BuildingFactory()
    tile = TileFactory(building=building)

    assert tile.content == building


@pytest.mark.django_db
def test_tile_content_property_without_building():
    """Test content property returns terrain when no building."""
    terrain = TerrainFactory()
    tile = TileFactory(terrain=terrain, building=None)

    assert tile.content == terrain


@pytest.mark.django_db
def test_tile_color_class_with_wall_building():
    """Test color_class returns wall template for wall buildings."""
    wall_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_type)
    tile = TileFactory(building=building)

    with mock.patch("apps.city.models.render_to_string") as mock_render:
        mock_render.return_value = "wall-classes"
        result = tile.color_class()

        mock_render.assert_called_once_with("city/classes/_tile_city_wall.txt")
        assert result == "wall-classes"


@pytest.mark.django_db
def test_tile_color_class_with_both_building():
    """Test color_class returns both template for country+city buildings."""
    building_type = BuildingTypeFactory(is_country=True, is_city=True, is_wall=False)
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(building=building)

    with mock.patch("apps.city.models.render_to_string") as mock_render:
        mock_render.return_value = "both-classes"
        result = tile.color_class()

        mock_render.assert_called_once_with("city/classes/_tile_both.txt")
        assert result == "both-classes"


@pytest.mark.django_db
def test_tile_color_class_with_country_building():
    """Test color_class returns country template for country-only buildings."""
    building_type = BuildingTypeFactory(is_country=True, is_city=False, is_wall=False)
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(building=building)

    with mock.patch("apps.city.models.render_to_string") as mock_render:
        mock_render.return_value = "country-classes"
        result = tile.color_class()

        mock_render.assert_called_once_with("city/classes/_tile_country.txt")
        assert result == "country-classes"


@pytest.mark.django_db
def test_tile_color_class_with_city_building():
    """Test color_class returns city template for city-only buildings."""
    building_type = BuildingTypeFactory(is_country=False, is_city=True, is_wall=False)
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(building=building)

    with mock.patch("apps.city.models.render_to_string") as mock_render:
        mock_render.return_value = "city-classes"
        result = tile.color_class()

        mock_render.assert_called_once_with("city/classes/_tile_city.txt")
        assert result == "city-classes"


@pytest.mark.django_db
def test_tile_color_class_without_building():
    """Test color_class returns terrain color when no building."""
    terrain = TerrainFactory(color_class="bg-green-400")
    tile = TileFactory(terrain=terrain, building=None)

    result = tile.color_class()
    assert result == "bg-green-400"


@pytest.mark.django_db
def test_tile_is_adjacent_to_city_building_true():
    """Test is_adjacent_to_city_building returns True when adjacent city building exists."""
    savegame = SavegameFactory()
    city_building_type = BuildingTypeFactory(is_city=True)
    city_building = BuildingFactory(building_type=city_building_type)

    # Create tile with city building at adjacent coordinates
    TileFactory(savegame=savegame, x=0, y=0, building=city_building)

    # Create tile to test
    tile = TileFactory(savegame=savegame, x=1, y=1)

    # Mock the queryset chain to return True
    with mock.patch("apps.city.models.Tile.objects.filter_savegame") as mock_filter_savegame:
        mock_queryset = mock.Mock()
        mock_filter_savegame.return_value = mock_queryset
        mock_queryset.filter_adjacent_tiles.return_value = mock_queryset
        mock_queryset.filter_city_building.return_value = mock_queryset
        mock_queryset.exists.return_value = True

        result = tile.is_adjacent_to_city_building()

        assert result is True
        mock_filter_savegame.assert_called_once_with(savegame=savegame)
        mock_queryset.filter_adjacent_tiles.assert_called_once_with(tile=tile)
        mock_queryset.filter_city_building.assert_called_once()
        mock_queryset.exists.assert_called_once()


@pytest.mark.django_db
def test_tile_is_adjacent_to_city_building_false():
    """Test is_adjacent_to_city_building returns False when no adjacent city building exists."""
    savegame = SavegameFactory()
    tile = TileFactory(savegame=savegame, x=1, y=1)

    # Mock the queryset chain to return False
    with mock.patch("apps.city.models.Tile.objects.filter_savegame") as mock_filter_savegame:
        mock_queryset = mock.Mock()
        mock_filter_savegame.return_value = mock_queryset
        mock_queryset.filter_adjacent_tiles.return_value = mock_queryset
        mock_queryset.filter_city_building.return_value = mock_queryset
        mock_queryset.exists.return_value = False

        result = tile.is_adjacent_to_city_building()

        assert result is False
        mock_queryset.exists.assert_called_once()
