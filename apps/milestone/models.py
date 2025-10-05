from django.db import models

from apps.city.models import Savegame


class Milestone(models.Model):
    """
    Global milestone definition that applies to all savegames.
    Organized in a tree structure with parent-child relationships.
    """

    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Description", blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Parent milestone that must be completed before this one becomes available",
    )
    order = models.PositiveSmallIntegerField("Order", default=0, help_text="Display order within the same level")

    class Meta:
        default_related_name = "milestones"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class MilestoneCondition(models.Model):
    """
    Links a milestone to a condition class with a specific value.
    A milestone can have multiple conditions that all must be met.
    """

    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    condition_class = models.CharField(
        "Condition class",
        max_length=200,
        help_text="Python class path (e.g., 'apps.milestone.conditions.population.MinPopulationCondition')",
    )
    value = models.CharField("Value", max_length=100, help_text="Value to pass to the condition class")

    class Meta:
        default_related_name = "milestone_conditions"

    def __str__(self) -> str:
        return f"{self.milestone.name}: {self.condition_class}({self.value})"


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
