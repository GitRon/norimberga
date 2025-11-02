from django.views import generic

from apps.city.services.defense.calculation import DefenseCalculationService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


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
