from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.events.harsh_winter import Event as HarshWinterEvent
from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_harsh_winter_event_class_attributes():
    """Test HarshWinter event has correct class attributes."""
    savegame = SavegameFactory.create()
    event = HarshWinterEvent(savegame=savegame)

    assert event.PROBABILITY == 15
    assert event.LEVEL == messages.WARNING
    assert event.TITLE == "Harsh Winter"


@pytest.mark.django_db
def test_harsh_winter_event_init_collects_all_wall_tiles():
    """Test event collects all wall tiles with hitpoints."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile1 = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)
    tile2 = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=80)

    with mock.patch("apps.city.events.events.harsh_winter.random.randint", return_value=15):
        event = HarshWinterEvent(savegame=savegame)

    assert event.damage == 15
    tile_ids = {t.id for t in event.wall_tiles}
    assert tile1.id in tile_ids
    assert tile2.id in tile_ids


@pytest.mark.django_db
def test_harsh_winter_event_init_ignores_tiles_without_hitpoints():
    """Test event ignores wall tiles with wall_hitpoints=None."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=None)

    with mock.patch("apps.city.events.events.harsh_winter.random.randint", return_value=15):
        event = HarshWinterEvent(savegame=savegame)

    assert len(event.wall_tiles) == 0


@pytest.mark.django_db
def test_harsh_winter_event_get_effects_returns_damage_for_all_tiles():
    """Test get_effects returns one DamageWall per wall tile."""
    from apps.city.events.effects.building.damage_wall import DamageWall

    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=80)

    with mock.patch("apps.city.events.events.harsh_winter.random.randint", return_value=15):
        event = HarshWinterEvent(savegame=savegame)

    effects = event.get_effects()

    assert len(effects) == 2
    assert all(isinstance(e, DamageWall) for e in effects)
    assert all(e.damage == 15 for e in effects)


@pytest.mark.django_db
def test_harsh_winter_event_process(ruins_building):
    """Test full event processing reduces HP on all wall tiles."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile1 = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)
    tile2 = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=50)

    with mock.patch("apps.city.events.events.harsh_winter.random.randint", return_value=15):
        event = HarshWinterEvent(savegame=savegame)
        event.process()

    tile1.refresh_from_db()
    tile2.refresh_from_db()
    assert tile1.wall_hitpoints == 85
    assert tile2.wall_hitpoints == 35


@pytest.mark.django_db
def test_harsh_winter_event_get_probability_zero_without_walls():
    """Test get_probability returns 0 when no wall tiles exist."""
    savegame = SavegameFactory.create()
    event = HarshWinterEvent(savegame=savegame)

    assert event.get_probability() == 0


@pytest.mark.django_db
def test_harsh_winter_event_get_probability_nonzero_with_walls():
    """Test get_probability returns PROBABILITY when wall tiles exist."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    event = HarshWinterEvent(savegame=savegame)

    assert event.get_probability() == 15


@pytest.mark.django_db
def test_harsh_winter_event_get_verbose_text():
    """Test get_verbose_text returns informative message."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    with mock.patch("apps.city.events.events.harsh_winter.random.randint", return_value=15):
        event = HarshWinterEvent(savegame=savegame)

    text = event.get_verbose_text()
    assert "15" in text
    assert "1 wall section" in text
