import pytest

from apps.city.events.effects.building.damage_wall import DamageWall
from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory


@pytest.mark.django_db
def test_damage_wall_init():
    """Test DamageWall initialization."""
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(building=building, wall_hitpoints=100)
    effect = DamageWall(tile=tile, damage=30)

    assert effect.tile == tile
    assert effect.damage == 30


@pytest.mark.django_db
def test_damage_wall_process_reduces_hitpoints():
    """Test process reduces wall_hitpoints by damage amount."""
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(building=building, wall_hitpoints=100)

    DamageWall(tile=tile, damage=30).process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints == 70


@pytest.mark.django_db
def test_damage_wall_process_clamps_to_zero(ruins_building):
    """Test process clamps hitpoints to 0 and converts to ruins when damage exceeds HP."""
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(building=building, wall_hitpoints=20)

    DamageWall(tile=tile, damage=50).process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints is None
    assert tile.building.building_type.type == tile.building.building_type.Type.RUINS


@pytest.mark.django_db
def test_damage_wall_process_converts_to_ruins_at_zero(ruins_building):
    """Test process converts wall to ruins when hitpoints reach exactly 0."""
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(building=building, wall_hitpoints=30)

    DamageWall(tile=tile, damage=30).process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints is None
    assert tile.building.building_type.type == tile.building.building_type.Type.RUINS


@pytest.mark.django_db
def test_damage_wall_process_does_nothing_when_no_hitpoints():
    """Test process does nothing when wall_hitpoints is None."""
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(building=building, wall_hitpoints=None)

    DamageWall(tile=tile, damage=30).process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints is None
    assert tile.building == building
