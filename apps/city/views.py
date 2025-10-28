import json
import typing
from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.forms.tile import TileBuildingForm
from apps.city.models import Tile
from apps.city.services.defense.calculation import DefenseCalculationService
from apps.city.services.wall.enclosure import WallEnclosureService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame
from apps.savegame.selectors.savegame import get_balance_data

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet


class BalanceView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/balance.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            balance_data = get_balance_data(savegame=savegame)
            context.update(balance_data)
        return context


class DefensesView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/defenses.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            defense_service = DefenseCalculationService(savegame=savegame)
            breakdown = defense_service.get_breakdown()
            context["breakdown"] = breakdown
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
