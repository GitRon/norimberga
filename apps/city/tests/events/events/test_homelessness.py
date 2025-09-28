from unittest import mock

import pytest

from apps.city.events.effects.savegame.increase_unrest_absolute import IncreaseUnrestAbsolute
from apps.city.events.events.homelessness import Event as HomelessnessEvent
from apps.city.models import Savegame
from apps.city.tests.factories import BuildingFactory, HouseBuildingTypeFactory, TileFactory


@pytest.mark.django_db
def test_homelessness_event_init():
    """Test HomelessnessEvent initialization and class attributes."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"unrest": 25})
    savegame.unrest = 25
    savegame.save()

    with mock.patch("apps.city.events.events.homelessness.random.randint") as mock_randint:
        mock_randint.return_value = 6

        event = HomelessnessEvent()

        assert event.PROBABILITY == 90
        assert event.TITLE == "Homelessness"
        assert event.savegame.id == savegame.id
        assert event.initial_unrest == 25
        assert event.additional_unrest == 6


@pytest.mark.django_db
def test_homelessness_event_init_creates_savegame():
    """Test HomelessnessEvent creates savegame if it doesn't exist."""
    Savegame.objects.filter(id=1).delete()

    with mock.patch("apps.city.events.events.homelessness.random.randint") as mock_randint:
        mock_randint.return_value = 7

        event = HomelessnessEvent()

        savegame = Savegame.objects.get(id=1)
        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_homelessness_event_get_probability_homeless_situation():
    """Test get_probability returns base probability when population exceeds housing."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 100, "unrest": 50})
    savegame.population = 100
    savegame.unrest = 50
    savegame.save()
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=10)
    TileFactory(savegame=savegame, building=building, x=50, y=10)

    with mock.patch("apps.city.events.events.homelessness.random.randint"):
        event = HomelessnessEvent()
        probability = event.get_probability()

        assert probability == 90


@pytest.mark.django_db
def test_homelessness_event_get_probability_no_homelessness():
    """Test get_probability returns 0 when population fits in housing."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 50, "unrest": 30})
    savegame.population = 50
    savegame.unrest = 30
    savegame.save()
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=60)
    TileFactory(savegame=savegame, building=building, x=51, y=10)

    with mock.patch("apps.city.events.events.homelessness.random.randint"):
        event = HomelessnessEvent()
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_homelessness_event_get_probability_max_unrest():
    """Test get_probability returns 0 when unrest is already at maximum."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 100, "unrest": 100})
    savegame.population = 100
    savegame.unrest = 100
    savegame.save()
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=10)
    TileFactory(savegame=savegame, building=building, x=52, y=10)

    with mock.patch("apps.city.events.events.homelessness.random.randint"):
        event = HomelessnessEvent()
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_homelessness_event_prepare_effect_decrease_population():
    """Test _prepare_effect_decrease_population returns correct effect."""
    Savegame.objects.get_or_create(id=1, defaults={"unrest": 20})

    with mock.patch("apps.city.events.events.homelessness.random.randint") as mock_randint:
        mock_randint.return_value = 7

        event = HomelessnessEvent()
        effect = event._prepare_effect_decrease_population()

        assert isinstance(effect, IncreaseUnrestAbsolute)
        assert effect.additional_unrest == 7


@pytest.mark.django_db
def test_homelessness_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"unrest": 30})
    savegame.unrest = 30
    savegame.save()

    with mock.patch("apps.city.events.events.homelessness.random.randint") as mock_randint:
        mock_randint.return_value = 8

        event = HomelessnessEvent()
        initial_unrest = event.initial_unrest

        # Simulate effect processing (increase unrest)
        savegame.unrest = min(savegame.unrest + 8, 100)
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            "Beggars and homeless folk are crowding the streets. The situation grows tenser by the day. The citys "
            f"unrest increased by {savegame.unrest - initial_unrest}%."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_homelessness_event_random_range():
    """Test that random.randint is called with correct range."""
    Savegame.objects.get_or_create(id=1)

    with mock.patch("apps.city.events.events.homelessness.random.randint") as mock_randint:
        mock_randint.return_value = 6

        HomelessnessEvent()

        mock_randint.assert_called_once_with(5, 8)
