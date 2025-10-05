import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.selectors.milestone import (
    get_all_milestones_with_conditions,
    get_available_milestones,
    get_child_milestones,
    get_completed_milestone_ids,
    get_root_milestones,
)
from apps.milestone.tests.factories import MilestoneConditionFactory, MilestoneFactory, MilestoneLogFactory


@pytest.mark.django_db
def test_get_all_milestones_with_conditions():
    """Test get_all_milestones_with_conditions returns all milestones."""
    milestone1 = MilestoneFactory()
    milestone2 = MilestoneFactory()
    MilestoneConditionFactory(milestone=milestone1)

    milestones = get_all_milestones_with_conditions()

    assert len(milestones) >= 2
    milestone_ids = [m.id for m in milestones]
    assert milestone1.id in milestone_ids
    assert milestone2.id in milestone_ids


@pytest.mark.django_db
def test_get_completed_milestone_ids():
    """Test get_completed_milestone_ids returns set of completed milestone IDs."""
    savegame = SavegameFactory()
    milestone1 = MilestoneFactory()
    milestone2 = MilestoneFactory()
    MilestoneLogFactory(savegame=savegame, milestone=milestone1)

    completed_ids = get_completed_milestone_ids(savegame=savegame)

    assert isinstance(completed_ids, set)
    assert milestone1.id in completed_ids
    assert milestone2.id not in completed_ids


@pytest.mark.django_db
def test_get_available_milestones_root_only():
    """Test get_available_milestones returns root milestones when nothing completed."""
    savegame = SavegameFactory()
    root1 = MilestoneFactory(name="Root 1", parent=None)
    root2 = MilestoneFactory(name="Root 2", parent=None)
    MilestoneFactory(name="Child", parent=root1)

    available = get_available_milestones(savegame=savegame)

    available_ids = [m.id for m in available]
    assert root1.id in available_ids
    assert root2.id in available_ids
    assert len(available) == 2


@pytest.mark.django_db
def test_get_available_milestones_excludes_completed():
    """Test get_available_milestones excludes completed milestones."""
    savegame = SavegameFactory()
    root1 = MilestoneFactory(name="Root 1", parent=None)
    root2 = MilestoneFactory(name="Root 2", parent=None)
    MilestoneLogFactory(savegame=savegame, milestone=root1)

    available = get_available_milestones(savegame=savegame)

    available_ids = [m.id for m in available]
    assert root1.id not in available_ids
    assert root2.id in available_ids


@pytest.mark.django_db
def test_get_available_milestones_includes_unlocked_children():
    """Test get_available_milestones includes children of completed milestones."""
    savegame = SavegameFactory()
    parent = MilestoneFactory(name="Parent", parent=None)
    child = MilestoneFactory(name="Child", parent=parent)
    MilestoneLogFactory(savegame=savegame, milestone=parent)

    available = get_available_milestones(savegame=savegame)

    available_ids = [m.id for m in available]
    assert parent.id not in available_ids
    assert child.id in available_ids


@pytest.mark.django_db
def test_get_root_milestones():
    """Test get_root_milestones returns only milestones without parents."""
    root1 = MilestoneFactory(name="Root 1", parent=None)
    root2 = MilestoneFactory(name="Root 2", parent=None)
    MilestoneFactory(name="Child", parent=root1)

    roots = get_root_milestones()

    assert len(roots) == 2
    root_ids = [m.id for m in roots]
    assert root1.id in root_ids
    assert root2.id in root_ids


@pytest.mark.django_db
def test_get_child_milestones():
    """Test get_child_milestones returns children of specified parent."""
    parent = MilestoneFactory(name="Parent")
    child1 = MilestoneFactory(name="Child 1", parent=parent)
    child2 = MilestoneFactory(name="Child 2", parent=parent)
    MilestoneFactory(name="Other", parent=None)

    children = get_child_milestones(parent_id=parent.id)

    assert len(children) == 2
    child_ids = [m.id for m in children]
    assert child1.id in child_ids
    assert child2.id in child_ids


@pytest.mark.django_db
def test_get_child_milestones_empty():
    """Test get_child_milestones returns empty list when no children."""
    parent = MilestoneFactory(name="Parent")

    children = get_child_milestones(parent_id=parent.id)

    assert len(children) == 0
