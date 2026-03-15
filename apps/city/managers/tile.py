import typing

from django.db import models
from django.db.models import Q

from apps.city.services.map.coordinates import MapCoordinatesService

if typing.TYPE_CHECKING:
    from apps.city.models import Tile
    from apps.savegame.models import Savegame


class TileQuerySet(models.QuerySet):
    def filter_savegame(self, *, savegame: "Savegame") -> models.QuerySet:
        return self.filter(savegame=savegame)

    def filter_adjacent_tiles(self, *, tile: "Tile") -> models.QuerySet:
        service = MapCoordinatesService()
        adjacent_coordinates = service.get_adjacent_coordinates(x=tile.x, y=tile.y)
        filter_condition = Q(id=-1)
        for coordinates in adjacent_coordinates:
            filter_condition |= Q(x=coordinates.x, y=coordinates.y)

        return self.filter(filter_condition)

    def filter_city_building(self) -> models.QuerySet:
        return self.filter(building__building_type__is_city=True)

    def filter_wall_tiles(self) -> models.QuerySet:
        return self.filter(wall_hitpoints__isnull=False).select_related("building", "building__building_type")

    def filter_city_buildings_only(self) -> models.QuerySet:
        return (
            self.filter(building__isnull=False, building__building_type__is_city=True)
            .exclude(building__building_type__is_wall=True)
            .exclude(building__building_type__is_country=True)
        )


class TileManager(models.Manager):
    def has_adjacent_city_building(self, *, tile: "Tile") -> bool:
        """Check if a tile has any adjacent city buildings."""
        return (
            self.filter_savegame(savegame=tile.savegame)
            .filter_adjacent_tiles(tile=tile)
            .filter_city_building()
            .exists()
        )

    def get_random_city_buildings(self, *, savegame: "Savegame", count: int) -> list:
        """Return up to `count` random city (non-wall, non-country) building tiles for a savegame."""
        return list(self.filter(savegame=savegame).filter_city_buildings_only().order_by("?")[:count])


TileManager = TileManager.from_queryset(TileQuerySet)
