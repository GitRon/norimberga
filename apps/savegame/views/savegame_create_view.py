from pathlib import Path

from django.core.files import File
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from apps.savegame.forms.savegame import SavegameCreateForm
from apps.savegame.models import Savegame


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
