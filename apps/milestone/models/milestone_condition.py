from django.db import models

from apps.milestone.models.milestone import Milestone


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
