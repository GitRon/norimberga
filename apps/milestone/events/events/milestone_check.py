from django.contrib import messages

from apps.event.events.events.base_event import BaseEvent
from apps.milestone.services.milestone_checker import MilestoneCheckerService


class Event(BaseEvent):
    """
    Event that checks for completed milestones at the end of each round.
    This event always runs (probability 100%).
    """

    PROBABILITY = 100
    LEVEL = messages.SUCCESS
    TITLE = "Milestone Achieved!"

    def __init__(self, *, savegame):
        super().__init__(savegame=savegame)
        self.completed_milestones = []

    def get_verbose_text(self) -> str | None:
        if not self.completed_milestones:
            return None

        if len(self.completed_milestones) == 1:
            milestone = self.completed_milestones[0]
            return f"Congratulations! You have achieved the milestone: {milestone.name}"

        milestone_names = ", ".join([m.name for m in self.completed_milestones])
        return f"Congratulations! You have achieved multiple milestones: {milestone_names}"

    def process(self) -> str | None:
        """
        Check for completed milestones and return message if any were completed.
        """
        service = MilestoneCheckerService(savegame=self.savegame)
        self.completed_milestones = service.process()

        if not self.completed_milestones:
            return None

        return self.get_verbose_text()
