import json
import typing
from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.forms.tile import TileBuildingForm
from apps.city.models import Tile
from apps.city.services.wall.enclosure import WallEnclosureService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet


class TileBuildView(SavegameRequiredMixin, generic.UpdateView):
    model = Tile
    form_class = TileBuildingForm
    template_name = "city/partials/tile/update_tile.html"

    def get_queryset(self) -> "QuerySet[Tile]":
        # Optimize tile fetching by prefetching related objects
        return Tile.objects.select_related("terrain", "building", "building__building_type", "savegame")

    def post(self, request, *args, **kwargs) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["savegame"] = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        old_building = form.initial.get("current_building")
        super().form_valid(form=form)

        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            # Charge building costs when building
            if form.cleaned_data["building"]:
                savegame.coins -= form.cleaned_data["building"].building_costs

            # Charge demolition costs when demolishing
            if old_building and not form.cleaned_data["building"]:
                savegame.coins -= old_building.demolition_costs

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

    def form_invalid(self, form) -> HttpResponse:
        # Re-render the form with validation errors
        # Modal stays open so user can see the error messages
        return super().form_invalid(form)

    def get_success_url(self) -> None:
        return None
