import pytest

from apps.city.events.effects.savegame.increase_unrest_absolute import IncreaseUnrestAbsolute
from apps.city.models import Savegame


@pytest.mark.django_db
def test_increase_unrest_absolute_init():
    """Test IncreaseUnrestAbsolute initialization with parameters."""
    effect = IncreaseUnrestAbsolute(additional_unrest=15)

    assert effect.additional_unrest == 15


@pytest.mark.django_db
def test_increase_unrest_absolute_process_normal_increase():
    """Test process increases unrest by specified amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'unrest': 30})
    savegame.unrest = 30
    savegame.save()
    effect = IncreaseUnrestAbsolute(additional_unrest=20)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 50


@pytest.mark.django_db
def test_increase_unrest_absolute_process_maximum_hundred():
    """Test process does not increase unrest above 100."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'unrest': 95})
    savegame.unrest = 95
    savegame.save()
    effect = IncreaseUnrestAbsolute(additional_unrest=15)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 100


@pytest.mark.django_db
def test_increase_unrest_absolute_process_exact_hundred():
    """Test process handles exact 100 unrest correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'unrest': 85})
    savegame.unrest = 85
    savegame.save()
    effect = IncreaseUnrestAbsolute(additional_unrest=15)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 100


@pytest.mark.django_db
def test_increase_unrest_absolute_process_creates_savegame():
    """Test process creates savegame if it doesn't exist."""
    # Ensure no savegame exists
    Savegame.objects.filter(id=1).delete()
    effect = IncreaseUnrestAbsolute(additional_unrest=25)

    effect.process()

    savegame = Savegame.objects.get(id=1)
    assert savegame.unrest == min(0 + 25, 100)  # Default unrest (0) + additional, max 100


@pytest.mark.django_db
def test_increase_unrest_absolute_process_zero_increase():
    """Test process with zero increase amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'unrest': 40})
    savegame.unrest = 40
    savegame.save()
    effect = IncreaseUnrestAbsolute(additional_unrest=0)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 40