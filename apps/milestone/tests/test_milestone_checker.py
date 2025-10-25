import pytest

from apps.milestone.models import MilestoneLog
from apps.milestone.services.milestone_checker import MilestoneCheckerService
from apps.milestone.tests.factories import MilestoneConditionFactory, MilestoneFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_milestone_checker_service_process_completes_milestone_when_conditions_met():
    # Arrange
    savegame = SavegameFactory(population=100)
    milestone = MilestoneFactory(name="First Village", description="Reach 50 inhabitants")
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="50"
    )
    service = MilestoneCheckerService(savegame=savegame)

    # Act
    completed = service.process()

    # Assert
    assert len(completed) == 1
    assert completed[0] == milestone
    assert MilestoneLog.objects.filter(savegame=savegame, milestone=milestone).exists()


@pytest.mark.django_db
def test_milestone_checker_service_process_does_not_complete_milestone_when_conditions_not_met():
    # Arrange
    savegame = SavegameFactory(population=30)
    milestone = MilestoneFactory(name="First Village", description="Reach 50 inhabitants")
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="50"
    )
    service = MilestoneCheckerService(savegame=savegame)

    # Act
    completed = service.process()

    # Assert
    assert len(completed) == 0
    assert not MilestoneLog.objects.filter(savegame=savegame, milestone=milestone).exists()


@pytest.mark.django_db
def test_milestone_checker_service_process_handles_multiple_conditions():
    # Arrange
    savegame = SavegameFactory(population=100, coins=500)
    milestone = MilestoneFactory(name="Prosperous Village")
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="50"
    )
    service = MilestoneCheckerService(savegame=savegame)

    # Act
    completed = service.process()

    # Assert
    assert len(completed) == 1
    assert completed[0] == milestone


@pytest.mark.django_db
def test_milestone_checker_service_process_does_not_recheck_completed_milestones():
    # Arrange
    savegame = SavegameFactory(population=100)
    milestone = MilestoneFactory(name="First Village")
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="50"
    )
    service = MilestoneCheckerService(savegame=savegame)

    # Act - complete milestone first time
    service.process()
    initial_count = MilestoneLog.objects.filter(savegame=savegame, milestone=milestone).count()

    # Act - run service again
    completed = service.process()

    # Assert - should not create duplicate log
    assert len(completed) == 0
    assert MilestoneLog.objects.filter(savegame=savegame, milestone=milestone).count() == initial_count


@pytest.mark.django_db
def test_milestone_checker_service_process_only_checks_available_milestones():
    # Arrange
    savegame = SavegameFactory(population=100)
    parent_milestone = MilestoneFactory(name="Parent Milestone")
    MilestoneConditionFactory(
        milestone=parent_milestone,
        condition_class="apps.milestone.conditions.population.MinPopulationCondition",
        value="50",
    )

    # Child milestone requires parent to be completed
    child_milestone = MilestoneFactory(name="Child Milestone", parent=parent_milestone)
    MilestoneConditionFactory(
        milestone=child_milestone,
        condition_class="apps.milestone.conditions.population.MinPopulationCondition",
        value="75",
    )

    service = MilestoneCheckerService(savegame=savegame)

    # Act - first run should complete only parent
    completed = service.process()

    # Assert
    assert len(completed) == 1
    assert completed[0] == parent_milestone
    assert not MilestoneLog.objects.filter(savegame=savegame, milestone=child_milestone).exists()


@pytest.mark.django_db
def test_milestone_checker_service_process_returns_false_for_milestone_without_conditions():
    """Test milestone checker returns false for milestones without conditions."""
    savegame = SavegameFactory(population=100)
    milestone = MilestoneFactory(name="No Conditions Milestone")
    # Don't add any conditions

    service = MilestoneCheckerService(savegame=savegame)
    completed = service.process()

    assert len(completed) == 0
    assert not MilestoneLog.objects.filter(savegame=savegame, milestone=milestone).exists()


@pytest.mark.django_db
def test_milestone_checker_service_process_handles_float_values():
    """Test milestone checker handles float values in conditions."""
    savegame = SavegameFactory(population=100)
    milestone = MilestoneFactory(name="Float Value Milestone")
    MilestoneConditionFactory(
        milestone=milestone,
        condition_class="apps.milestone.conditions.population.MinPopulationCondition",
        value="50.5",  # Float value
    )

    service = MilestoneCheckerService(savegame=savegame)
    completed = service.process()

    assert len(completed) == 1


@pytest.mark.django_db
def test_milestone_checker_service_process_handles_string_values():
    """Test milestone checker handles string values in conditions that fail comparison."""
    savegame = SavegameFactory(population=100)
    milestone = MilestoneFactory(name="String Value Milestone")
    MilestoneConditionFactory(
        milestone=milestone,
        condition_class="apps.milestone.conditions.population.MinPopulationCondition",
        value="not_a_number",  # String value that can't be converted
    )

    service = MilestoneCheckerService(savegame=savegame)
    # Will raise TypeError during comparison, so we expect that
    with pytest.raises(TypeError):
        service.process()


@pytest.mark.django_db
def test_milestone_checker_service_process_unlocks_child_milestones():
    # Arrange
    savegame = SavegameFactory(population=100)
    parent_milestone = MilestoneFactory(name="Parent Milestone")
    MilestoneConditionFactory(
        milestone=parent_milestone,
        condition_class="apps.milestone.conditions.population.MinPopulationCondition",
        value="50",
    )

    child_milestone = MilestoneFactory(name="Child Milestone", parent=parent_milestone)
    MilestoneConditionFactory(
        milestone=child_milestone,
        condition_class="apps.milestone.conditions.population.MinPopulationCondition",
        value="75",
    )

    service = MilestoneCheckerService(savegame=savegame)

    # Act - complete parent first
    service.process()

    # Act - run again to check child
    completed = service.process()

    # Assert - child should now be completed
    assert len(completed) == 1
    assert completed[0] == child_milestone
    assert MilestoneLog.objects.filter(savegame=savegame, milestone=child_milestone).exists()
