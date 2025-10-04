import pytest

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.models import Savegame
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_decrease_coins_init():
    """Test DecreaseCoins initialization with parameters."""
    effect = DecreaseCoins(coins=50)

    assert effect.coins == 50


@pytest.mark.django_db
def test_decrease_coins_process_normal_decrease():
    """Test process decreases coins by specified amount."""
    savegame = SavegameFactory(coins=200)
    effect = DecreaseCoins(coins=75)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 125


@pytest.mark.django_db
def test_decrease_coins_process_negative_balance():
    """Test process allows coins to go negative."""
    savegame = SavegameFactory(coins=30)
    effect = DecreaseCoins(coins=50)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == -20


@pytest.mark.django_db
def test_decrease_coins_process_exact_zero():
    """Test process handles exact zero coins correctly."""
    savegame = SavegameFactory(coins=80)
    effect = DecreaseCoins(coins=80)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 0


@pytest.mark.django_db
def test_decrease_coins_process_creates_savegame():
    """Test process works with newly created savegame."""
    savegame = SavegameFactory(coins=0)
    effect = DecreaseCoins(coins=25)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 0 - 25  # Default coins (0) - decreased amount


@pytest.mark.django_db
def test_decrease_coins_process_zero_decrease():
    """Test process with zero decrease amount."""
    savegame = SavegameFactory(coins=150)
    effect = DecreaseCoins(coins=0)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 150
