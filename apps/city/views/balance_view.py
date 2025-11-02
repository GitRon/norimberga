from django.views import generic

from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame
from apps.savegame.selectors.savegame import get_balance_data


class BalanceView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/balance.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            balance_data = get_balance_data(savegame=savegame)
            context.update(balance_data)
        return context
