import pytest

from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.city.models import Savegame


@pytest.mark.django_db
def test_increase_coins_init():
    """Test IncreaseCoins initialization with parameters."""
    effect = IncreaseCoins(coins=75)

    assert effect.coins == 75


@pytest.mark.django_db
def test_increase_coins_process_normal_increase():
    """Test process increases coins by specified amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'coins': 150})
    savegame.coins = 150
    savegame.save()
    effect = IncreaseCoins(coins=50)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.coins == 200


@pytest.mark.django_db
def test_increase_coins_process_from_negative():
    """Test process increases coins from negative balance."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'coins': -20})
    savegame.coins = -20
    savegame.save()
    effect = IncreaseCoins(coins=30)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.coins == 10


@pytest.mark.django_db
def test_increase_coins_process_large_increase():
    """Test process handles large coin increases."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'coins': 100})
    savegame.coins = 100
    savegame.save()
    effect = IncreaseCoins(coins=1000)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.coins == 1100


@pytest.mark.django_db
def test_increase_coins_process_creates_savegame():
    """Test process creates savegame if it doesn't exist."""
    # Ensure no savegame exists
    Savegame.objects.filter(id=1).delete()
    effect = IncreaseCoins(coins=40)

    effect.process()

    savegame = Savegame.objects.get(id=1)
    assert savegame.coins == 0 + 40  # Default coins (0) + increased amount


@pytest.mark.django_db
def test_increase_coins_process_zero_increase():
    """Test process with zero increase amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'coins': 250})
    savegame.coins = 250
    savegame.save()
    effect = IncreaseCoins(coins=0)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.coins == 250