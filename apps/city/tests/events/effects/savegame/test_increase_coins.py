import pytest

from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.city.models import Savegame
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_increase_coins_init():
    """Test IncreaseCoins initialization with parameters."""
    effect = IncreaseCoins(coins=75)

    assert effect.coins == 75


@pytest.mark.django_db
def test_increase_coins_process_normal_increase():
    """Test process increases coins by specified amount."""
    savegame = SavegameFactory(coins=150)
    effect = IncreaseCoins(coins=50)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 200


@pytest.mark.django_db
def test_increase_coins_process_from_negative():
    """Test process increases coins from negative balance."""
    savegame = SavegameFactory(coins=-20)
    effect = IncreaseCoins(coins=30)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 10


@pytest.mark.django_db
def test_increase_coins_process_large_increase():
    """Test process handles large coin increases."""
    savegame = SavegameFactory(coins=100)
    effect = IncreaseCoins(coins=1000)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 1100


@pytest.mark.django_db
def test_increase_coins_process_creates_savegame():
    """Test process works with newly created savegame."""
    savegame = SavegameFactory(coins=0)
    effect = IncreaseCoins(coins=40)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 0 + 40  # Default coins (0) + increased amount


@pytest.mark.django_db
def test_increase_coins_process_zero_increase():
    """Test process with zero increase amount."""
    savegame = SavegameFactory(coins=250)
    effect = IncreaseCoins(coins=0)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.coins == 250
