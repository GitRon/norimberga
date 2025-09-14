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
def test_remove_building_process_removes_building():
    """Test process removes building from tile."""
    building = BuildingFactory()
    tile = TileFactory(building=building)
    effect = RemoveBuilding(tile=tile)

    # Verify building is initially present
    assert tile.building == building

    effect.process()

    tile.refresh_from_db()
    assert tile.building is None


@pytest.mark.django_db
def test_remove_building_process_already_empty_tile():
    """Test process handles tile that already has no building."""
    tile = TileFactory(building=None)
    effect = RemoveBuilding(tile=tile)

    # Verify tile has no building initially
    assert tile.building is None

    effect.process()

    tile.refresh_from_db()
    assert tile.building is None  # Should remain None


@pytest.mark.django_db
def test_remove_building_process_saves_tile():
    """Test process saves the tile after removing building."""
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
    # Verify building was actually removed from database
    tile.refresh_from_db()
    assert tile.building is None
