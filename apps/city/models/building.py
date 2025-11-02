from django.core.validators import MinValueValidator
from django.db import models

from apps.city.models.building_type import BuildingType


class Building(models.Model):
    name = models.CharField(max_length=50)
    building_type = models.ForeignKey(BuildingType, verbose_name="Building type", on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField("Level")

    taxes = models.PositiveSmallIntegerField("Taxes", default=0, validators=(MinValueValidator(0),))
    building_costs = models.PositiveSmallIntegerField("Building costs", default=0, validators=(MinValueValidator(0),))
    demolition_costs = models.PositiveSmallIntegerField(
        "Demolition costs", default=0, validators=(MinValueValidator(0),)
    )
    maintenance_costs = models.PositiveSmallIntegerField(
        "Maintenance costs", default=0, validators=(MinValueValidator(0),)
    )
    housing_space = models.PositiveSmallIntegerField("Housing space", default=0, validators=(MinValueValidator(0),))
    defense_value = models.PositiveSmallIntegerField("Defense value", default=0, validators=(MinValueValidator(0),))
    prestige = models.PositiveSmallIntegerField("Prestige", default=0, validators=(MinValueValidator(0),))

    class Meta:
        default_related_name = "buildings"

    def __str__(self) -> str:
        return f"{self.name}"
