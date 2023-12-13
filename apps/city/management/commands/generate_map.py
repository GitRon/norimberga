from django.core.management.base import BaseCommand

from apps.city.models import Savegame
from apps.city.services.map_generation import MapGenerationService


class Command(BaseCommand):
    def handle(self, *args, **options):
        savegame, _ = Savegame.objects.get_or_create(id=1)
        service = MapGenerationService(savegame=savegame)
        service.process()
