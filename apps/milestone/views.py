from django.views import generic

from apps.milestone.services.milestone_tree import MilestoneTreeService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class MilestoneListView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "milestone/milestone_list.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()

        if not savegame:
            context["milestone_tree"] = []
            return context

        # Use service to build milestone tree
        service = MilestoneTreeService(savegame=savegame)
        context["milestone_tree"] = service.process()

        return context
