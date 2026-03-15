from django.views import generic

from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class SiegeChronicleView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/siege/chronicle.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            context["chronicles"] = savegame.siege_chronicles.all()
        return context
