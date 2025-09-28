from unittest.mock import Mock

import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.milestones.abstract import AbstractMilestone


@pytest.mark.django_db
def test_abstract_milestone_init():
    """Test AbstractMilestone initialization with savegame_id."""
    savegame = SavegameFactory()
    milestone = AbstractMilestone(savegame_id=savegame.id)

    assert milestone.savegame == savegame


@pytest.mark.django_db
def test_abstract_milestone_init_nonexistent_savegame():
    """Test AbstractMilestone initialization fails with non-existent savegame_id."""
    from apps.city.models import Savegame

    with pytest.raises(Savegame.DoesNotExist):
        AbstractMilestone(savegame_id=99999)


@pytest.mark.django_db
def test_abstract_milestone_default_attributes():
    """Test AbstractMilestone has expected default attributes."""
    savegame = SavegameFactory()
    milestone = AbstractMilestone(savegame_id=savegame.id)

    assert milestone.conditions == ()
    assert milestone.previous_quests == ()
    assert milestone.next_quests == ()


@pytest.mark.django_db
def test_abstract_milestone_is_accomplished_no_conditions():
    """Test is_accomplished returns True when no conditions are defined."""
    savegame = SavegameFactory()
    milestone = AbstractMilestone(savegame_id=savegame.id)

    assert milestone.is_accomplished() is True


@pytest.mark.django_db
def test_abstract_milestone_is_accomplished_all_conditions_valid():
    """Test is_accomplished returns True when all conditions are valid."""
    savegame = SavegameFactory()
    milestone = AbstractMilestone(savegame_id=savegame.id)

    # Mock conditions that return True
    mock_condition1 = Mock()
    mock_condition1.is_valid.return_value = True
    mock_condition2 = Mock()
    mock_condition2.is_valid.return_value = True

    milestone.conditions = (mock_condition1, mock_condition2)

    assert milestone.is_accomplished() is True
    mock_condition1.is_valid.assert_called_once_with(savegame=savegame)
    mock_condition2.is_valid.assert_called_once_with(savegame=savegame)


@pytest.mark.django_db
def test_abstract_milestone_is_accomplished_some_conditions_invalid():
    """Test is_accomplished returns False when some conditions are invalid."""
    savegame = SavegameFactory()
    milestone = AbstractMilestone(savegame_id=savegame.id)

    # Mock conditions where one returns False
    mock_condition1 = Mock()
    mock_condition1.is_valid.return_value = True
    mock_condition2 = Mock()
    mock_condition2.is_valid.return_value = False

    milestone.conditions = (mock_condition1, mock_condition2)

    assert milestone.is_accomplished() is False
    mock_condition1.is_valid.assert_called_once_with(savegame=savegame)
    mock_condition2.is_valid.assert_called_once_with(savegame=savegame)


@pytest.mark.django_db
def test_abstract_milestone_is_accomplished_all_conditions_invalid():
    """Test is_accomplished returns False when all conditions are invalid."""
    savegame = SavegameFactory()
    milestone = AbstractMilestone(savegame_id=savegame.id)

    # Mock conditions that return False
    mock_condition1 = Mock()
    mock_condition1.is_valid.return_value = False
    mock_condition2 = Mock()
    mock_condition2.is_valid.return_value = False

    milestone.conditions = (mock_condition1, mock_condition2)

    assert milestone.is_accomplished() is False
    mock_condition1.is_valid.assert_called_once_with(savegame=savegame)
    # Note: due to short-circuit evaluation with all(), second condition might not be called
