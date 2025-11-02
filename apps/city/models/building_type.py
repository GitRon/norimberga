from django.db import models

from apps.city.models.terrain import Terrain


class BuildingType(models.Model):
    class Type(models.IntegerChoices):
        REGULAR = 1, "Regular"
        RUINS = 2, "Ruins"

    name = models.CharField(max_length=50)
    allowed_terrains = models.ManyToManyField(Terrain, verbose_name="Allowed terrains")
    type = models.IntegerField("Type", choices=Type.choices, default=Type.REGULAR)

    is_country = models.BooleanField("Is country building", default=False)
    is_city = models.BooleanField("Is city building", default=False)
    is_house = models.BooleanField("Is house", default=False)
    is_wall = models.BooleanField("Is Wall", default=False)
    is_unique = models.BooleanField("Is Unique", default=False)

    class Meta:
        default_related_name = "building_types"

    def __str__(self) -> str:
        return f"{self.name}"
