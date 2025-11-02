from django.db import models


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
