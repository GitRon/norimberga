from apps.city.models import Savegame


def get_current_savegame(request) -> dict:
    savegame = None
    if hasattr(request, "user") and request.user.is_authenticated:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
    return {"savegame": savegame}
