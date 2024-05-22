from django.db import models

from apps.city.models import Savegame


class MilestoneLog(models.Model):
    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    milestone = models.CharField("Milestone", max_length=100)
    accomplished_at = models.PositiveSmallIntegerField("Finished at", help_text="Accomplished in this year")

    class Meta:
        default_related_name = "quest_logs"

    def __str__(self):
        return self.milestone
