from django.views import generic

from apps.city.services.defense.calculation import DefenseCalculationService
from apps.city.services.wall.condition import WallConditionService
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

            wall_condition = WallConditionService(savegame=savegame).process()
            context["wall_condition"] = wall_condition
        return context
