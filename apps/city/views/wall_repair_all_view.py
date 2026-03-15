from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.services.wall.repair_all import WallRepairAllService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class WallRepairAllView(SavegameRequiredMixin, generic.View):
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()

        try:
            WallRepairAllService(savegame=savegame).process()
        except ValueError as e:
            return HttpResponse(str(e), status=HTTPStatus.BAD_REQUEST)

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Refresh"] = "true"
        return response
