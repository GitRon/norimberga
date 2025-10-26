from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.events.events.fire import Event as FireEvent
from apps.city.tests.factories import BuildingFactory, HouseBuildingTypeFactory, TileFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_fire_event_init():
    """Test FireEvent initialization and class attributes."""
    savegame = SavegameFactory(population=150)
    house_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=house_type)
    tile = TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 25

        event = FireEvent(savegame=savegame)

        assert event.PROBABILITY == 5
        assert event.LEVEL == messages.ERROR
        assert event.TITLE == "Fire"
        assert event.savegame.id == savegame.id
        assert event.initial_population == 150
        assert event.lost_population == 25
        assert event.affected_tile.id == tile.id


@pytest.mark.django_db
def test_fire_event_init_no_house():
    """Test FireEvent initialization when no houses exist."""
    savegame = SavegameFactory(population=100)

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 30

        event = FireEvent(savegame=savegame)

        assert event.affected_tile is None


@pytest.mark.django_db
def test_fire_event_init_creates_savegame():
    """Test FireEvent accepts a savegame parameter."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 20

        event = FireEvent(savegame=savegame)

        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_fire_event_get_probability_with_population():
    """Test get_probability returns base probability when population > 0."""
    savegame = SavegameFactory(population=80)

    event = FireEvent(savegame=savegame)

    probability = event.get_probability()

    assert probability == 5


@pytest.mark.django_db
def test_fire_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(population=0)

    event = FireEvent(savegame=savegame)

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_fire_event_prepare_effect_decrease_population():
    """Test _prepare_effect_decrease_population returns correct effect."""
    savegame = SavegameFactory(population=100)

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 35

        event = FireEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_population()

        assert isinstance(effect, DecreasePopulationAbsolute)
        assert effect.lost_population == 35


@pytest.mark.django_db
def test_fire_event_prepare_effect_remove_building_with_house():
    """Test _prepare_effect_remove_building returns effect when house exists."""
    savegame = SavegameFactory(population=100)
    house_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=house_type)
    tile = TileFactory(savegame=savegame, building=building)

    event = FireEvent(savegame=savegame)
    effect = event._prepare_effect_remove_building()

    assert isinstance(effect, RemoveBuilding)
    assert effect.tile.id == tile.id


@pytest.mark.django_db
def test_fire_event_prepare_effect_remove_building_no_house():
    """Test _prepare_effect_remove_building returns None when no house exists."""
    savegame = SavegameFactory(population=100)

    event = FireEvent(savegame=savegame)

    effect = event._prepare_effect_remove_building()

    assert effect is None


@pytest.mark.django_db
def test_fire_event_get_verbose_text_with_building():
    """Test get_verbose_text returns correct description with building."""
    savegame = SavegameFactory(population=120)
    house_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=house_type)
    tile = TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 20

        event = FireEvent(savegame=savegame)
        initial_population = event.initial_population

        # Simulate effect processing (decrease population)
        savegame.population = max(savegame.population - 20, 0)
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Due to general neglect, a fire raged throughout the city, killing "
            f"{initial_population - savegame.population} citizens."
            f" The fire started in the building {tile} and destroyed it completely."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_fire_event_get_verbose_text_no_building():
    """Test get_verbose_text returns correct description without building."""
    savegame = SavegameFactory(population=80)

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 15

        event = FireEvent(savegame=savegame)
        initial_population = event.initial_population

        # Simulate effect processing (decrease population)
        savegame.population = max(savegame.population - 15, 0)
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Due to general neglect, a fire raged throughout the city, killing "
            f"{initial_population - savegame.population} citizens."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_fire_event_get_effects_with_building():
    """Test get_effects returns both effects when house exists."""
    savegame = SavegameFactory(population=100)
    house_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=house_type)
    TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 25

        event = FireEvent(savegame=savegame)
        effects = event.get_effects()

        assert len(effects) == 2
        population_effect = next(e for e in effects if isinstance(e, DecreasePopulationAbsolute))
        building_effect = next(e for e in effects if isinstance(e, RemoveBuilding))

        assert population_effect.lost_population == 25
        assert building_effect.tile.building.id == building.id


@pytest.mark.django_db
def test_fire_event_get_effects_no_building():
    """Test get_effects returns population effect and None when no house exists."""
    savegame = SavegameFactory(population=100)

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 30

        event = FireEvent(savegame=savegame)
        effects = event.get_effects()

        # Should have 2 effects: population effect and None (for building)
        assert len(effects) == 2

        # Filter out None effects like process() does
        valid_effects = [e for e in effects if e is not None]
        assert len(valid_effects) == 1
        assert isinstance(valid_effects[0], DecreasePopulationAbsolute)
        assert valid_effects[0].lost_population == 30


@pytest.mark.django_db
def test_fire_event_process(ruins_building):
    """Test full event processing workflow."""
    savegame = SavegameFactory(population=100)
    house_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=house_type)
    tile = TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.fire.random.randint") as mock_randint:
        mock_randint.return_value = 20

        event = FireEvent(savegame=savegame)
        result_text = event.process()

        # Verify population effect was applied
        savegame.refresh_from_db()
        assert savegame.population == 80  # 100 - 20 = 80

        # Verify building was replaced with ruins
        tile.refresh_from_db()
        assert tile.building is not None
        assert tile.building == ruins_building
        assert tile.building.name == "Ruins"

        # Verify result text is returned
        assert "Due to general neglect, a fire raged throughout the city" in result_text
        assert "killing 20 citizens" in result_text
        assert "destroyed it completely" in result_text
