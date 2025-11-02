from django.views import generic

from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class PrestigeView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/prestige.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if savegame:
            from apps.city.services.prestige import PrestigeCalculationService

            prestige_service = PrestigeCalculationService(savegame=savegame)
            total_prestige = prestige_service.process()

            # Get breakdown of prestige sources
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
