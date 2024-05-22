from django.views import generic


class MilestoneListView(generic.TemplateView):
    template_name = "milestone/milestone_list.html"
