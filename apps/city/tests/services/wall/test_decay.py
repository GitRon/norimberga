import pytest

from apps.city.services.wall.decay import WallDecayService
from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_wall_decay_service_reduces_all_wall_tiles():
    """Test decay reduces hitpoints on all wall tiles."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile1 = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)
    tile2 = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=80)

    WallDecayService(savegame=savegame).process()

    tile1.refresh_from_db()
    tile2.refresh_from_db()
    assert tile1.wall_hitpoints == 90
    assert tile2.wall_hitpoints == 70


@pytest.mark.django_db
def test_wall_decay_service_skips_non_wall_tiles():
    """Test decay does not affect tiles without wall buildings."""
    from apps.city.tests.factories import BuildingTypeFactory

    savegame = SavegameFactory.create()
    city_type = BuildingTypeFactory.create(is_city=True, is_wall=False)
    city_building = BuildingFactory.create(building_type=city_type)
    tile = TileFactory.create(savegame=savegame, building=city_building, wall_hitpoints=None)

    WallDecayService(savegame=savegame).process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints is None


@pytest.mark.django_db
def test_wall_decay_service_converts_to_ruins_at_zero(ruins_building):
    """Test decay converts wall to ruins when HP reaches 0."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=5)

    WallDecayService(savegame=savegame).process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints is None
    assert tile.building.building_type.type == tile.building.building_type.Type.RUINS


@pytest.mark.django_db
def test_wall_decay_service_no_wall_tiles():
    """Test decay does nothing when there are no wall tiles."""
    savegame = SavegameFactory.create()

    # Should not raise
    WallDecayService(savegame=savegame).process()


@pytest.mark.django_db
def test_wall_decay_service_skips_wall_tiles_without_hitpoints():
    """Test decay skips wall tiles where wall_hitpoints is None."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=None)

    WallDecayService(savegame=savegame).process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints is None
