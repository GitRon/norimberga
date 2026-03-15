import pytest

from apps.city.services.siege.segment import WallSegment, WallSegmentService
from apps.city.tests.factories import BuildingFactory, TerrainFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_wall_segment_service_no_wall_tiles():
    """Test all segments are empty when no wall tiles exist."""
    savegame = SavegameFactory.create()

    result = WallSegmentService(savegame=savegame).process()

    assert set(result.keys()) == {"N", "S", "E", "W"}
    for seg in result.values():
        assert seg.tiles == []
        assert seg.total_hp == 0
        assert seg.total_max_hp == 0
        assert seg.hp_ratio == 0.0


@pytest.mark.django_db
def test_wall_segment_service_returns_wall_segment_dataclasses():
    """Test process returns WallSegment dataclasses for all directions."""
    savegame = SavegameFactory.create()

    result = WallSegmentService(savegame=savegame).process()

    for seg in result.values():
        assert isinstance(seg, WallSegment)


@pytest.mark.django_db
def test_wall_segment_service_classifies_north():
    """Test tile in upper half (y < 9.5) goes to North segment."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)

    # Tile at y=2 (clearly North)
    TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wall_building, wall_hitpoints=100)

    result = WallSegmentService(savegame=savegame).process()

    assert len(result["N"].tiles) == 1
    assert len(result["S"].tiles) == 0
    assert len(result["E"].tiles) == 0
    assert len(result["W"].tiles) == 0


@pytest.mark.django_db
def test_wall_segment_service_classifies_south():
    """Test tile in lower half (y > 9.5) goes to South segment."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)

    TileFactory.create(savegame=savegame, x=9, y=17, terrain=terrain, building=wall_building, wall_hitpoints=100)

    result = WallSegmentService(savegame=savegame).process()

    assert len(result["S"].tiles) == 1
    assert len(result["N"].tiles) == 0


@pytest.mark.django_db
def test_wall_segment_service_classifies_east():
    """Test tile with larger x-deviation goes to East segment."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)

    # x=18 → dx=8.5, y=10 → dy=0.5 → East (|dx| > |dy|)
    TileFactory.create(savegame=savegame, x=18, y=10, terrain=terrain, building=wall_building, wall_hitpoints=100)

    result = WallSegmentService(savegame=savegame).process()

    assert len(result["E"].tiles) == 1


@pytest.mark.django_db
def test_wall_segment_service_classifies_west():
    """Test tile with larger negative x-deviation goes to West segment."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)

    # x=1 → dx=-8.5, y=10 → dy=0.5 → West
    TileFactory.create(savegame=savegame, x=1, y=10, terrain=terrain, building=wall_building, wall_hitpoints=100)

    result = WallSegmentService(savegame=savegame).process()

    assert len(result["W"].tiles) == 1


@pytest.mark.django_db
def test_wall_segment_service_hp_ratio_calculation():
    """Test hp_ratio is calculated as total_hp / total_max_hp."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)

    # level=1 → max_hp=100, current=50 → ratio=0.5
    TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wall_building, wall_hitpoints=50)

    result = WallSegmentService(savegame=savegame).process()

    assert result["N"].total_hp == 50
    assert result["N"].total_max_hp == 100
    assert result["N"].hp_ratio == 0.5


@pytest.mark.django_db
def test_wall_segment_service_tie_goes_to_ns():
    """Test that ties between dx and dy go to N/S."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)

    # x=0 (dx=-9.5), y=0 (dy=-9.5) → tie → North (dy < 0)
    TileFactory.create(savegame=savegame, x=0, y=0, terrain=terrain, building=wall_building, wall_hitpoints=100)

    result = WallSegmentService(savegame=savegame).process()

    assert len(result["N"].tiles) == 1
    assert len(result["E"].tiles) == 0
    assert len(result["W"].tiles) == 0


@pytest.mark.django_db
def test_wall_segment_service_excludes_tiles_without_wall_hitpoints():
    """Test only tiles with wall_hitpoints set are included."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)

    # Tile without wall_hitpoints (no wall)
    TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wall_building, wall_hitpoints=None)

    result = WallSegmentService(savegame=savegame).process()

    for seg in result.values():
        assert seg.tiles == []


@pytest.mark.django_db
def test_wall_segment_service_multiple_tiles_same_direction():
    """Test multiple tiles in the same direction are all in that segment."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])

    # Use x=3..7, y=2 to ensure all tiles clearly go to North (abs(dy)>abs(dx))
    for x in range(3, 8):
        wall_building = BuildingFactory.create(building_type=wall_type, level=1)
        TileFactory.create(savegame=savegame, x=x, y=2, terrain=terrain, building=wall_building, wall_hitpoints=100)

    result = WallSegmentService(savegame=savegame).process()

    assert len(result["N"].tiles) == 5
    assert result["N"].total_hp == 500
    assert result["N"].total_max_hp == 500
    assert result["N"].hp_ratio == 1.0
