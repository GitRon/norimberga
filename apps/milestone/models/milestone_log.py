from django.db import models

from apps.milestone.models.milestone import Milestone
from apps.savegame.models import Savegame


class MilestoneLog(models.Model):
    """
    Savegame-specific log of accomplished milestones.
    """

    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    accomplished_at = models.PositiveSmallIntegerField("Finished at", help_text="Accomplished in this year")

    class Meta:
        default_related_name = "milestone_logs"
        unique_together = ("savegame", "milestone")

    def __str__(self) -> str:
        return f"{self.savegame.city_name}: {self.milestone.name}"
