from django.views import generic

from apps.edict.selectors import get_available_edicts_for_savegame
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class EdictListView(SavegameRequiredMixin, generic.TemplateView):
    """Display list of all edicts with availability status."""

    template_name = "edict/edict_list.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()

        context["edicts"] = get_available_edicts_for_savegame(savegame=savegame)

        return context
