import json
from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.models import Tile
from apps.city.services.wall.enclosure import WallEnclosureService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class TileDemolishView(SavegameRequiredMixin, generic.View):
    def post(self, request, pk, *args, **kwargs) -> HttpResponse:
        tile = Tile.objects.get(pk=pk)
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()

        # Check if building can be demolished
        if tile.building:
            # Allow ruins to be demolished, but not other unique buildings
            is_ruins = tile.building.building_type.type == tile.building.building_type.Type.RUINS
            if tile.building.building_type.is_unique and not is_ruins:
                # TODO(RV): give user proper feedback
                return HttpResponse("Cannot demolish unique buildings", status=400)

            # Check if player has enough coins for demolition
            if tile.building.demolition_costs > savegame.coins:
                return HttpResponse("Not enough coins to demolish this building", status=400)

            # Charge demolition costs
            if tile.building.demolition_costs > 0:
                savegame.coins -= tile.building.demolition_costs
                savegame.save()

            # Remove the building
            tile.building = None
            tile.save()

            # Update enclosure status
            if savegame:
                savegame.is_enclosed = WallEnclosureService(savegame=savegame).process()
                savegame.save()

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = json.dumps(
            {
                "refreshMap": "-",
                "updateNavbarValues": "-",
            }
        )
        return response
