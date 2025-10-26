from unittest import mock

import pytest

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.events.events.riot import Event as RiotEvent
from apps.city.tests.factories import BuildingFactory, BuildingTypeFactory, TileFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_riot_event_init():
    """Test RiotEvent initialization and class attributes."""
    savegame = SavegameFactory.create(population=100, unrest=75)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 1]  # population loss %, demolition count

        event = RiotEvent(savegame=savegame)

        assert event.PROBABILITY == 100
        assert event.TITLE == "Riots"
        assert event.savegame.id == savegame.id
        assert event.initial_population == 100
        assert event.lost_population == 8  # ceil((7/100) * 100) = 8 due to floating point precision
        assert event.demolished_buildings_count == 1


@pytest.mark.django_db
def test_riot_event_init_accepts_savegame():
    """Test RiotEvent accepts a savegame parameter."""
    savegame = SavegameFactory.create(unrest=80)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [8, 0]

        event = RiotEvent(savegame=savegame)

        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_riot_event_lost_population_calculation():
    """Test lost_population calculation with different percentages."""
    savegame = SavegameFactory.create(population=200, unrest=75)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [6, 0]

        event = RiotEvent(savegame=savegame)

        # ceil((6/100) * 200) = ceil(12) = 12
        assert event.lost_population == 12


@pytest.mark.django_db
def test_riot_event_lost_population_small_population():
    """Test lost_population calculation with small population."""
    savegame = SavegameFactory.create(population=10, unrest=90)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [5, 1]

        event = RiotEvent(savegame=savegame)

        # ceil((5/100) * 10) = ceil(0.5) = 1
        assert event.lost_population == 1


@pytest.mark.django_db
def test_riot_event_get_probability_unrest_below_threshold():
    """Test get_probability returns 0 when unrest is below 75."""
    savegame = SavegameFactory.create(population=100, unrest=50)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 0]

        event = RiotEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_riot_event_get_probability_unrest_at_threshold():
    """Test get_probability when unrest is exactly 75."""
    savegame = SavegameFactory.create(population=100, unrest=75)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 0]

        event = RiotEvent(savegame=savegame)
        probability = event.get_probability()

        # 100 * 75 / 100 = 75
        assert probability == 75


@pytest.mark.django_db
def test_riot_event_get_probability_high_unrest():
    """Test get_probability calculation with high unrest."""
    savegame = SavegameFactory.create(population=100, unrest=80)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 0]

        event = RiotEvent(savegame=savegame)
        probability = event.get_probability()

        # 100 * 80 / 100 = 80
        assert probability == 80


@pytest.mark.django_db
def test_riot_event_get_probability_zero_unrest():
    """Test get_probability returns 0 when unrest is zero."""
    savegame = SavegameFactory.create(population=100, unrest=0)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 0]

        event = RiotEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_riot_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory.create(population=0, unrest=80)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 0]

        event = RiotEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_riot_event_prepare_effect_decrease_population():
    """Test _prepare_effect_decrease_population returns correct effect."""
    savegame = SavegameFactory.create(population=150, unrest=75)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [8, 0]

        event = RiotEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_population()

        assert isinstance(effect, DecreasePopulationAbsolute)
        assert effect.lost_population == 12  # ceil((8/100) * 150) = 12


@pytest.mark.django_db
def test_riot_event_get_verbose_text_no_buildings():
    """Test get_verbose_text returns correct description without buildings."""
    savegame = SavegameFactory.create(population=100, unrest=85)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [6, 0]

        event = RiotEvent(savegame=savegame)
        initial_population = event.initial_population

        # Simulate effect processing (decrease population)
        lost_population = event.lost_population
        savegame.population = savegame.population - lost_population
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            "The people have enough! Outraged mobs started fights in the streets which lead to the loss of "
            f"{initial_population - savegame.population} human lives."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_riot_event_random_range():
    """Test that random.randint is called with correct ranges."""
    savegame = SavegameFactory.create(population=100, unrest=75)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 1]

        RiotEvent(savegame=savegame)

        assert mock_randint.call_count == 2
        mock_randint.assert_any_call(5, 10)
        mock_randint.assert_any_call(0, 2)


