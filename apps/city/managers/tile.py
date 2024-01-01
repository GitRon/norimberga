import typing

from django.db import models
from django.db.models import Q

from apps.city.services.map.coordinates import MapCoordinatesService

if typing.TYPE_CHECKING:
    from apps.city.models import Tile


class TileQuerySet(models.QuerySet):
    def filter_savegame(self, tile: "Tile"):
        return self.filter(savegame=tile.savegame)

    def filter_adjacent_tiles(self, tile: "Tile"):
        adjacent_coordinates = MapCoordinatesService.get_adjacent_coordinates(tile=tile)
        filter_condition = Q(id=-1)
        for coordinates in adjacent_coordinates:
            filter_condition |= Q(x=coordinates.x, y=coordinates.y)

        return self.filter(filter_condition)

    def filter_city_building(self):
        return self.filter(building__building_type__is_city=True)


class TileManager(models.Manager):
    pass


TileManager = TileManager.from_queryset(TileQuerySet)
