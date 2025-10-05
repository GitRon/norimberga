from django.views import generic

from apps.city.mixins import SavegameRequiredMixin


class MilestoneListView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "milestone/milestone_list.html"
