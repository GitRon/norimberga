from django.views import generic

from apps.city.services.defense.calculation import DefenseCalculationService
from apps.city.services.prestige import PrestigeCalculationService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame
from apps.thread.services.thread_checker import ThreadCheckerService


class ThreadsView(SavegameRequiredMixin, generic.TemplateView):
    """Main threads view with tabs for Defense, Prestige, and Active Threads."""

    template_name = "thread/threads.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()

        if savegame:
            # Get defense data
            defense_service = DefenseCalculationService(savegame=savegame)
            breakdown = defense_service.get_breakdown()
            context["breakdown"] = breakdown

            # Get prestige data
            prestige_service = PrestigeCalculationService(savegame=savegame)
            total_prestige = prestige_service.process()

            tiles_with_prestige = (
                savegame.tiles.filter(building__isnull=False, building__prestige__gt=0)
                .select_related("building")
                .order_by("-building__prestige")
            )

            prestige_breakdown = [
                {
                    "building_name": tile.building.name,
                    "level": tile.building.level,
                    "prestige": tile.building.prestige,
                    "x": tile.x,
                    "y": tile.y,
                }
                for tile in tiles_with_prestige
            ]

            context["total_prestige"] = total_prestige
            context["prestige_breakdown"] = prestige_breakdown

            # Get active threads
            thread_checker = ThreadCheckerService(savegame=savegame)
            active_threads = thread_checker.process()
            context["active_threads"] = active_threads

        return context


class DefenseTabView(SavegameRequiredMixin, generic.TemplateView):
    """Partial view for defense tab content."""

    template_name = "thread/partials/_defense_tab.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()

        if savegame:
            defense_service = DefenseCalculationService(savegame=savegame)
            breakdown = defense_service.get_breakdown()
            context["breakdown"] = breakdown

        return context


class PrestigeTabView(SavegameRequiredMixin, generic.TemplateView):
    """Partial view for prestige tab content."""

    template_name = "thread/partials/_prestige_tab.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()

        if savegame:
            prestige_service = PrestigeCalculationService(savegame=savegame)
            total_prestige = prestige_service.process()

            tiles_with_prestige = (
                savegame.tiles.filter(building__isnull=False, building__prestige__gt=0)
                .select_related("building")
                .order_by("-building__prestige")
            )

            prestige_breakdown = [
                {
                    "building_name": tile.building.name,
                    "level": tile.building.level,
                    "prestige": tile.building.prestige,
                    "x": tile.x,
                    "y": tile.y,
                }
                for tile in tiles_with_prestige
            ]

            context["total_prestige"] = total_prestige
            context["prestige_breakdown"] = prestige_breakdown

        return context


class ThreadsTabView(SavegameRequiredMixin, generic.TemplateView):
    """Partial view for active threads tab content."""

    template_name = "thread/partials/_threads_tab.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()

        if savegame:
            thread_checker = ThreadCheckerService(savegame=savegame)
            active_threads = thread_checker.process()
            context["active_threads"] = active_threads

        return context
