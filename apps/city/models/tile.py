from django.db import models
from django.template.loader import render_to_string

from apps.city.managers.tile import TileManager
from apps.city.models.building import Building
from apps.city.models.terrain import Terrain
from apps.savegame.models import Savegame


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
        # Only used for buildings now - terrain uses background images instead
        if self.building:
            if self.building.building_type.is_wall:
                return render_to_string("city/classes/_tile_city_wall.txt")
            elif self.building.building_type.is_country and self.building.building_type.is_city:
                return render_to_string("city/classes/_tile_both.txt")
            elif self.building.building_type.is_country:
                return render_to_string("city/classes/_tile_country.txt")
            else:
                return render_to_string("city/classes/_tile_city.txt")
        return ""

    def terrain_image_url(self) -> str:
        """Return the URL path to the terrain image."""
        from django.templatetags.static import static

        return static(f"img/tiles/{self.terrain.image_filename}")

    def is_adjacent_to_city_building(self) -> bool:
        return Tile.objects.has_adjacent_city_building(tile=self)

    def is_edge_tile(self) -> bool:
        """Check if this tile is on the edge of the map."""
        from apps.city.constants import MAP_SIZE

        max_coord = MAP_SIZE - 1
        return self.x == 0 or self.y == 0 or self.x == max_coord or self.y == max_coord
