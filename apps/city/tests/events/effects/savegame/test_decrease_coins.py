import pytest

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.models import Savegame


@pytest.mark.django_db
def test_decrease_coins_init():
    """Test DecreaseCoins initialization with parameters."""
    effect = DecreaseCoins(coins=50)

    assert effect.coins == 50


@pytest.mark.django_db
def test_decrease_coins_process_normal_decrease():
    """Test process decreases coins by specified amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'coins': 200})
    savegame.coins = 200
    savegame.save()
    effect = DecreaseCoins(coins=75)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.coins == 125


@pytest.mark.django_db
def test_decrease_coins_process_negative_balance():
    """Test process allows coins to go negative."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'coins': 30})
    savegame.coins = 30
    savegame.save()
    effect = DecreaseCoins(coins=50)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.coins == -20


@pytest.mark.django_db
def test_decrease_coins_process_exact_zero():
    """Test process handles exact zero coins correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'coins': 80})
    savegame.coins = 80
    savegame.save()
    effect = DecreaseCoins(coins=80)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.coins == 0


@pytest.mark.django_db
def test_decrease_coins_process_creates_savegame():
    """Test process creates savegame if it doesn't exist."""
    # Ensure no savegame exists
    Savegame.objects.filter(id=1).delete()
    effect = DecreaseCoins(coins=25)

    effect.process()

    savegame = Savegame.objects.get(id=1)
    assert savegame.coins == 0 - 25  # Default coins (0) - decreased amount


@pytest.mark.django_db
def test_decrease_coins_process_zero_decrease():
    """Test process with zero decrease amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'coins': 150})
    savegame.coins = 150
    savegame.save()
    effect = DecreaseCoins(coins=0)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.coins == 150