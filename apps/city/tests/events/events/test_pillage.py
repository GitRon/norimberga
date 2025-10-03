from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.events.pillage import Event as PillageEvent
from apps.city.models import Savegame
from apps.city.tests.factories import BuildingFactory, BuildingTypeFactory, TileFactory, WallBuildingTypeFactory


@pytest.mark.django_db
def test_pillage_event_init():
    """Test PillageEvent initialization and class attributes."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, coins=1000, is_enclosed=False)
    building_type = BuildingTypeFactory()
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 20

        event = PillageEvent()

        assert event.PROBABILITY == 85
        assert event.LEVEL == messages.ERROR
        assert event.TITLE == "Pillage"
        assert event.savegame.id == savegame.id
        assert event.initial_coins == 1000
        assert event.lost_coins == 200  # 20% of 1000
        assert event.affected_tile.id == tile.id


@pytest.mark.django_db
def test_pillage_event_init_minimum_coins():
    """Test PillageEvent uses minimum loss of 50 coins when calculated loss is lower."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, coins=100, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 10

        event = PillageEvent()

        # 10% of 100 is 10, but minimum is 50
        assert event.lost_coins == 50


@pytest.mark.django_db
def test_pillage_event_init_no_buildings():
    """Test PillageEvent initialization when no buildings exist."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, coins=500, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 15

        event = PillageEvent()

        assert event.affected_tile is None


@pytest.mark.django_db
def test_pillage_event_init_excludes_walls():
    """Test PillageEvent excludes wall buildings from destruction."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, coins=800, is_enclosed=False)
    wall_type = WallBuildingTypeFactory()
    wall_building = BuildingFactory(building_type=wall_type)
    TileFactory(savegame=savegame, building=wall_building)

    event = PillageEvent()

    assert event.affected_tile is None


@pytest.mark.django_db
def test_pillage_event_init_creates_savegame():
    """Test PillageEvent creates savegame if it doesn't exist."""
    Savegame.objects.filter(id=1).delete()

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 25

        event = PillageEvent()

        savegame = Savegame.objects.get(id=1)
        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_pillage_event_get_probability_not_enclosed():
    """Test get_probability returns base probability when city is not enclosed."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, is_enclosed=False)

    event = PillageEvent()

    probability = event.get_probability()

    assert probability == 85


@pytest.mark.django_db
def test_pillage_event_get_probability_enclosed():
    """Test get_probability returns 0 when city is enclosed."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, is_enclosed=True)

    event = PillageEvent()

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_pillage_event_prepare_effect_decrease_coins():
    """Test _prepare_effect_decrease_coins returns correct effect."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, coins=1000, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 30

        event = PillageEvent()
        effect = event._prepare_effect_decrease_coins()

        assert isinstance(effect, DecreaseCoins)
        assert effect.coins == 300  # 30% of 1000


@pytest.mark.django_db
def test_pillage_event_prepare_effect_remove_building_with_building():
    """Test _prepare_effect_remove_building returns effect when building exists."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, coins=500, is_enclosed=False)
    building_type = BuildingTypeFactory()
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(savegame=savegame, building=building)

    event = PillageEvent()
    effect = event._prepare_effect_remove_building()

    assert isinstance(effect, RemoveBuilding)
    assert effect.tile.id == tile.id


@pytest.mark.django_db
def test_pillage_event_prepare_effect_remove_building_no_building():
    """Test _prepare_effect_remove_building returns None when no building exists."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, coins=500, is_enclosed=False)

    event = PillageEvent()

    effect = event._prepare_effect_remove_building()

    assert effect is None


@pytest.mark.django_db
def test_pillage_event_get_verbose_text_with_building():
    """Test get_verbose_text returns correct description with building."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, coins=800, is_enclosed=False)
    building_type = BuildingTypeFactory()
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 25

        event = PillageEvent()
        initial_coins = event.initial_coins

        # Simulate effect processing (decrease coins)
        savegame.coins -= 200
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Without a protective wall, raiders pillaged the city! "
            f"They stole {initial_coins - savegame.coins} coins."
            f" The building at {tile} was destroyed during the raid."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_pillage_event_get_verbose_text_no_building():
    """Test get_verbose_text returns correct description without building."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, coins=600, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 20

        event = PillageEvent()
        initial_coins = event.initial_coins

        # Simulate effect processing (decrease coins)
        savegame.coins -= 120
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Without a protective wall, raiders pillaged the city! They stole {initial_coins - savegame.coins} coins."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_pillage_event_get_effects_with_building():
    """Test get_effects returns both effects when building exists."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, coins=1000, is_enclosed=False)
    building_type = BuildingTypeFactory()
    building = BuildingFactory(building_type=building_type)
    TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 15

        event = PillageEvent()
        effects = event.get_effects()

        assert len(effects) == 2
        coin_effect = next(e for e in effects if isinstance(e, DecreaseCoins))
        building_effect = next(e for e in effects if isinstance(e, RemoveBuilding))

        assert coin_effect.coins == 150  # 15% of 1000
        assert building_effect.tile.building.id == building.id


@pytest.mark.django_db
def test_pillage_event_get_effects_no_building():
    """Test get_effects returns coin effect and None when no building exists."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, coins=500, is_enclosed=False)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 20

        event = PillageEvent()
        effects = event.get_effects()

        # Should have 2 effects: coin effect and None (for building)
        assert len(effects) == 2

        # Filter out None effects like process() does
        valid_effects = [e for e in effects if e is not None]
        assert len(valid_effects) == 1
        assert isinstance(valid_effects[0], DecreaseCoins)
        assert valid_effects[0].coins == 100  # 20% of 500


@pytest.mark.django_db
def test_pillage_event_process():
    """Test full event processing workflow."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, coins=1000, is_enclosed=False)
    building_type = BuildingTypeFactory()
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(savegame=savegame, building=building)

    with mock.patch("apps.city.events.events.pillage.random.randint") as mock_randint:
        mock_randint.return_value = 25

        event = PillageEvent()
        result_text = event.process()

        # Verify coin effect was applied
        savegame.refresh_from_db()
        assert savegame.coins == 750  # 1000 - 250 = 750

        # Verify building effect was applied
        tile.refresh_from_db()
        assert tile.building is None

        # Verify result text is returned
        assert "Without a protective wall, raiders pillaged the city" in result_text
        assert "They stole 250 coins" in result_text
        assert "destroyed during the raid" in result_text
