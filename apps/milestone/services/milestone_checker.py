import importlib

from apps.milestone.conditions.abstract import AbstractCondition
from apps.milestone.models import Milestone, MilestoneLog
from apps.milestone.selectors.milestone import get_available_milestones
from apps.savegame.models import Savegame


class MilestoneCheckerService:
    """
    Checks which milestones have been accomplished for a savegame.
    """

    def __init__(self, *, savegame: Savegame) -> None:
        self.savegame = savegame

    def _check_milestone_conditions(self, *, milestone: Milestone) -> bool:
        """
        Check if all conditions for a milestone are met.
        """
        conditions = milestone.milestone_conditions.all()

        if not conditions:
            return False

        for condition_model in conditions:
            # Import the condition class dynamically
            module_path, class_name = condition_model.condition_class.rsplit(".", 1)
            module = importlib.import_module(module_path)
            condition_class = getattr(module, class_name)

            # Instantiate and check the condition
            # Convert value to appropriate type (int, float, or keep as string)
            try:
                value = int(condition_model.value)
            except ValueError:
                try:
                    value = float(condition_model.value)
                except ValueError:
                    value = condition_model.value

            condition: AbstractCondition = condition_class(savegame=self.savegame, value=value)

            if not condition.is_valid():
                return False

        return True

    def process(self) -> list[Milestone]:
        """
        Check all available milestones and create MilestoneLog entries for completed ones.
        Returns list of newly completed milestones.
        """
        available_milestones = get_available_milestones(savegame=self.savegame)
        newly_completed = []

        for milestone in available_milestones:
            if self._check_milestone_conditions(milestone=milestone):
                MilestoneLog.objects.create(
                    savegame=self.savegame, milestone=milestone, accomplished_at=self.savegame.current_year
                )
                newly_completed.append(milestone)

        return newly_completed
