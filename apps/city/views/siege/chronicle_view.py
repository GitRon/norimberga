from django.views import generic

from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.selectors.savegame import get_active_savegame_for_user


class SiegeChronicleView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/siege/chronicle.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = get_active_savegame_for_user(user=self.request.user)
        if savegame:
            context["chronicles"] = savegame.siege_chronicles.all()
        return context
