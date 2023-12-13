from django.db import models


class Savegame(models.Model):
    city_name = models.CharField(max_length=100)
    map_size = models.PositiveSmallIntegerField(default=5)

    class Meta:
        default_related_name = "savegames"

    def __str__(self):
        return self.city_name


class TileType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        default_related_name = "tile_types"

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        default_related_name = "buildings"

    def __str__(self):
        return self.name


class Tile(models.Model):
    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    tile_type = models.ForeignKey(TileType, on_delete=models.CASCADE)
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
        return self.building if self.building else self.tile_type
