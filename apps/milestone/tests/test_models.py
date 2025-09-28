import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.tests.factories import MilestoneLogFactory


@pytest.mark.django_db
def test_milestone_log_creation():
    """Test MilestoneLog creation with factory."""
    milestone_log = MilestoneLogFactory()

    assert milestone_log.savegame is not None
    assert milestone_log.milestone is not None
    assert milestone_log.accomplished_at is not None
    assert isinstance(milestone_log.accomplished_at, int)


@pytest.mark.django_db
def test_milestone_log_str_representation():
    """Test MilestoneLog __str__ method returns milestone name."""
    milestone_log = MilestoneLogFactory(milestone="Test Milestone")

    assert str(milestone_log) == "Test Milestone"


@pytest.mark.django_db
def test_milestone_log_relationships():
    """Test MilestoneLog foreign key relationship with Savegame."""
    savegame = SavegameFactory()
    milestone_log = MilestoneLogFactory(savegame=savegame)

    assert milestone_log.savegame == savegame
    assert milestone_log in savegame.quest_logs.all()


@pytest.mark.django_db
def test_milestone_log_meta_related_name():
    """Test MilestoneLog uses correct related name."""
    savegame = SavegameFactory()
    milestone_log = MilestoneLogFactory(savegame=savegame)

    # Test that we can access milestone logs via the related name
    assert hasattr(savegame, "quest_logs")
    assert milestone_log in savegame.quest_logs.all()


@pytest.mark.django_db
def test_milestone_log_field_constraints():
    """Test MilestoneLog field constraints."""
    milestone_log = MilestoneLogFactory(
        milestone="A" * 100,  # Max length
        accomplished_at=1,
    )

    assert len(milestone_log.milestone) == 100
    assert milestone_log.accomplished_at == 1
