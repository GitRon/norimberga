import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.services.milestone_tree import MilestoneTreeService
from apps.milestone.tests.factories import MilestoneConditionFactory, MilestoneFactory, MilestoneLogFactory


@pytest.mark.django_db
def test_milestone_tree_service_process_builds_tree():
    """Test MilestoneTreeService builds tree structure."""
    savegame = SavegameFactory()
    root = MilestoneFactory(name="Root", parent=None)
    child = MilestoneFactory(name="Child", parent=root)
    MilestoneConditionFactory(milestone=root)

    service = MilestoneTreeService(savegame=savegame)
    tree = service.process()

    assert len(tree) >= 1
    root_node = next((node for node in tree if node["milestone"].id == root.id), None)
    assert root_node is not None
    assert len(root_node["children"]) == 1
    assert root_node["children"][0]["milestone"].id == child.id


@pytest.mark.django_db
def test_milestone_tree_service_process_sets_completion_status():
    """Test MilestoneTreeService correctly sets completion status."""
    savegame = SavegameFactory()
    completed = MilestoneFactory(name="Completed", parent=None)
    available = MilestoneFactory(name="Available", parent=None)
    MilestoneLogFactory(savegame=savegame, milestone=completed)

    service = MilestoneTreeService(savegame=savegame)
    tree = service.process()

    completed_node = next((node for node in tree if node["milestone"].id == completed.id), None)
    available_node = next((node for node in tree if node["milestone"].id == available.id), None)

    assert completed_node["is_completed"] is True
    assert completed_node["is_available"] is False
    assert available_node["is_completed"] is False
    assert available_node["is_available"] is True


@pytest.mark.django_db
def test_milestone_tree_service_process_sets_locked_status():
    """Test MilestoneTreeService correctly sets locked status for children."""
    savegame = SavegameFactory()
    parent = MilestoneFactory(name="Parent", parent=None)
    MilestoneFactory(name="Locked Child", parent=parent)

    service = MilestoneTreeService(savegame=savegame)
    tree = service.process()

    parent_node = next((node for node in tree if node["milestone"].id == parent.id), None)
    locked_node = parent_node["children"][0]

    assert locked_node["is_locked"] is True
    assert locked_node["is_available"] is False


@pytest.mark.django_db
def test_milestone_tree_service_process_includes_verbose_conditions():
    """Test MilestoneTreeService includes verbose condition info."""
    savegame = SavegameFactory()
    milestone = MilestoneFactory(name="Test", parent=None)
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="50"
    )

    service = MilestoneTreeService(savegame=savegame)
    tree = service.process()

    node = next((node for node in tree if node["milestone"].id == milestone.id), None)
    assert "conditions_verbose" in node
    assert len(node["conditions_verbose"]) == 1
    condition = node["conditions_verbose"][0]
    assert condition["verbose_name"] == "Minimum Population"
    assert condition["value"] == "50"


@pytest.mark.django_db
def test_milestone_tree_service_process_handles_multiple_conditions():
    """Test MilestoneTreeService handles milestones with multiple conditions."""
    savegame = SavegameFactory()
    milestone = MilestoneFactory(name="Test", parent=None)
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.population.MinPopulationCondition", value="100"
    )
    MilestoneConditionFactory(
        milestone=milestone, condition_class="apps.milestone.conditions.coins.MinCoinsCondition", value="500"
    )

    service = MilestoneTreeService(savegame=savegame)
    tree = service.process()

    node = next((node for node in tree if node["milestone"].id == milestone.id), None)
    assert len(node["conditions_verbose"]) == 2
    verbose_names = {c["verbose_name"] for c in node["conditions_verbose"]}
    assert "Minimum Population" in verbose_names
    assert "Minimum Coins" in verbose_names


@pytest.mark.django_db
def test_milestone_tree_service_process_handles_invalid_condition_class():
    """Test MilestoneTreeService handles invalid condition class gracefully."""
    savegame = SavegameFactory()
    milestone = MilestoneFactory(name="Test", parent=None)
    MilestoneConditionFactory(milestone=milestone, condition_class="invalid.module.InvalidClass", value="50")

    service = MilestoneTreeService(savegame=savegame)
    tree = service.process()

    node = next((node for node in tree if node["milestone"].id == milestone.id), None)
    assert len(node["conditions_verbose"]) == 1
    # Should fallback to class name
    assert "InvalidClass" in node["conditions_verbose"][0]["verbose_name"]


@pytest.mark.django_db
def test_milestone_tree_service_process_builds_deep_tree():
    """Test MilestoneTreeService handles deep tree structures."""
    savegame = SavegameFactory()
    root = MilestoneFactory(name="Root", parent=None)
    child1 = MilestoneFactory(name="Child 1", parent=root)
    child2 = MilestoneFactory(name="Child 2", parent=child1)
    child3 = MilestoneFactory(name="Child 3", parent=child2)

    service = MilestoneTreeService(savegame=savegame)
    tree = service.process()

    root_node = next((node for node in tree if node["milestone"].id == root.id), None)
    assert len(root_node["children"]) == 1
    assert root_node["children"][0]["milestone"].id == child1.id
    assert len(root_node["children"][0]["children"]) == 1
    assert root_node["children"][0]["children"][0]["milestone"].id == child2.id
    assert len(root_node["children"][0]["children"][0]["children"]) == 1
    assert root_node["children"][0]["children"][0]["children"][0]["milestone"].id == child3.id
