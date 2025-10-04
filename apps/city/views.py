import json
from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.urls import reverse_lazy
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
        context["max_housing_space"] = BuildingHousingService(savegame=self.object).calculate_max_space()
        return context


class LandingPageView(generic.TemplateView):
    template_name = "city/landing_page.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # TODO(RV): move to context processor
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            context["max_housing_space"] = BuildingHousingService(savegame=savegame).calculate_max_space()
        return context


class CityMapView(generic.TemplateView):
    template_name = "city/partials/city/_city_map.html"


class CityMessagesView(generic.TemplateView):
    template_name = "city/partials/city/_messages.html"


class BalanceView(generic.TemplateView):
    template_name = "city/balance.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            balance_data = get_balance_data(savegame=savegame)
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
        kwargs["savegame"] = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if not kwargs["savegame"]:
            # Create a default savegame if user has none
            kwargs["savegame"] = Savegame.objects.create(user=self.request.user, city_name="New City", is_active=True)
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        super().form_valid(form=form)

        if form.cleaned_data["building"]:
            savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
            if savegame:
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


class SavegameListView(LoginRequiredMixin, generic.ListView):
    model = Savegame
    template_name = "city/savegame_list.html"
    context_object_name = "savegames"

    def get_queryset(self) -> list[Savegame]:
        return Savegame.objects.filter(user=self.request.user).order_by("-id")


class SavegameLoadView(LoginRequiredMixin, generic.View):
    def post(self, request, pk, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.get(pk=pk, user=request.user)

        # Set all other savegames of this user to inactive
        Savegame.objects.filter(user=request.user).update(is_active=False)

        # Set this savegame to active
        savegame.is_active = True
        savegame.save()

        return HttpResponse(status=HTTPStatus.OK, headers={"HX-Redirect": reverse_lazy("city:landing-page")})


class SavegameDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Savegame
    success_url = reverse_lazy("city:savegame-list")

    def get_queryset(self) -> list[Savegame]:
        # Only allow deleting own savegames that are not active
        return Savegame.objects.filter(user=self.request.user, is_active=False)


class UserLoginView(LoginView):
    template_name = "city/login.html"
    next_page = reverse_lazy("city:landing-page")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("city:login")
