from unittest import mock

import pytest
from django.db import IntegrityError

from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TerrainFactory,
    TileFactory,
    WallBuildingTypeFactory,
)
from apps.savegame.tests.factories import SavegameFactory


# Tile Model Tests
@pytest.mark.django_db
def test_tile_str_representation():
    """Test __str__ method returns coordinates."""
    tile = TileFactory(x=3, y=4)
    assert str(tile) == "3/4"


@pytest.mark.django_db
def test_tile_creation():
    """Test tile creation with all fields."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    building = BuildingFactory.create()

    tile = TileFactory(savegame=savegame, terrain=terrain, x=2, y=3, building=building)

    assert tile.savegame == savegame
    assert tile.terrain == terrain
    assert tile.x == 2
    assert tile.y == 3
    assert tile.building == building


@pytest.mark.django_db
def test_tile_unique_together_constraint():
    """Test tile unique_together constraint for savegame, x, y."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create first tile
    TileFactory(savegame=savegame, terrain=terrain, x=1, y=1)

    # Try to create second tile with same savegame and coordinates
    with pytest.raises(IntegrityError):
        TileFactory(savegame=savegame, terrain=terrain, x=1, y=1)


@pytest.mark.django_db
def test_tile_content_property_with_building():
    """Test content property returns building when present."""
    building = BuildingFactory.create()
    tile = TileFactory(building=building)

    assert tile.content == building


@pytest.mark.django_db
def test_tile_content_property_without_building():
    """Test content property returns terrain when no building."""
    terrain = TerrainFactory.create()
    tile = TileFactory(terrain=terrain, building=None)

    assert tile.content == terrain


@pytest.mark.django_db
def test_tile_color_class_with_wall_building():
    """Test color_class returns wall template for wall buildings."""
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory(building_type=wall_type)
    tile = TileFactory(building=building)

    with mock.patch("apps.city.models.tile.render_to_string") as mock_render:
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

    with mock.patch("apps.city.models.tile.render_to_string") as mock_render:
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

    with mock.patch("apps.city.models.tile.render_to_string") as mock_render:
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

    with mock.patch("apps.city.models.tile.render_to_string") as mock_render:
        mock_render.return_value = "city-classes"
        result = tile.color_class()

        mock_render.assert_called_once_with("city/classes/_tile_city.txt")
        assert result == "city-classes"


@pytest.mark.django_db
def test_tile_color_class_without_building():
    """Test color_class returns empty string when no building (terrain uses images now)."""
    terrain = TerrainFactory(image_filename="grass.png")
    tile = TileFactory(terrain=terrain, building=None)

    result = tile.color_class()
    assert result == ""


@pytest.mark.django_db
def test_tile_terrain_image_url():
    """Test terrain_image_url returns correct static path."""
    terrain = TerrainFactory(image_filename="grass.png")
    tile = TileFactory(terrain=terrain, building=None)

    result = tile.terrain_image_url()
    assert result == "/static/img/tiles/grass.png"


@pytest.mark.django_db
def test_tile_is_adjacent_to_city_building_delegates_to_manager():
    """Test is_adjacent_to_city_building delegates to manager method."""
    tile = TileFactory.create()

    # Mock the manager method
    with mock.patch("apps.city.models.Tile.objects.has_adjacent_city_building") as mock_manager_method:
        mock_manager_method.return_value = True

        result = tile.is_adjacent_to_city_building()

        assert result is True
        mock_manager_method.assert_called_once_with(tile=tile)


@pytest.mark.django_db
def test_tile_is_edge_tile_corners():
    """Test is_edge_tile returns True for corner tiles."""
    savegame = SavegameFactory.create()

    # Test all four corners (20x20 map has coordinates 0-19)
    tile_top_left = TileFactory(savegame=savegame, x=0, y=0)
    tile_top_right = TileFactory(savegame=savegame, x=19, y=0)
    tile_bottom_left = TileFactory(savegame=savegame, x=0, y=19)
    tile_bottom_right = TileFactory(savegame=savegame, x=19, y=19)

    assert tile_top_left.is_edge_tile() is True
    assert tile_top_right.is_edge_tile() is True
    assert tile_bottom_left.is_edge_tile() is True
    assert tile_bottom_right.is_edge_tile() is True


@pytest.mark.django_db
def test_tile_is_edge_tile_edges():
    """Test is_edge_tile returns True for tiles on edges."""
    savegame = SavegameFactory.create()

    # Test tiles on each edge (20x20 map has coordinates 0-19)
    tile_top = TileFactory(savegame=savegame, x=10, y=0)
    tile_bottom = TileFactory(savegame=savegame, x=10, y=19)
    tile_left = TileFactory(savegame=savegame, x=0, y=10)
    tile_right = TileFactory(savegame=savegame, x=19, y=10)

    assert tile_top.is_edge_tile() is True
    assert tile_bottom.is_edge_tile() is True
    assert tile_left.is_edge_tile() is True
    assert tile_right.is_edge_tile() is True


@pytest.mark.django_db
def test_tile_is_edge_tile_center():
    """Test is_edge_tile returns False for non-edge tiles."""
    savegame = SavegameFactory.create()

    # Test center tiles
    tile_center = TileFactory(savegame=savegame, x=2, y=2)
    tile_inner = TileFactory(savegame=savegame, x=1, y=1)
    tile_inner2 = TileFactory(savegame=savegame, x=3, y=3)

    assert tile_center.is_edge_tile() is False
    assert tile_inner.is_edge_tile() is False
    assert tile_inner2.is_edge_tile() is False
