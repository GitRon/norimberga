import pytest

from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_decrease_unrest_absolute_init():
    """Test DecreaseUnrestAbsolute initialization with parameters."""
    effect = DecreaseUnrestAbsolute(lost_unrest=10)

    assert effect.lost_unrest == 10


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_normal_decrease():
    """Test process decreases unrest by specified amount."""
    savegame = SavegameFactory(unrest=50)
    effect = DecreaseUnrestAbsolute(lost_unrest=15)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == 35


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_minimum_zero():
    """Test process does not decrease unrest below zero."""
    savegame = SavegameFactory(unrest=5)
    effect = DecreaseUnrestAbsolute(lost_unrest=10)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == 0


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_exact_zero():
    """Test process handles exact zero unrest correctly."""
    savegame = SavegameFactory(unrest=10)
    effect = DecreaseUnrestAbsolute(lost_unrest=10)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == 0


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_creates_savegame():
    """Test process works with newly created savegame."""
    savegame = SavegameFactory(unrest=0)
    effect = DecreaseUnrestAbsolute(lost_unrest=5)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == max(0 - 5, 0)  # Default unrest (0) - lost_unrest, min 0


@pytest.mark.django_db
def test_decrease_unrest_absolute_process_zero_decrease():
    """Test process with zero decrease amount."""
    savegame = SavegameFactory(unrest=30)
    effect = DecreaseUnrestAbsolute(lost_unrest=0)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == 30
