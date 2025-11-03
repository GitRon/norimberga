from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.events.effects.savegame.increase_unrest_absolute import IncreaseUnrestAbsolute
from apps.city.events.events.enemy_raid import Event as EnemyRaidEvent
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TileFactory,
    WallBuildingTypeFactory,
)
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_enemy_raid_event_init():
    """Test EnemyRaidEvent initialization and class attributes."""
    savegame = SavegameFactory(coins=1000, population=100)
    building_type = BuildingTypeFactory(is_city=True)
    building = BuildingFactory(building_type=building_type)
    TileFactory(savegame=savegame, building=building)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=20),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        # Intensity is 20-10=10
        # intensity_multiplier = 1 + (10/10) = 2
        mock_randint.side_effect = [25, 15, 15, 20]  # 25% coins, 15% population, 15% unrest, 20% buildings

        event = EnemyRaidEvent(savegame=savegame)

        assert event.PROBABILITY == 5
        assert event.LEVEL == messages.ERROR
        assert event.TITLE == "Enemy Raid"
        assert event.savegame.id == savegame.id
        assert event.prestige == 20
        assert event.defense == 10
        assert event.intensity == 10
        assert event.initial_coins == 1000
        assert event.lost_coins == 500  # 25% * 1000 * 2.0 = 500
        assert event.lost_population == 30  # 15% * 100 * 2.0 = 30
        assert event.increased_unrest == 30  # 15 * 2.0 = 30 (capped at 30)
        assert event.destroyed_building_count == 1


@pytest.mark.django_db
def test_enemy_raid_event_init_minimum_losses():
    """Test EnemyRaidEvent uses minimum losses when calculated loss is lower."""
    savegame = SavegameFactory(coins=100, population=20)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=12),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        # Intensity is 2, multiplier = 1.2
        mock_randint.side_effect = [15, 10, 10]  # 15% coins, 10% population, 10% unrest

        event = EnemyRaidEvent(savegame=savegame)

        # 15% of 100 * 1.2 = 18, but minimum is 100
        assert event.lost_coins == 100
        # 10% of 20 * 1.2 = 2.4, but minimum is 10
        assert event.lost_population == 10
        # 10 * 1.2 = 12
        assert event.increased_unrest == 12


@pytest.mark.django_db
def test_enemy_raid_event_init_no_buildings():
    """Test EnemyRaidEvent initialization when no buildings exist."""
    savegame = SavegameFactory(coins=500)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.return_value = 20

        event = EnemyRaidEvent(savegame=savegame)

        assert event.destroyed_building_count == 0
        assert len(event.affected_tiles) == 0


@pytest.mark.django_db
def test_enemy_raid_event_init_excludes_non_city_buildings():
    """Test EnemyRaidEvent only destroys city buildings."""
    savegame = SavegameFactory(coins=800)
    wall_type = WallBuildingTypeFactory.create()
    wall_building = BuildingFactory(building_type=wall_type)
    TileFactory(savegame=savegame, building=wall_building)

    country_building_type = BuildingTypeFactory(is_city=False)
    country_building = BuildingFactory(building_type=country_building_type)
    TileFactory(savegame=savegame, building=country_building)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.return_value = 20

        event = EnemyRaidEvent(savegame=savegame)

        assert event.destroyed_building_count == 0
        assert len(event.affected_tiles) == 0


@pytest.mark.django_db
def test_enemy_raid_event_init_excludes_unique_buildings():
    """Test EnemyRaidEvent excludes unique buildings from destruction."""
    savegame = SavegameFactory(coins=800)
    unique_building_type = BuildingTypeFactory(is_city=True, is_unique=True)
    unique_building = BuildingFactory(building_type=unique_building_type)
    TileFactory(savegame=savegame, building=unique_building)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.return_value = 20

        event = EnemyRaidEvent(savegame=savegame)

        assert event.destroyed_building_count == 0


