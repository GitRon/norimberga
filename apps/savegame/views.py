from http import HTTPStatus
from pathlib import Path

from django.core.files import File
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from apps.savegame.forms.savegame import SavegameCreateForm
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame
from apps.savegame.selectors.savegame import get_balance_data


class SavegameValueView(generic.DetailView):
    model = Savegame
    template_name = "savegame/partials/_nav_values.html"


class BalanceView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "savegame/balance.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            balance_data = get_balance_data(savegame=savegame)
            context.update(balance_data)
        return context


class SavegameListView(generic.ListView):
    model = Savegame
    template_name = "savegame/savegame_list.html"
    context_object_name = "savegames"

    def get_queryset(self) -> list[Savegame]:
        return Savegame.objects.filter(user=self.request.user).order_by("-id")


class SavegameLoadView(generic.View):
    def post(self, request, pk, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.get(pk=pk, user=request.user)

        # Set all other savegames of this user to inactive
        Savegame.objects.filter(user=request.user).update(is_active=False)

        # Set this savegame to active
        savegame.is_active = True
        savegame.save()

        return HttpResponse(status=HTTPStatus.OK, headers={"HX-Redirect": reverse_lazy("city:landing-page")})


class SavegameCreateView(generic.CreateView):
    model = Savegame
    form_class = SavegameCreateForm
    template_name = "savegame/savegame_create.html"

    def form_valid(self, form) -> HttpResponse:
        # Import here to avoid circular imports
        from apps.city.services.map.generation import MapGenerationService
        from apps.city.services.wall.enclosure import WallEnclosureService
        from apps.coat_of_arms.services.generator import CoatOfArmsGeneratorService

        # Set user before saving
        form.instance.user = self.request.user

        # Save the savegame
        self.object = form.save()

        # Generate coat of arms
        coat_service = CoatOfArmsGeneratorService()
        temp_path = Path(f"temp_coat_of_arms_{self.object.id}.svg")
        coat_service.process(output_path=temp_path)

        # Save the generated coat of arms to the savegame
        with temp_path.open("rb") as f:
            self.object.coat_of_arms.save(f"coat_of_arms_{self.object.id}.svg", File(f), save=False)

        # Clean up temporary file
        temp_path.unlink()

        # Generate map using the service
        service = MapGenerationService(savegame=self.object)
        service.process()

        # Set this as the active savegame and update enclosure status
        Savegame.objects.filter(user=self.request.user).update(is_active=False)
        self.object.is_active = True
        self.object.is_enclosed = WallEnclosureService(savegame=self.object).process()
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse_lazy("city:landing-page")


class SavegameDeleteView(generic.DeleteView):
    model = Savegame
    success_url = reverse_lazy("savegame:savegame-list")

    def get_queryset(self) -> list[Savegame]:
        # Only allow deleting own savegames that are not active
        return Savegame.objects.filter(user=self.request.user, is_active=False)

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        # If HTMX request, return empty response for client-side removal
        if request.headers.get("HX-Request"):
            return HttpResponse(status=HTTPStatus.OK)

        # Otherwise redirect to list view
        return HttpResponseRedirect(self.get_success_url())
