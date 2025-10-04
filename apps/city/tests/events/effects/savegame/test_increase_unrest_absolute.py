import pytest

from apps.city.events.effects.savegame.increase_unrest_absolute import IncreaseUnrestAbsolute
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_increase_unrest_absolute_init():
    """Test IncreaseUnrestAbsolute initialization with parameters."""
    effect = IncreaseUnrestAbsolute(additional_unrest=15)

    assert effect.additional_unrest == 15


@pytest.mark.django_db
def test_increase_unrest_absolute_process_normal_increase():
    """Test process increases unrest by specified amount."""
    savegame = SavegameFactory(unrest=30)
    effect = IncreaseUnrestAbsolute(additional_unrest=20)

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == 50


@pytest.mark.django_db
def test_increase_unrest_absolute_process_maximum_hundred():
    """Test process does not increase unrest above 100."""
    savegame = SavegameFactory(unrest=95)
    effect = IncreaseUnrestAbsolute(additional_unrest=15)

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == 100


@pytest.mark.django_db
def test_increase_unrest_absolute_process_exact_hundred():
    """Test process handles exact 100 unrest correctly."""
    savegame = SavegameFactory(unrest=85)
    effect = IncreaseUnrestAbsolute(additional_unrest=15)

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == 100


@pytest.mark.django_db
def test_increase_unrest_absolute_process_creates_savegame():
    """Test process works with newly created savegame."""
    savegame = SavegameFactory(unrest=0)
    effect = IncreaseUnrestAbsolute(additional_unrest=25)

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == min(0 + 25, 100)  # Default unrest (0) + additional, max 100


@pytest.mark.django_db
def test_increase_unrest_absolute_process_zero_increase():
    """Test process with zero increase amount."""
    savegame = SavegameFactory(unrest=40)
    effect = IncreaseUnrestAbsolute(additional_unrest=0)

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.unrest == 40
