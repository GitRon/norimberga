import pytest

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.tests.factories import BuildingFactory, TileFactory


@pytest.mark.django_db
def test_remove_building_init():
    """Test RemoveBuilding initialization with tile parameter."""
    tile = TileFactory()
    effect = RemoveBuilding(tile=tile)

    assert effect.tile == tile


@pytest.mark.django_db
def test_remove_building_process_replaces_with_ruins(ruins_building):
    """Test process replaces building with ruins instead of removing it."""
    building = BuildingFactory()
    tile = TileFactory(building=building)
    effect = RemoveBuilding(tile=tile)

    # Verify building is initially present
    assert tile.building == building

    effect.process()

    tile.refresh_from_db()
    # Building should be replaced with ruins, not removed entirely
    assert tile.building is not None
    assert tile.building == ruins_building
    assert tile.building.name == "Ruins"
    assert tile.building.pk == 28


@pytest.mark.django_db
def test_remove_building_process_already_empty_tile(ruins_building):
    """Test process replaces empty tile with ruins."""
    tile = TileFactory(building=None)
    effect = RemoveBuilding(tile=tile)

    # Verify tile has no building initially
    assert tile.building is None

    effect.process()

    tile.refresh_from_db()
    # Empty tile should also get ruins
    assert tile.building is not None
    assert tile.building == ruins_building
    assert tile.building.name == "Ruins"


@pytest.mark.django_db
def test_remove_building_process_saves_tile(ruins_building):
    """Test process saves the tile after replacing with ruins."""
    building = BuildingFactory()
    tile = TileFactory(building=building)
    effect = RemoveBuilding(tile=tile)

    # Mock save to verify it's called
    original_save = tile.save
    save_called = []

    def mock_save(*args, **kwargs):
        save_called.append(True)
        return original_save(*args, **kwargs)

    tile.save = mock_save

    effect.process()

    # Verify save was called
    assert len(save_called) == 1
    # Verify building was actually replaced with ruins in database
    tile.refresh_from_db()
    assert tile.building is not None
    assert tile.building == ruins_building
