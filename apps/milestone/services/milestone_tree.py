import importlib

from apps.city.models import Savegame
from apps.milestone.models import Milestone
from apps.milestone.selectors.milestone import (
    get_all_milestones_with_conditions,
    get_completed_milestone_ids,
    get_root_milestones,
)


class MilestoneTreeService:
    """
    Service to build a milestone tree structure with completion status.
    """

    def __init__(self, *, savegame: Savegame) -> None:
        self.savegame = savegame

    def _get_condition_verbose_info(self, *, condition_model) -> dict:
        """
        Get verbose information for a condition including human-readable name.

        Returns dict with:
        - verbose_name: Human-readable condition type name
        - value: The condition value
        """
        try:
            # Import the condition class dynamically
            module_path, class_name = condition_model.condition_class.rsplit(".", 1)
            module = importlib.import_module(module_path)
            condition_class = getattr(module, class_name)

            # Get verbose name from the class (all condition classes must inherit from AbstractCondition)
            verbose_name = condition_class.get_verbose_name()

        except (ImportError, AttributeError, ValueError):
            # Fallback to class name if import fails
            verbose_name = condition_model.condition_class.split(".")[-1]

        return {
            "verbose_name": verbose_name,
            "value": condition_model.value,
        }

    def _build_milestone_node(
        self, *, milestone: Milestone, all_milestones: list[Milestone], completed_milestone_ids: set[int]
    ) -> dict:
        """
        Build a single milestone node with its metadata and children.
        """
        is_completed = milestone.id in completed_milestone_ids
        parent_completed = milestone.parent_id is None or milestone.parent_id in completed_milestone_ids

        # Get verbose condition information
        conditions_verbose = [
            self._get_condition_verbose_info(condition_model=condition)
            for condition in milestone.milestone_conditions.all()
        ]

        # Get edicts enabled by this milestone
        enabled_edicts = list(milestone.edicts.filter(is_active=True).order_by("name"))

        milestone_data = {
            "milestone": milestone,
            "is_completed": is_completed,
            "is_available": parent_completed and not is_completed,
            "is_locked": not parent_completed,
            "conditions_verbose": conditions_verbose,
            "enabled_edicts": enabled_edicts,
            "children": [],
        }

        # Recursively build children
        children = [m for m in all_milestones if m.parent_id == milestone.id]
        for child in children:
            child_data = self._build_milestone_node(
                milestone=child, all_milestones=all_milestones, completed_milestone_ids=completed_milestone_ids
            )
            milestone_data["children"].append(child_data)

        return milestone_data

    def process(self) -> list[dict]:
        """
        Build the complete milestone tree structure.

        Returns a list of root milestone nodes, each containing:
        - milestone: The Milestone instance
        - is_completed: Whether this milestone is completed
        - is_available: Whether this milestone is available to complete
        - is_locked: Whether this milestone is locked (parent not completed)
        - conditions_verbose: List of dicts with verbose condition info
        - enabled_edicts: List of Edict instances unlocked by this milestone
        - children: List of child milestone nodes (recursive structure)
        """
        completed_milestone_ids = get_completed_milestone_ids(savegame=self.savegame)
        all_milestones = get_all_milestones_with_conditions()
        root_milestones = get_root_milestones()

        milestone_tree = []
        for root in root_milestones:
            node = self._build_milestone_node(
                milestone=root, all_milestones=all_milestones, completed_milestone_ids=completed_milestone_ids
            )
            milestone_tree.append(node)

        return milestone_tree
