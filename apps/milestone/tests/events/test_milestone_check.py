import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.events.events.milestone_check import Event as MilestoneCheckEvent
from apps.milestone.tests.factories import MilestoneConditionFactory, MilestoneFactory


@pytest.mark.django_db
def test_milestone_check_event_get_verbose_text_single_milestone():
    """Test event returns proper message for single milestone."""
    savegame = SavegameFactory(population=100)
    milestone = MilestoneFactory(name="Test Milestone")
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="50"
    )

    event = MilestoneCheckEvent(savegame=savegame)
    result = event.process()

    assert result == "Congratulations! You have achieved the milestone: Test Milestone"


@pytest.mark.django_db
def test_milestone_check_event_get_verbose_text_multiple_milestones():
    """Test event returns proper message for multiple milestones."""
    savegame = SavegameFactory(population=100, coins=1000)
    milestone1 = MilestoneFactory(name="Milestone 1")
    milestone2 = MilestoneFactory(name="Milestone 2")
    MilestoneConditionFactory(
        milestone=milestone1, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="50"
    )
    MilestoneConditionFactory(
        milestone=milestone2, condition_class="apps.milestone.conditions.coins.MinCoinsCondition", value="500"
    )

    event = MilestoneCheckEvent(savegame=savegame)
    result = event.process()

    assert "Congratulations! You have achieved multiple milestones:" in result
    assert "Milestone 1" in result
    assert "Milestone 2" in result


@pytest.mark.django_db
def test_milestone_check_event_returns_none_when_no_milestones():
    """Test event returns None when no milestones completed."""
    savegame = SavegameFactory(population=10)
    milestone = MilestoneFactory(name="Test Milestone")
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="100"
    )

    event = MilestoneCheckEvent(savegame=savegame)
    result = event.process()

    assert result is None


@pytest.mark.django_db
def test_milestone_check_event_probability():
    """Test event has 100% probability."""
    savegame = SavegameFactory()
    event = MilestoneCheckEvent(savegame=savegame)

    assert event.PROBABILITY == 100


@pytest.mark.django_db
def test_milestone_check_event_get_verbose_text_returns_none_when_no_completed():
    """Test get_verbose_text returns None when no milestones completed."""
    savegame = SavegameFactory()
    event = MilestoneCheckEvent(savegame=savegame)

    assert event.get_verbose_text() is None
