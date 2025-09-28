import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.conditions.abstract import AbstractCondition


def test_abstract_condition_init():
    """Test AbstractCondition initialization."""
    condition = AbstractCondition()
    assert condition is not None


def test_abstract_condition_init_with_kwargs():
    """Test AbstractCondition initialization with kwargs."""
    condition = AbstractCondition(some_arg="value")
    assert condition is not None


def test_abstract_condition_is_valid_not_implemented():
    """Test AbstractCondition is_valid raises NotImplementedError."""
    condition = AbstractCondition()
    savegame = SavegameFactory.build()

    with pytest.raises(NotImplementedError):
        condition.is_valid(savegame)