@pytest.mark.django_db
def test_enemy_raid_event_unrest_capped_at_30():
    """Test that unrest increase is capped at 30%."""
    savegame = SavegameFactory(coins=1000, population=100)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=100),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        # Intensity is 90, multiplier = 10
        mock_randint.side_effect = [20, 10, 20]  # 20% coins, 10% population, 20% unrest

        event = EnemyRaidEvent(savegame=savegame)

        # 20 * 10 = 200, but capped at 30
        assert event.increased_unrest == 30


@pytest.mark.django_db
def test_enemy_raid_event_get_probability_defense_exceeds_prestige():
    """Test get_probability returns 0 when defense >= prestige."""
    savegame = SavegameFactory.create()

    with (
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=5),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        event = EnemyRaidEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_enemy_raid_event_get_probability_equal_values():
    """Test get_probability returns 0 when defense equals prestige."""
    savegame = SavegameFactory.create()

    with (
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=10),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        event = EnemyRaidEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_enemy_raid_event_get_probability_prestige_exceeds_defense():
    """Test get_probability scales with intensity when prestige > defense."""
    savegame = SavegameFactory.create()

    with (
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        event = EnemyRaidEvent(savegame=savegame)
        probability = event.get_probability()

        # Base 5% + intensity 5 = 10%
        assert probability == 10


@pytest.mark.django_db
def test_enemy_raid_event_get_probability_capped_at_50():
    """Test get_probability is capped at 50%."""
    savegame = SavegameFactory.create()

    with (
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=100),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        event = EnemyRaidEvent(savegame=savegame)
        probability = event.get_probability()

        # Base 5% + intensity 90 = 95%, but capped at 50%
        assert probability == 50


@pytest.mark.django_db
def test_enemy_raid_event_prepare_effect_decrease_coins():
    """Test _prepare_effect_decrease_coins returns correct effect."""
    savegame = SavegameFactory(coins=1000, population=100)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [30, 15, 15]  # 30% coins, 15% population, 15% unrest

        event = EnemyRaidEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_coins()

        assert isinstance(effect, DecreaseCoins)
        # 30% * 1000 * 1.5 = 450
        assert effect.coins == 450


@pytest.mark.django_db
def test_enemy_raid_event_prepare_effect_decrease_population():
    """Test _prepare_effect_decrease_population returns correct effect."""
    savegame = SavegameFactory(coins=1000, population=200)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [20, 10, 10]  # 20% coins, 10% population, 10% unrest

        event = EnemyRaidEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_population()

        assert isinstance(effect, DecreasePopulationAbsolute)
        # 10% * 200 * 1.5 = 30
        assert effect.lost_population == 30


@pytest.mark.django_db
def test_enemy_raid_event_prepare_effect_increase_unrest():
    """Test _prepare_effect_increase_unrest returns correct effect."""
    savegame = SavegameFactory(coins=1000, population=200)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [20, 10, 15]  # 20% coins, 10% population, 15% unrest

        event = EnemyRaidEvent(savegame=savegame)
        effect = event._prepare_effect_increase_unrest()

        assert isinstance(effect, IncreaseUnrestAbsolute)
        # 15 * 1.5 = 22
        assert effect.additional_unrest == 22


@pytest.mark.django_db
def test_enemy_raid_event_get_effects_with_buildings():
    """Test get_effects returns all effects when buildings exist."""
    savegame = SavegameFactory(coins=1000, population=200)
    building_type = BuildingTypeFactory(is_city=True)
    buildings = BuildingFactory.create_batch(3, building_type=building_type)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i, y=0)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [15, 10, 12, 100]  # coins%, pop%, unrest%, 100% buildings

        event = EnemyRaidEvent(savegame=savegame)
        effects = event.get_effects()

        coin_effects = [e for e in effects if isinstance(e, DecreaseCoins)]
        population_effects = [e for e in effects if isinstance(e, DecreasePopulationAbsolute)]
        unrest_effects = [e for e in effects if isinstance(e, IncreaseUnrestAbsolute)]
        building_effects = [e for e in effects if isinstance(e, RemoveBuilding)]

        assert len(coin_effects) == 1
        assert len(population_effects) == 1
        assert len(unrest_effects) == 1
        assert len(building_effects) == 3


