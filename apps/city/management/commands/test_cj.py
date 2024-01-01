from django.core.management.base import BaseCommand

from apps.city.models import Tile


class Command(BaseCommand):
    def handle(self, *args, **options):
        tile = Tile.objects.filter(x=0, y=0).first()

        print(tile, tile.is_adjacent_to_city_building())
