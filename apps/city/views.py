import json
from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.forms.tile import TileBuildingForm
from apps.city.models import Tile
from apps.city.services.wall.enclosure import WallEnclosureService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame
from apps.savegame.selectors.savegame import get_balance_data


class BalanceView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/balance.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            balance_data = get_balance_data(savegame=savegame)
            context.update(balance_data)
        return context


class NavbarValuesView(generic.TemplateView):
    template_name = "partials/_navbar_values.html"


class LandingPageView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/landing_page.html"


class CityMapView(generic.TemplateView):
    template_name = "city/partials/city/_city_map.html"


class CityMessagesView(generic.TemplateView):
    template_name = "city/partials/city/_messages.html"


class TileBuildView(SavegameRequiredMixin, generic.UpdateView):
    model = Tile
    form_class = TileBuildingForm
    template_name = "city/partials/tile/update_tile.html"

    def post(self, request, *args, **kwargs) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["savegame"] = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        super().form_valid(form=form)

        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if form.cleaned_data["building"] and savegame:
            savegame.coins -= form.cleaned_data["building"].building_costs
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

    def get_success_url(self) -> None:
        return None


class TileDemolishView(SavegameRequiredMixin, generic.View):
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
            savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
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