@pytest.mark.django_db
def test_enemy_raid_event_get_effects_no_buildings():
    """Test get_effects returns coin, population, and unrest effects when no buildings exist."""
    savegame = SavegameFactory(coins=500, population=80)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [20, 15, 18]  # 20% coins, 15% population, 18% unrest

        event = EnemyRaidEvent(savegame=savegame)
        effects = event.get_effects()

        coin_effect = next(e for e in effects if isinstance(e, DecreaseCoins))
        population_effect = next(e for e in effects if isinstance(e, DecreasePopulationAbsolute))
        unrest_effect = next(e for e in effects if isinstance(e, IncreaseUnrestAbsolute))
        building_effects = [e for e in effects if isinstance(e, RemoveBuilding)]

        assert coin_effect.coins == 150  # 20% * 500 * 1.5 = 150
        assert population_effect.lost_population == 18  # 15% * 80 * 1.5 = 18
        assert unrest_effect.additional_unrest == 27  # 18 * 1.5 = 27
        assert len(building_effects) == 0


@pytest.mark.django_db
def test_enemy_raid_event_get_verbose_text_with_single_building():
    """Test get_verbose_text returns correct description with single building."""
    savegame = SavegameFactory(coins=800, population=150)
    building_type = BuildingTypeFactory(is_city=True)
    building = BuildingFactory(building_type=building_type)
    TileFactory(savegame=savegame, building=building)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=20),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [25, 10, 15, 100]  # coins%, pop%, unrest%, 100% buildings

        event = EnemyRaidEvent(savegame=savegame)
        initial_coins = event.initial_coins
        lost_population = event.lost_population
        increased_unrest = event.increased_unrest

        # Simulate effect processing
        savegame.coins -= 400
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Your city's wealth and prestige (20) attracted enemy forces! "
            f"With only 10 defense, the raiders overwhelmed your guards. "
            f"They stole {initial_coins - savegame.coins} coins and killed "
            f"{lost_population} inhabitants. "
            f"Unrest increased by {increased_unrest}%."
            f" 1 building was destroyed during the raid."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_enemy_raid_event_get_verbose_text_with_multiple_buildings():
    """Test get_verbose_text returns correct description with multiple buildings."""
    savegame = SavegameFactory(coins=800, population=150)
    building_type = BuildingTypeFactory(is_city=True)
    buildings = BuildingFactory.create_batch(5, building_type=building_type)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i, y=0)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=20),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [25, 10, 15, 100]  # coins%, pop%, unrest%, 100% buildings

        event = EnemyRaidEvent(savegame=savegame)
        initial_coins = event.initial_coins
        lost_population = event.lost_population
        increased_unrest = event.increased_unrest
        destroyed_count = event.destroyed_building_count

        # Simulate effect processing
        savegame.coins -= 400
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Your city's wealth and prestige (20) attracted enemy forces! "
            f"With only 10 defense, the raiders overwhelmed your guards. "
            f"They stole {initial_coins - savegame.coins} coins and killed "
            f"{lost_population} inhabitants. "
            f"Unrest increased by {increased_unrest}%."
            f" {destroyed_count} buildings were destroyed during the raid."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_enemy_raid_event_get_verbose_text_no_buildings():
    """Test get_verbose_text returns correct description without buildings."""
    savegame = SavegameFactory(coins=600, population=100)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=20),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [20, 12, 18]  # 20% coins, 12% population, 18% unrest

        event = EnemyRaidEvent(savegame=savegame)
        initial_coins = event.initial_coins
        lost_population = event.lost_population
        increased_unrest = event.increased_unrest

        # Simulate effect processing
        savegame.coins -= 240
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Your city's wealth and prestige (20) attracted enemy forces! "
            f"With only 10 defense, the raiders overwhelmed your guards. "
            f"They stole {initial_coins - savegame.coins} coins and killed "
            f"{lost_population} inhabitants. "
            f"Unrest increased by {increased_unrest}%."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_enemy_raid_event_get_prestige():
    """Test _get_prestige calls PrestigeCalculationService."""
    savegame = SavegameFactory.create()

    with (
        mock.patch("apps.city.events.events.enemy_raid.PrestigeCalculationService") as mock_service,
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=5),
    ):
        mock_service.return_value.process.return_value = 25

        event = EnemyRaidEvent(savegame=savegame)
        prestige = event._get_prestige()

        assert prestige == 25
        mock_service.assert_called_with(savegame=savegame)
        mock_service.return_value.process.assert_called()


