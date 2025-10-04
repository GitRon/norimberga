from apps.milestone.models import MilestoneLog


class AccomplishMilestone:
    savegame_id: int
    milestone: str
    current_year: int

    def __init__(self, savegame_id: int, milestone: str, current_year: int):
        self.savegame_id = savegame_id
        self.milestone = milestone
        self.current_year = current_year

    def process(self, savegame=None):
        MilestoneLog.objects.create(
            savegame_id=self.savegame_id,
            milestone=self.milestone,
            accomplished_at=self.current_year,
        )