@pytest.mark.django_db
def test_riot_event_fractional_calculation():
    """Test lost_population handles fractional calculations correctly."""
    savegame = SavegameFactory.create(population=33, unrest=75)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [5, 0]

        event = RiotEvent(savegame=savegame)

        # ceil((5/100) * 33) = ceil(1.65) = 2
        assert event.lost_population == 2


@pytest.mark.django_db
def test_riot_event_get_affected_tiles_no_buildings():
    """Test _get_affected_tiles returns empty list when no buildings exist."""
    savegame = SavegameFactory.create(population=100, unrest=75)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 2]

        event = RiotEvent(savegame=savegame)

        assert event.demolished_buildings_count == 2
        assert event.affected_tiles == []


@pytest.mark.django_db
def test_riot_event_get_affected_tiles_with_non_unique_buildings():
    """Test _get_affected_tiles returns non-unique buildings."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    building1 = BuildingFactory.create(building_type=building_type)
    building2 = BuildingFactory.create(building_type=building_type)
    tile1 = TileFactory.create(savegame=savegame, building=building1)
    tile2 = TileFactory.create(savegame=savegame, building=building2)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 2]

        event = RiotEvent(savegame=savegame)

        assert event.demolished_buildings_count == 2
        assert len(event.affected_tiles) == 2
        assert tile1 in event.affected_tiles
        assert tile2 in event.affected_tiles


@pytest.mark.django_db
def test_riot_event_get_affected_tiles_excludes_unique_buildings():
    """Test _get_affected_tiles excludes unique buildings."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    unique_building_type = BuildingTypeFactory.create(is_unique=True)
    non_unique_building_type = BuildingTypeFactory.create(is_unique=False)
    unique_building = BuildingFactory.create(building_type=unique_building_type)
    non_unique_building = BuildingFactory.create(building_type=non_unique_building_type)
    TileFactory.create(savegame=savegame, building=unique_building)
    tile_non_unique = TileFactory.create(savegame=savegame, building=non_unique_building)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 2]

        event = RiotEvent(savegame=savegame)

        assert event.demolished_buildings_count == 2
        assert len(event.affected_tiles) == 1
        assert tile_non_unique in event.affected_tiles


@pytest.mark.django_db
def test_riot_event_get_affected_tiles_limited_by_count():
    """Test _get_affected_tiles limits results to demolished_buildings_count."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    buildings = BuildingFactory.create_batch(5, building_type=building_type)
    for building in buildings:
        TileFactory.create(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 1]

        event = RiotEvent(savegame=savegame)

        assert event.demolished_buildings_count == 1
        assert len(event.affected_tiles) == 1


@pytest.mark.django_db
def test_riot_event_prepare_effect_remove_building_0_with_building():
    """Test _prepare_effect_remove_building_0 returns effect when building available."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    building = BuildingFactory.create(building_type=building_type)
    tile = TileFactory.create(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 1]

        event = RiotEvent(savegame=savegame)
        effect = event._prepare_effect_remove_building_0()

        assert isinstance(effect, RemoveBuilding)
        assert effect.tile.id == tile.id


@pytest.mark.django_db
def test_riot_event_prepare_effect_remove_building_0_no_building():
    """Test _prepare_effect_remove_building_0 returns None when no building available."""
    savegame = SavegameFactory.create(population=100, unrest=75)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 1]

        event = RiotEvent(savegame=savegame)
        effect = event._prepare_effect_remove_building_0()

        assert effect is None


@pytest.mark.django_db
def test_riot_event_prepare_effect_remove_building_1_with_two_buildings():
    """Test _prepare_effect_remove_building_1 returns effect when second building available."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    building1 = BuildingFactory.create(building_type=building_type)
    building2 = BuildingFactory.create(building_type=building_type)
    tile1 = TileFactory.create(savegame=savegame, building=building1)
    tile2 = TileFactory.create(savegame=savegame, building=building2)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 2]

        event = RiotEvent(savegame=savegame)
        effect = event._prepare_effect_remove_building_1()

        assert isinstance(effect, RemoveBuilding)
        assert effect.tile.id in [tile1.id, tile2.id]


@pytest.mark.django_db
def test_riot_event_prepare_effect_remove_building_1_with_one_building():
    """Test _prepare_effect_remove_building_1 returns None when only one building available."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    building = BuildingFactory.create(building_type=building_type)
    TileFactory.create(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 2]

        event = RiotEvent(savegame=savegame)
        effect = event._prepare_effect_remove_building_1()

        assert effect is None


