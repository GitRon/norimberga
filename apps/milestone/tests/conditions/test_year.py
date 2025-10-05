import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.conditions.year import MinYearCondition


@pytest.mark.django_db
def test_min_year_condition_init():
    """Test MinYearCondition initialization."""
    savegame = SavegameFactory()
    condition = MinYearCondition(savegame=savegame, value=1200)

    assert condition.savegame == savegame
    assert condition.value == 1200


@pytest.mark.django_db
def test_min_year_condition_is_valid_true():
    """Test MinYearCondition returns True when year >= minimum."""
    savegame = SavegameFactory(current_year=1250)
    condition = MinYearCondition(savegame=savegame, value=1200)

    assert condition.is_valid() is True


@pytest.mark.django_db
def test_min_year_condition_is_valid_true_exact():
    """Test MinYearCondition returns True when year == minimum."""
    savegame = SavegameFactory(current_year=1200)
    condition = MinYearCondition(savegame=savegame, value=1200)

    assert condition.is_valid() is True


@pytest.mark.django_db
def test_min_year_condition_is_valid_false():
    """Test MinYearCondition returns False when year < minimum."""
    savegame = SavegameFactory(current_year=1150)
    condition = MinYearCondition(savegame=savegame, value=1200)

    assert condition.is_valid() is False


@pytest.mark.django_db
def test_min_year_condition_is_valid_early_years():
    """Test MinYearCondition works with early medieval years."""
    savegame = SavegameFactory(current_year=1100)
    condition = MinYearCondition(savegame=savegame, value=1050)

    assert condition.is_valid() is True


@pytest.mark.django_db
def test_min_year_condition_is_valid_later_years():
    """Test MinYearCondition works with later medieval years."""
    savegame = SavegameFactory(current_year=1450)
    condition = MinYearCondition(savegame=savegame, value=1400)

    assert condition.is_valid() is True
