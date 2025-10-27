import pytest

from apps.milestone.tests.factories import MilestoneConditionFactory, MilestoneFactory, MilestoneLogFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_milestone_log_creation():
    """Test MilestoneLog creation with factory."""
    milestone_log = MilestoneLogFactory.create()

    assert milestone_log.savegame is not None
    assert milestone_log.milestone is not None
    assert milestone_log.accomplished_at is not None
    assert isinstance(milestone_log.accomplished_at, int)


@pytest.mark.django_db
def test_milestone_log_str_representation():
    """Test MilestoneLog __str__ method returns savegame and milestone name."""
    milestone = MilestoneFactory(name="Test Milestone")
    savegame = SavegameFactory(city_name="Test City")
    milestone_log = MilestoneLogFactory(milestone=milestone, savegame=savegame)

    assert str(milestone_log) == "Test City: Test Milestone"


@pytest.mark.django_db
def test_milestone_log_relationships():
    """Test MilestoneLog foreign key relationship with Savegame."""
    savegame = SavegameFactory.create()
    milestone_log = MilestoneLogFactory(savegame=savegame)

    assert milestone_log.savegame == savegame
    assert milestone_log in savegame.milestone_logs.all()


@pytest.mark.django_db
def test_milestone_log_meta_related_name():
    """Test MilestoneLog uses correct related name."""
    savegame = SavegameFactory.create()
    milestone_log = MilestoneLogFactory(savegame=savegame)

    # Test that we can access milestone logs via the related name
    assert hasattr(savegame, "milestone_logs")
    assert milestone_log in savegame.milestone_logs.all()


@pytest.mark.django_db
def test_milestone_log_field_constraints():
    """Test MilestoneLog field constraints."""
    milestone = MilestoneFactory(name="A" * 100)  # Max length
    milestone_log = MilestoneLogFactory(
        milestone=milestone,
        accomplished_at=1,
    )

    assert len(milestone_log.milestone.name) == 100
    assert milestone_log.accomplished_at == 1


@pytest.mark.django_db
def test_milestone_creation():
    """Test Milestone creation with factory."""
    milestone = MilestoneFactory.create()

    assert milestone.name is not None
    assert milestone.description is not None
    assert milestone.parent is None
    assert milestone.order is not None


@pytest.mark.django_db
def test_milestone_parent_child_relationship():
    """Test Milestone parent-child relationship."""
    parent = MilestoneFactory(name="Parent Milestone")
    child = MilestoneFactory(name="Child Milestone", parent=parent)

    assert child.parent == parent
    assert child in parent.milestones.all()


@pytest.mark.django_db
def test_milestone_str_representation():
    """Test Milestone __str__ method."""
    milestone = MilestoneFactory(name="Test Milestone")

    assert str(milestone) == "Test Milestone"


@pytest.mark.django_db
def test_milestone_condition_str_representation():
    """Test MilestoneCondition __str__ method."""
    milestone = MilestoneFactory(name="Test Milestone")
    condition = MilestoneConditionFactory(
        milestone=milestone,
        condition_class="apps.milestone.conditions.population.MinPopulationCondition",
        value="100",
    )

    assert str(condition) == "Test Milestone: apps.milestone.conditions.population.MinPopulationCondition(100)"
