from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.events.events.pillage import Event as PillageEvent
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TileFactory,
    WallBuildingTypeFactory,
)
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_pillage_event_init():
    """Test PillageEvent initialization and class attributes."""
    savegame = SavegameFactory(coins=1000, population=100, is_enclosed=False)
    building_type = BuildingTypeFactory(is_city=True)
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [20, 10, 20]  # 20% coins, 10% population, 20% buildings

        event = PillageEvent(savegame=savegame)

        assert event.PROBABILITY == 30
        assert event.LEVEL == messages.ERROR
        assert event.TITLE == "Pillage"
        assert event.savegame.id == savegame.id
        assert event.initial_coins == 1000
        assert event.lost_coins == 200  # 20% of 1000
        assert event.lost_population == 10  # 10% of 100
        assert event.destroyed_building_count == 1
        assert len(event.affected_tiles) == 1
        assert event.affected_tiles[0].id == tile.id


@pytest.mark.django_db
def test_pillage_event_init_minimum_coins():
    """Test PillageEvent uses minimum loss of 50 coins when calculated loss is lower."""
    savegame = SavegameFactory(coins=100, population=20, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [10, 10]  # 10% coins, 10% population

        event = PillageEvent(savegame=savegame)

        # 10% of 100 is 10, but minimum is 50
        assert event.lost_coins == 50
        # 10% of 20 is 2, but minimum is 5
        assert event.lost_population == 5


@pytest.mark.django_db
def test_pillage_event_init_no_buildings():
    """Test PillageEvent initialization when no buildings exist."""
    savegame = SavegameFactory(coins=500, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 15

        event = PillageEvent(savegame=savegame)

        assert event.destroyed_building_count == 0
        assert len(event.affected_tiles) == 0


@pytest.mark.django_db
def test_pillage_event_init_excludes_non_city_buildings():
    """Test PillageEvent only destroys city buildings (is_city=True)."""
    savegame = SavegameFactory(coins=800, is_enclosed=False)
    wall_type = WallBuildingTypeFactory()
    wall_building = BuildingFactory(building_type=wall_type)
    TileFactory(savegame=savegame, building=wall_building)

    # Also test non-city buildings
    country_building_type = BuildingTypeFactory(is_city=False)
    country_building = BuildingFactory(building_type=country_building_type)
    TileFactory(savegame=savegame, building=country_building)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 15

        event = PillageEvent(savegame=savegame)

        assert event.destroyed_building_count == 0
        assert len(event.affected_tiles) == 0


@pytest.mark.django_db
def test_pillage_event_init_creates_savegame():
    """Test PillageEvent accepts a savegame parameter."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 25

        event = PillageEvent(savegame=savegame)

        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_pillage_event_get_probability_not_enclosed():
    """Test get_probability returns base probability when city is not enclosed."""
    savegame = SavegameFactory(is_enclosed=False)

    event = PillageEvent(savegame=savegame)

    probability = event.get_probability()

    assert probability == 30


@pytest.mark.django_db
def test_pillage_event_get_probability_enclosed():
    """Test get_probability returns 0 when city is enclosed."""
    savegame = SavegameFactory(is_enclosed=True)

    event = PillageEvent(savegame=savegame)

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_pillage_event_prepare_effect_decrease_coins():
    """Test _prepare_effect_decrease_coins returns correct effect."""
    savegame = SavegameFactory(coins=1000, population=100, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [30, 15]  # 30% coins, 15% population

        event = PillageEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_coins()

        assert isinstance(effect, DecreaseCoins)
        assert effect.coins == 300  # 30% of 1000


@pytest.mark.django_db
def test_pillage_event_prepare_effect_decrease_population():
    """Test _prepare_effect_decrease_population returns correct effect."""
    savegame = SavegameFactory(coins=1000, population=200, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [20, 10]  # 20% coins, 10% population

        event = PillageEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_population()

        assert isinstance(effect, DecreasePopulationAbsolute)
        assert effect.lost_population == 20  # 10% of 200


@pytest.mark.django_db
def test_pillage_event_get_effects_includes_all_building_removals():
    """Test get_effects includes RemoveBuilding effects for all affected buildings."""
    savegame = SavegameFactory(coins=500, is_enclosed=False)
    building_type = BuildingTypeFactory(is_city=True)
    building1 = BuildingFactory(building_type=building_type)
    TileFactory(savegame=savegame, building=building1)
    building2 = BuildingFactory(building_type=building_type)
    TileFactory(savegame=savegame, building=building2)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [15, 10, 100]  # coins%, pop%, 100% buildings (2/2)

        event = PillageEvent(savegame=savegame)
        effects = event.get_effects()

        building_effects = [e for e in effects if isinstance(e, RemoveBuilding)]
        assert len(building_effects) == 2


@pytest.mark.django_db
def test_pillage_event_get_verbose_text_with_single_building():
    """Test get_verbose_text returns correct description with single building."""
    savegame = SavegameFactory(coins=800, population=150, is_enclosed=False)
    building_type = BuildingTypeFactory(is_city=True)
    building = BuildingFactory(building_type=building_type)
    TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [25, 10, 100]  # 25% coins, 10% population, 100% buildings

        event = PillageEvent(savegame=savegame)
        initial_coins = event.initial_coins
        lost_population = event.lost_population

        # Simulate effect processing (decrease coins)
        savegame.coins -= 200
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Without a protective wall, raiders pillaged the city! "
            f"They stole {initial_coins - savegame.coins} coins and killed "
            f"{lost_population} inhabitants."
            f" 1 building was destroyed during the raid."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_pillage_event_get_verbose_text_with_multiple_buildings():
    """Test get_verbose_text returns correct description with multiple buildings."""
    savegame = SavegameFactory(coins=800, population=150, is_enclosed=False)
    building_type = BuildingTypeFactory(is_city=True)
    buildings = BuildingFactory.create_batch(5, building_type=building_type)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i, y=0)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [25, 10, 100]  # 25% coins, 10% population, 100% buildings

        event = PillageEvent(savegame=savegame)
        initial_coins = event.initial_coins
        lost_population = event.lost_population
        destroyed_count = event.destroyed_building_count

        # Simulate effect processing (decrease coins)
        savegame.coins -= 200
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Without a protective wall, raiders pillaged the city! "
            f"They stole {initial_coins - savegame.coins} coins and killed "
            f"{lost_population} inhabitants."
            f" {destroyed_count} buildings were destroyed during the raid."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_pillage_event_get_verbose_text_no_building():
    """Test get_verbose_text returns correct description without building."""
    savegame = SavegameFactory(coins=600, population=100, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [20, 12]  # 20% coins, 12% population

        event = PillageEvent(savegame=savegame)
        initial_coins = event.initial_coins
        lost_population = event.lost_population

        # Simulate effect processing (decrease coins)
        savegame.coins -= 120
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Without a protective wall, raiders pillaged the city! "
            f"They stole {initial_coins - savegame.coins} coins and killed "
            f"{lost_population} inhabitants."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_pillage_event_get_effects_with_buildings():
    """Test get_effects returns all effects when buildings exist."""
    savegame = SavegameFactory(coins=1000, population=200, is_enclosed=False)
    building_type = BuildingTypeFactory(is_city=True)
    buildings = BuildingFactory.create_batch(3, building_type=building_type)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i, y=0)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [15, 10, 100]  # 15% coins, 10% population, 100% buildings

        event = PillageEvent(savegame=savegame)
        effects = event.get_effects()

        coin_effects = [e for e in effects if isinstance(e, DecreaseCoins)]
        population_effects = [e for e in effects if isinstance(e, DecreasePopulationAbsolute)]
        building_effects = [e for e in effects if isinstance(e, RemoveBuilding)]

        assert len(coin_effects) == 1
        assert len(population_effects) == 1
        assert len(building_effects) == 3

        assert coin_effects[0].coins == 150  # 15% of 1000
        assert population_effects[0].lost_population == 20  # 10% of 200


@pytest.mark.django_db
def test_pillage_event_get_effects_no_building():
    """Test get_effects returns coin and population effects when no building exists."""
    savegame = SavegameFactory(coins=500, population=80, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [20, 8]  # 20% coins, 8% population

        event = PillageEvent(savegame=savegame)
        effects = event.get_effects()

        coin_effect = next(e for e in effects if isinstance(e, DecreaseCoins))
        population_effect = next(e for e in effects if isinstance(e, DecreasePopulationAbsolute))
        building_effects = [e for e in effects if isinstance(e, RemoveBuilding)]

        assert coin_effect.coins == 100  # 20% of 500
        assert population_effect.lost_population == 6  # 8% of 80, rounded down
        assert len(building_effects) == 0


@pytest.mark.django_db
def test_pillage_event_scaling_with_many_buildings():
    """Test that building destruction scales with city size but respects maximum of 5."""
    savegame = SavegameFactory(coins=1000, population=100, is_enclosed=False)
    building_type = BuildingTypeFactory(is_city=True)
    # Create 20 city buildings
    buildings = BuildingFactory.create_batch(20, building_type=building_type)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i % 5, y=i // 5)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [20, 10, 25]  # 20% coins, 10% population, 25% buildings

        event = PillageEvent(savegame=savegame)

        # 25% of 20 = 5, which is exactly the max
        assert event.destroyed_building_count == 5
        assert len(event.affected_tiles) == 5


@pytest.mark.django_db
def test_pillage_event_scaling_with_few_buildings():
    """Test that building destruction respects minimum of 1."""
    savegame = SavegameFactory(coins=1000, population=100, is_enclosed=False)
    building_type = BuildingTypeFactory(is_city=True)
    # Create 3 city buildings
    buildings = BuildingFactory.create_batch(3, building_type=building_type)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i, y=0)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [20, 10, 10]  # 20% coins, 10% population, 10% buildings

        event = PillageEvent(savegame=savegame)

        # 10% of 3 = 0.3, but minimum is 1
        assert event.destroyed_building_count == 1
        assert len(event.affected_tiles) == 1


@pytest.mark.django_db
def test_pillage_event_process(ruins_building):
    """Test full event processing workflow."""
    savegame = SavegameFactory(coins=1000, population=100, is_enclosed=False)
    building_type = BuildingTypeFactory(is_city=True)
    buildings = BuildingFactory.create_batch(2, building_type=building_type)
    tiles = [TileFactory(savegame=savegame, building=building, x=i, y=0) for i, building in enumerate(buildings)]

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.side_effect = [25, 10, 100]  # 25% coins, 10% population, 100% buildings

        event = PillageEvent(savegame=savegame)
        result_text = event.process()

        # Verify coin effect was applied
        savegame.refresh_from_db()
        assert savegame.coins == 750  # 1000 - 250 = 750

        # Verify population effect was applied
        assert savegame.population == 90  # 100 - 10 = 90

        # Verify buildings were replaced with ruins
        for tile in tiles:
            tile.refresh_from_db()
            assert tile.building is not None
            assert tile.building == ruins_building
            assert tile.building.name == "Ruins"

        # Verify result text is returned
        assert "Without a protective wall, raiders pillaged the city" in result_text
        assert "They stole 250 coins" in result_text
        assert "killed 10 inhabitants" in result_text
        assert "destroyed during the raid" in result_text
