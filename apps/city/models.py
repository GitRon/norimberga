from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.loader import render_to_string


class Savegame(models.Model):
    city_name = models.CharField(max_length=100)
    map_size = models.PositiveSmallIntegerField(default=5)
    coins = models.SmallIntegerField("Coins", default=0)
    population = models.PositiveSmallIntegerField("Population", default=0)
    current_year = models.PositiveSmallIntegerField("Current year", default=1150)

    class Meta:
        default_related_name = "savegames"

    def __str__(self):
        return self.city_name


class Terrain(models.Model):
    """
    Type of country. Determines what you can do on it.
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


class Building(models.Model):
    class BehaviourTypeChoices(models.IntegerChoices):
        IS_COUNTRY = 1, "Country building"
        IS_CITY = 2, "City building"
        IS_WALL = 3, "Type of city wall"

    name = models.CharField(max_length=50)
    behaviour_type = models.PositiveSmallIntegerField("Behaviour type", choices=BehaviourTypeChoices.choices)
    allowed_terrains = models.ManyToManyField(Terrain, verbose_name="Allowed terrains")

    taxes = models.PositiveSmallIntegerField("Taxes", default=0)
    building_costs = models.PositiveSmallIntegerField("Building costs", default=0)
    maintenance_costs = models.PositiveSmallIntegerField("Maintenance costs", default=0)

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
            if self.building.behaviour_type == Building.BehaviourTypeChoices.IS_WALL:
                return render_to_string("city/classes/_tile_city_wall.txt")
            elif self.building.behaviour_type == Building.BehaviourTypeChoices.IS_COUNTRY:
                return render_to_string("city/classes/_tile_country.txt")
            elif self.building.behaviour_type == Building.BehaviourTypeChoices.IS_CITY:
                return render_to_string("city/classes/_tile_city.txt")
            else:
                return ""
        return self.terrain.color_class
