import json
from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.forms.tile import TileBuildingForm
from apps.city.models import Savegame, Tile
from apps.city.selectors.savegame import get_balance_data
from apps.city.services.building.housing import BuildingHousingService
from apps.city.services.wall.enclosure import WallEnclosureService


class SavegameValueView(generic.DetailView):
    model = Savegame
    template_name = "savegame/partials/_nav_values.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["max_housing_space"] = BuildingHousingService().calculate_max_space()
        return context


class LandingPageView(generic.TemplateView):
    template_name = "city/landing_page.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # TODO(RV): move to context processor
        context["max_housing_space"] = BuildingHousingService().calculate_max_space()
        return context


class CityMapView(generic.TemplateView):
    template_name = "city/partials/city/_city_map.html"


class CityMessagesView(generic.TemplateView):
    template_name = "city/partials/city/_messages.html"


class BalanceView(generic.TemplateView):
    template_name = "city/balance.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        balance_data = get_balance_data(savegame_id=1)
        context.update(balance_data)
        return context


class TileBuildView(generic.UpdateView):
    model = Tile
    form_class = TileBuildingForm
    template_name = "city/partials/tile/update_tile.html"

    def post(self, request, *args, **kwargs) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["savegame"], _ = Savegame.objects.get_or_create(id=1)
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        super().form_valid(form=form)

        if form.cleaned_data["building"]:
            savegame, _ = Savegame.objects.get_or_create(id=1)
            savegame.coins -= form.cleaned_data["building"].building_costs
            savegame.is_enclosed = WallEnclosureService(savegame).process()
            savegame.save()

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = json.dumps(
            {
                "refreshMap": "-",
                "updateNavbarValues": "-",
            }
        )
        return response

    def get_success_url(self) -> None:
        return None


class TileDemolishView(generic.View):
    def post(self, request, pk, *args, **kwargs) -> HttpResponse:
        tile = Tile.objects.get(pk=pk)

        # Check if building can be demolished
        if tile.building and tile.building.building_type.is_unique:
            # TODO(RV): give user proper feedback
            return HttpResponse("Cannot demolish unique buildings", status=400)

        # Remove the building
        if tile.building:
            tile.building = None
            tile.save()

            # Update enclosure status
            savegame, _ = Savegame.objects.get_or_create(id=1)
            savegame.is_enclosed = WallEnclosureService(savegame).process()
            savegame.save()

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = json.dumps(
            {
                "refreshMap": "-",
                "updateNavbarValues": "-",
            }
        )
        return response
