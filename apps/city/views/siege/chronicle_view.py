from django.views import generic

from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.selectors.savegame import get_active_savegame_for_user, get_siege_chronicles


class SiegeChronicleView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/siege/chronicle.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = get_active_savegame_for_user(user=self.request.user)
        context["chronicles"] = get_siege_chronicles(savegame=savegame)
        return context
