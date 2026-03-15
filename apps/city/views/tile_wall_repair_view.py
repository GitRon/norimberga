import json
from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.models import Tile
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class TileWallRepairView(SavegameRequiredMixin, generic.View):
    http_method_names = ("post",)

    def post(self, request, pk, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        if not savegame:
            return HttpResponse("No active savegame found.", status=HTTPStatus.BAD_REQUEST)

        tile = (
            Tile.objects.select_related("building", "building__building_type").filter(savegame=savegame, pk=pk).first()
        )
        if not tile:
            return HttpResponse("Tile not found.", status=HTTPStatus.NOT_FOUND)

        if not tile.building or not tile.building.building_type.is_wall:
            return HttpResponse("This tile does not have a wall building.", status=HTTPStatus.BAD_REQUEST)

        if tile.wall_hitpoints is None:
            return HttpResponse("This wall tile has no hitpoints to repair.", status=HTTPStatus.BAD_REQUEST)

        repair_cost = tile.wall_repair_cost
        if not repair_cost:
            return HttpResponse("This wall is already at full health.", status=HTTPStatus.BAD_REQUEST)

        if savegame.coins < repair_cost:
            return HttpResponse(f"Not enough coins. Repair costs {repair_cost} coins.", status=HTTPStatus.BAD_REQUEST)

        savegame.coins -= repair_cost
        savegame.save()

        tile.wall_hitpoints = tile.wall_hitpoints_max
        tile.save()

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = json.dumps(
            {
                "refreshMap": "-",
                "updateNavbarValues": "-",
            }
        )
        return response
