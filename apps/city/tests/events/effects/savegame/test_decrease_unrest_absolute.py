import pytest

from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.city.models import Savegame


@pytest.mark.django_db
def test_decrease_unrest_absolute_init():
    """Test DecreaseUnrestAbsolute initialization with parameters."""
    effect = DecreaseUnrestAbsolute(lost_unrest=10)

    assert effect.lost_unrest == 10


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_normal_decrease():
    """Test process decreases unrest by specified amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'unrest': 50})
    savegame.unrest = 50
    savegame.save()
    effect = DecreaseUnrestAbsolute(lost_unrest=15)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 35


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_minimum_zero():
    """Test process does not decrease unrest below zero."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'unrest': 5})
    savegame.unrest = 5
    savegame.save()
    effect = DecreaseUnrestAbsolute(lost_unrest=10)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 0


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_exact_zero():
    """Test process handles exact zero unrest correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'unrest': 10})
    savegame.unrest = 10
    savegame.save()
    effect = DecreaseUnrestAbsolute(lost_unrest=10)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 0


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_creates_savegame():
    """Test process creates savegame if it doesn't exist."""
    # Ensure no savegame exists
    Savegame.objects.filter(id=1).delete()
    effect = DecreaseUnrestAbsolute(lost_unrest=5)

    effect.process()

    savegame = Savegame.objects.get(id=1)
    assert savegame.unrest == max(0 - 5, 0)  # Default unrest (0) - lost_unrest, min 0


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_zero_decrease():
    """Test process with zero decrease amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'unrest': 30})
    savegame.unrest = 30
    savegame.save()
    effect = DecreaseUnrestAbsolute(lost_unrest=0)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.unrest == 30