@pytest.mark.django_db
def test_riot_event_prepare_effect_remove_building_2_with_three_buildings():
    """Test _prepare_effect_remove_building_2 returns effect when third building available.

    Note: In normal game logic, this scenario cannot occur because random.randint(0, 2)
    limits demolished_buildings_count to at most 2, meaning affected_tiles can only
    contain 0-2 tiles. We manually override affected_tiles here to test the code path.
    """
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    buildings = BuildingFactory.create_batch(3, building_type=building_type)
    tiles = [TileFactory.create(savegame=savegame, building=building) for building in buildings]

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 2]

        event = RiotEvent(savegame=savegame)

        # Manually override affected_tiles to test the edge case where 3 buildings are affected
        event.affected_tiles = tiles

        effect = event._prepare_effect_remove_building_2()

        assert isinstance(effect, RemoveBuilding)
        assert effect.tile.id in [tile.id for tile in tiles]


@pytest.mark.django_db
def test_riot_event_prepare_effect_remove_building_2_returns_none():
    """Test _prepare_effect_remove_building_2 returns None when only two buildings can be demolished."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    buildings = BuildingFactory.create_batch(3, building_type=building_type)
    for building in buildings:
        TileFactory.create(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [7, 2]

        event = RiotEvent(savegame=savegame)
        effect = event._prepare_effect_remove_building_2()

        # Only 0-2 buildings can be demolished, so index 2 (third building) should return None
        assert effect is None


@pytest.mark.django_db
def test_riot_event_get_verbose_text_with_one_building():
    """Test get_verbose_text returns correct description with one demolished building."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    building = BuildingFactory.create(building_type=building_type)
    TileFactory.create(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [6, 1]

        event = RiotEvent(savegame=savegame)
        initial_population = event.initial_population

        # Simulate effect processing (decrease population)
        lost_population = event.lost_population
        savegame.population = savegame.population - lost_population
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            "The people have enough! Outraged mobs started fights in the streets which lead to the loss of "
            f"{initial_population - savegame.population} human lives."
            " During the riots, 1 building was destroyed."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_riot_event_get_verbose_text_with_two_buildings():
    """Test get_verbose_text returns correct description with two demolished buildings."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    buildings = BuildingFactory.create_batch(2, building_type=building_type)
    for building in buildings:
        TileFactory.create(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [6, 2]

        event = RiotEvent(savegame=savegame)
        initial_population = event.initial_population

        # Simulate effect processing (decrease population)
        lost_population = event.lost_population
        savegame.population = savegame.population - lost_population
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            "The people have enough! Outraged mobs started fights in the streets which lead to the loss of "
            f"{initial_population - savegame.population} human lives."
            " During the riots, 2 buildings were destroyed."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_riot_event_process_full_workflow(ruins_building):
    """Test full event processing workflow with building demolition."""
    savegame = SavegameFactory.create(population=100, unrest=75)
    building_type = BuildingTypeFactory.create(is_unique=False)
    building = BuildingFactory.create(building_type=building_type)
    tile = TileFactory.create(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [6, 1]

        event = RiotEvent(savegame=savegame)
        result_text = event.process()

        # Verify population effect was applied
        savegame.refresh_from_db()
        assert savegame.population == 94  # 100 - 6 = 94

        # Verify building was replaced with ruins
        tile.refresh_from_db()
        assert tile.building is not None
        assert tile.building == ruins_building
        assert tile.building.name == "Ruins"

        # Verify result text is returned
        assert "The people have enough! Outraged mobs started fights in the streets" in result_text
        assert "6 human lives" in result_text
        assert "1 building was destroyed" in result_text


@pytest.mark.django_db
def test_riot_event_process_with_no_buildings():
    """Test full event processing workflow without buildings."""
    savegame = SavegameFactory.create(population=100, unrest=80)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.side_effect = [8, 0]

        event = RiotEvent(savegame=savegame)
        result_text = event.process()

        # Verify population effect was applied
        savegame.refresh_from_db()
        assert savegame.population == 92  # 100 - 8 = 92

        # Verify result text is returned
        assert "The people have enough! Outraged mobs started fights in the streets" in result_text
        assert "8 human lives" in result_text
        assert "building" not in result_text.split("human lives.")[1]
