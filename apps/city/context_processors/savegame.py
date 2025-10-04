from apps.city.models import Savegame


def get_current_savegame(request) -> dict:
    savegame, _ = Savegame.objects.get_or_create(id=1)
    return {"savegame": savegame}
