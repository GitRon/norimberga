from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.city.models import Savegame
from apps.city.services.map.generation import MapGenerationService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--savegame-id",
            type=int,
            default=None,
            help="ID of the savegame to generate the map for (optional)",
        )

    def handle(self, *args, **options):
        savegame_id = options["savegame_id"]
        if savegame_id:
            savegame = Savegame.objects.get(id=savegame_id)
        else:
            # Create new savegame without specifying ID - need a user first
            user, _ = User.objects.get_or_create(username="admin", defaults={"is_staff": True, "is_superuser": True})
            savegame = Savegame.objects.create(user=user)
        service = MapGenerationService(savegame=savegame)
        service.process()
