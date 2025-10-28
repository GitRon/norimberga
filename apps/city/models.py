from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.loader import render_to_string

from apps.city.managers.tile import TileManager
from apps.savegame.models import Savegame


class Terrain(models.Model):
    """
    Type of country. Determines what you can build on it.
    """

    name = models.CharField(max_length=50)
    color_class = models.CharField(
        max_length=20, help_text="Tailwind color for usage in frontend. Example: 'bg-yellow-500'"
    )
    probability = models.PositiveSmallIntegerField(
        "Probability weight", validators=(MaxValueValidator(100), MinValueValidator(1))
    )
    is_water = models.BooleanField("Is water", default=False)

    class Meta:
        default_related_name = "terrains"

    def __str__(self) -> str:
        return self.name


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


class Tile(models.Model):
    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    terrain = models.ForeignKey(Terrain, on_delete=models.CASCADE)
    x = models.PositiveSmallIntegerField()
    y = models.PositiveSmallIntegerField()
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, blank=True, null=True)

    objects = TileManager()

    class Meta:
        unique_together = ("savegame", "x", "y")
        default_related_name = "tiles"

    def __str__(self) -> str:
        return f"{self.x}/{self.y}"

    @property
    def content(self) -> Building | Terrain:
        return self.building if self.building else self.terrain

    def color_class(self) -> str:
        # Tailwind can't detect dynamic classes, therefore, they are safelist-ed
        if self.building:
            if self.building.building_type.is_wall:
                return render_to_string("city/classes/_tile_city_wall.txt")
            elif self.building.building_type.is_country and self.building.building_type.is_city:
                return render_to_string("city/classes/_tile_both.txt")
            elif self.building.building_type.is_country:
                return render_to_string("city/classes/_tile_country.txt")
            else:
                return render_to_string("city/classes/_tile_city.txt")
        return self.terrain.color_class

    def is_adjacent_to_city_building(self) -> bool:
        return Tile.objects.has_adjacent_city_building(tile=self)

    def is_edge_tile(self) -> bool:
        """Check if this tile is on the edge of the map."""
        from apps.city.constants import MAP_SIZE

        max_coord = MAP_SIZE - 1
        return self.x == 0 or self.y == 0 or self.x == max_coord or self.y == max_coord