@pytest.mark.django_db
def test_enemy_raid_event_get_defense():
    """Test _get_defense calls DefenseCalculationService."""
    savegame = SavegameFactory.create()

    with (
        mock.patch("apps.city.events.events.enemy_raid.DefenseCalculationService") as mock_service,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=10),
    ):
        mock_service.return_value.process.return_value = 15

        event = EnemyRaidEvent(savegame=savegame)
        defense = event._get_defense()

        assert defense == 15
        mock_service.assert_called_with(savegame=savegame)
        mock_service.return_value.process.assert_called()


@pytest.mark.django_db
def test_enemy_raid_event_scaling_with_many_buildings():
    """Test that building destruction scales with city size but respects maximum of 5."""
    savegame = SavegameFactory(coins=1000, population=100)
    building_type = BuildingTypeFactory(is_city=True)
    buildings = BuildingFactory.create_batch(20, building_type=building_type)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i % 5, y=i // 5)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=20),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [20, 10, 15, 30]  # coins%, pop%, unrest%, 30% buildings

        event = EnemyRaidEvent(savegame=savegame)

        # 30% * 20 * 2 = 12, but capped at 5
        assert event.destroyed_building_count == 5
        assert len(event.affected_tiles) == 5


@pytest.mark.django_db
def test_enemy_raid_event_scaling_with_few_buildings():
    """Test that building destruction respects minimum of 1."""
    savegame = SavegameFactory(coins=1000, population=100)
    building_type = BuildingTypeFactory(is_city=True)
    buildings = BuildingFactory.create_batch(3, building_type=building_type)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i, y=0)

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=15),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [20, 10, 15, 15]  # coins%, pop%, unrest%, 15% buildings

        event = EnemyRaidEvent(savegame=savegame)

        # 15% * 3 * 1.5 = 0.675, but minimum is 1
        assert event.destroyed_building_count == 1
        assert len(event.affected_tiles) == 1


@pytest.mark.django_db
def test_enemy_raid_event_process(ruins_building):
    """Test full event processing workflow."""
    savegame = SavegameFactory(coins=1000, population=100, unrest=10)
    building_type = BuildingTypeFactory(is_city=True)
    buildings = BuildingFactory.create_batch(2, building_type=building_type)
    tiles = [TileFactory(savegame=savegame, building=building, x=i, y=0) for i, building in enumerate(buildings)]

    with (
        mock.patch("apps.city.events.events.enemy_raid.random.randint") as mock_randint,
        mock.patch.object(EnemyRaidEvent, "_get_prestige", return_value=20),
        mock.patch.object(EnemyRaidEvent, "_get_defense", return_value=10),
    ):
        mock_randint.side_effect = [25, 10, 15, 100]  # coins%, pop%, unrest%, 100% buildings

        event = EnemyRaidEvent(savegame=savegame)
        result_text = event.process()

        # Verify coin effect was applied (25% * 1000 * 2 = 500)
        savegame.refresh_from_db()
        assert savegame.coins == 500

        # Verify population effect was applied (10% * 100 * 2 = 20)
        assert savegame.population == 80

        # Verify unrest effect was applied (15 * 2 = 30, capped)
        assert savegame.unrest == 40  # 10 + 30

        # Verify buildings were replaced with ruins
        for tile in tiles:
            tile.refresh_from_db()
            assert tile.building is not None
            assert tile.building.building_type.type == tile.building.building_type.Type.RUINS

        # Verify result text is returned
        assert "Your city's wealth and prestige (20) attracted enemy forces" in result_text
        assert "They stole 500 coins" in result_text
        assert "killed 20 inhabitants" in result_text
        assert "Unrest increased by 30%" in result_text
        assert "destroyed during the raid" in result_text
