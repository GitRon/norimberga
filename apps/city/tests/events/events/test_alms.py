from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.city.events.events.alms import Event as AlmsEvent
from apps.city.models import Savegame


@pytest.mark.django_db
def test_alms_event_init():
    """Test AlmsEvent initialization and class attributes."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"unrest": 30})
    savegame.unrest = 30
    savegame.save()

    with mock.patch("apps.city.events.events.alms.random.randint") as mock_randint:
        mock_randint.return_value = 4

        event = AlmsEvent()

        assert event.PROBABILITY == 15
        assert event.LEVEL == messages.SUCCESS
        assert event.TITLE == "Alms"
        assert event.savegame.id == savegame.id
        assert event.initial_unrest == 30
        assert event.lost_unrest == 4


@pytest.mark.django_db
def test_alms_event_init_creates_savegame():
    """Test AlmsEvent creates savegame if it doesn't exist."""
    # Ensure no savegame exists
    Savegame.objects.filter(id=1).delete()

    with mock.patch("apps.city.events.events.alms.random.randint") as mock_randint:
        mock_randint.return_value = 3

        event = AlmsEvent()

        savegame = Savegame.objects.get(id=1)
        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_alms_event_get_probability_with_conditions():
    """Test get_probability returns base probability when conditions are met."""
    Savegame.objects.filter(id=1).delete()
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"unrest": 20, "population": 50})
    savegame.unrest = 20
    savegame.population = 50
    savegame.save()

    event = AlmsEvent()

    probability = event.get_probability()

    assert probability == 15


@pytest.mark.django_db
def test_alms_event_get_probability_zero_unrest():
    """Test get_probability returns 0 when unrest is zero."""
    Savegame.objects.filter(id=1).delete()
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"unrest": 0, "population": 50})
    savegame.unrest = 0
    savegame.population = 50
    savegame.save()

    event = AlmsEvent()

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_alms_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    Savegame.objects.filter(id=1).delete()
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"unrest": 30, "population": 0})
    savegame.unrest = 30
    savegame.population = 0
    savegame.save()

    event = AlmsEvent()

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_alms_event_get_probability_both_zero():
    """Test get_probability returns 0 when both unrest and population are zero."""
    Savegame.objects.filter(id=1).delete()
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"unrest": 0, "population": 0})
    savegame.unrest = 0
    savegame.population = 0
    savegame.save()

    event = AlmsEvent()

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_alms_event_prepare_effect_decrease_population():
    """Test _prepare_effect_decrease_population returns correct effect."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, unrest=25)

    with mock.patch("apps.city.events.events.alms.random.randint") as mock_randint:
        mock_randint.return_value = 4

        event = AlmsEvent()
        effect = event._prepare_effect_decrease_population()

        assert isinstance(effect, DecreaseUnrestAbsolute)
        assert effect.lost_unrest == 4


@pytest.mark.django_db
def test_alms_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, unrest=40)

    with mock.patch("apps.city.events.events.alms.random.randint") as mock_randint:
        mock_randint.return_value = 5

        event = AlmsEvent()
        initial_unrest = event.initial_unrest

        # Simulate effect processing (decrease unrest)
        savegame.unrest = max(savegame.unrest - 5, 0)
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"Members of the city council decided to provide alms for the sick and poor. "
            f"The unrest drops by {initial_unrest - savegame.unrest}%."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_alms_event_process():
    """Test full event processing workflow."""
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, unrest=30, population=100)

    with mock.patch("apps.city.events.events.alms.random.randint") as mock_randint:
        mock_randint.return_value = 4

        event = AlmsEvent()
        result_text = event.process()

        # Verify effect was applied
        savegame.refresh_from_db()
        assert savegame.unrest == 26  # 30 - 4 = 26

        # Verify result text is returned
        assert "Members of the city council decided to provide alms" in result_text
        assert "The unrest drops by 4%" in result_text


@pytest.mark.django_db
def test_alms_event_get_effects():
    """Test get_effects returns list of effects."""
    Savegame.objects.filter(id=1).delete()
    Savegame.objects.create(id=1, unrest=20)

    with mock.patch("apps.city.events.events.alms.random.randint") as mock_randint:
        mock_randint.return_value = 3

        event = AlmsEvent()
        effects = event.get_effects()

        assert len(effects) == 1
        assert isinstance(effects[0], DecreaseUnrestAbsolute)
        assert effects[0].lost_unrest == 3
