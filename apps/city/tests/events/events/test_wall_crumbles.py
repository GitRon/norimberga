from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.events.wall_crumbles import Event as WallCrumblesEvent
from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_wall_crumbles_event_class_attributes():
    """Test WallCrumbles event has correct class attributes."""
    savegame = SavegameFactory.create()
    event = WallCrumblesEvent(savegame=savegame)

    assert event.PROBABILITY == 20
    assert event.LEVEL == messages.WARNING
    assert event.TITLE == "Wall Crumbles"


@pytest.mark.django_db
def test_wall_crumbles_event_init_selects_wall_tiles():
    """Test event selects wall tiles with hitpoints."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    with (
        mock.patch("apps.city.events.events.wall_crumbles.random.randint") as mock_randint,
        mock.patch("apps.city.events.events.wall_crumbles.random.sample") as mock_sample,
    ):
        mock_randint.return_value = 40
        mock_sample.return_value = []  # return value doesn't matter for this test

        event = WallCrumblesEvent(savegame=savegame)

        assert event.damage_per_tile == 40


@pytest.mark.django_db
def test_wall_crumbles_event_probability_zero_without_walls():
    """Test get_probability returns 0 when there are no wall tiles."""
    savegame = SavegameFactory.create()
    event = WallCrumblesEvent(savegame=savegame)

    assert event.get_probability() == 0


@pytest.mark.django_db
def test_wall_crumbles_event_probability_nonzero_with_walls():
    """Test get_probability returns PROBABILITY when wall tiles exist."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    event = WallCrumblesEvent(savegame=savegame)

    assert event.get_probability() == 20


@pytest.mark.django_db
def test_wall_crumbles_event_get_effects_returns_damage_effects():
    """Test get_effects returns DamageWall effects for affected tiles."""
    from apps.city.events.effects.building.damage_wall import DamageWall

    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    with (
        mock.patch("apps.city.events.events.wall_crumbles.random.randint") as mock_randint,
        mock.patch("apps.city.events.events.wall_crumbles.random.sample") as mock_sample,
    ):
        mock_randint.return_value = 40
        mock_sample.return_value = [tile]

        event = WallCrumblesEvent(savegame=savegame)
        effects = event.get_effects()

    assert len(effects) == 1
    assert isinstance(effects[0], DamageWall)
    assert effects[0].tile == tile
    assert effects[0].damage == 40


@pytest.mark.django_db
def test_wall_crumbles_event_get_effects_empty_when_no_walls():
    """Test get_effects returns empty list when no wall tiles exist."""
    savegame = SavegameFactory.create()
    event = WallCrumblesEvent(savegame=savegame)

    effects = event.get_effects()

    assert effects == []


@pytest.mark.django_db
def test_wall_crumbles_event_process(ruins_building):
    """Test full event processing applies damage to affected wall tile."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    with (
        mock.patch("apps.city.events.events.wall_crumbles.random.randint") as mock_randint,
        mock.patch("apps.city.events.events.wall_crumbles.random.sample") as mock_sample,
    ):
        mock_randint.return_value = 40
        mock_sample.side_effect = lambda population, k: population[:k]

        event = WallCrumblesEvent(savegame=savegame)
        event.process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints == 60


@pytest.mark.django_db
def test_wall_crumbles_event_get_verbose_text():
    """Test get_verbose_text returns message with count and damage."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    with (
        mock.patch("apps.city.events.events.wall_crumbles.random.randint") as mock_randint,
        mock.patch("apps.city.events.events.wall_crumbles.random.sample") as mock_sample,
    ):
        mock_randint.return_value = 40
        mock_sample.return_value = [tile]

        event = WallCrumblesEvent(savegame=savegame)

    text = event.get_verbose_text()
    assert "40" in text
    assert "1 wall section" in text
