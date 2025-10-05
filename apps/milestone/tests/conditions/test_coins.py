import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.conditions.coins import MinCoinsCondition


@pytest.mark.django_db
def test_min_coins_condition_init():
    """Test MinCoinsCondition initialization."""
    savegame = SavegameFactory()
    condition = MinCoinsCondition(savegame=savegame, value=100)

    assert condition.savegame == savegame
    assert condition.value == 100


@pytest.mark.django_db
def test_min_coins_condition_is_valid_true():
    """Test MinCoinsCondition returns True when coins >= minimum."""
    savegame = SavegameFactory(coins=200)
    condition = MinCoinsCondition(savegame=savegame, value=100)

    assert condition.is_valid() is True


@pytest.mark.django_db
def test_min_coins_condition_is_valid_true_exact():
    """Test MinCoinsCondition returns True when coins == minimum."""
    savegame = SavegameFactory(coins=100)
    condition = MinCoinsCondition(savegame=savegame, value=100)

    assert condition.is_valid() is True


@pytest.mark.django_db
def test_min_coins_condition_is_valid_false():
    """Test MinCoinsCondition returns False when coins < minimum."""
    savegame = SavegameFactory(coins=50)
    condition = MinCoinsCondition(savegame=savegame, value=100)

    assert condition.is_valid() is False


@pytest.mark.django_db
def test_min_coins_condition_is_valid_negative_coins():
    """Test MinCoinsCondition works with negative coins (debt)."""
    savegame = SavegameFactory(coins=-50)
    condition = MinCoinsCondition(savegame=savegame, value=0)

    assert condition.is_valid() is False


@pytest.mark.django_db
def test_min_coins_condition_is_valid_zero_minimum():
    """Test MinCoinsCondition with zero minimum."""
    savegame = SavegameFactory(coins=100)
    condition = MinCoinsCondition(savegame=savegame, value=0)

    assert condition.is_valid() is True
