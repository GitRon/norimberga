from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.loader import render_to_string

from apps.city.managers.tile import TileManager


class Savegame(models.Model):
    city_name = models.CharField(max_length=100)
    map_size = models.PositiveSmallIntegerField(default=5)
    coins = models.SmallIntegerField("Coins", default=0)
    population = models.PositiveSmallIntegerField("Population", default=0)
    unrest = models.PositiveSmallIntegerField(
        "Unrest", default=0, validators=(MinValueValidator(0), MaxValueValidator(100))
    )
    current_year = models.PositiveSmallIntegerField("Current year", default=1150)

    is_active = models.BooleanField("Is active", default=False)

    class Meta:
        default_related_name = "savegames"

    def __str__(self):
        return self.city_name


class Terrain(models.Model):
    """
    Type of country. Determines what you can build on it.
    """

    name = models.CharField(max_length=50)
    color_class = models.CharField(max_length=20)
    probability = models.PositiveSmallIntegerField(
        "Probability weight", validators=(MaxValueValidator(100), MinValueValidator(1))
    )

    class Meta:
        default_related_name = "terrains"

    def __str__(self):
        return self.name


class BuildingType(models.Model):
    name = models.CharField(max_length=50)
    allowed_terrains = models.ManyToManyField(Terrain, verbose_name="Allowed terrains")

    is_country = models.BooleanField("Is country building", default=False)
    is_city = models.BooleanField("Is city building", default=False)
    is_house = models.BooleanField("Is house", default=False)
    is_wall = models.BooleanField("Is Wall", default=False)
    is_unique = models.BooleanField("Is Unique", default=False)

    class Meta:
        default_related_name = "building_types"

    def __str__(self):
        return f"{self.name}"


class Building(models.Model):
    name = models.CharField(max_length=50)
    building_type = models.ForeignKey(BuildingType, verbose_name="Building type", on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField("Level")

    taxes = models.PositiveSmallIntegerField("Taxes", default=0, validators=(MinValueValidator(0),))
    building_costs = models.PositiveSmallIntegerField("Building costs", default=0, validators=(MinValueValidator(0),))
    maintenance_costs = models.PositiveSmallIntegerField(
        "Maintenance costs", default=0, validators=(MinValueValidator(0),)
    )
    housing_space = models.PositiveSmallIntegerField("Housing space", default=0, validators=(MinValueValidator(0),))

    class Meta:
        default_related_name = "buildings"

    def __str__(self):
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

    def __str__(self):
        return f"{self.x}/{self.y}"

    @property
    def content(self):
        return self.building if self.building else self.terrain

    def color_class(self):
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

    def is_adjacent_to_city_building(self):
        return (
            Tile.objects.filter_savegame(savegame=self.savegame)
            .filter_adjacent_tiles(tile=self)
            .filter_city_building()
            .exists()
        )
