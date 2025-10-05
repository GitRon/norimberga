from apps.city.models import Savegame


def get_current_savegame(request) -> dict:
    savegame = None
    is_enclosed = False
    if hasattr(request, "user") and request.user.is_authenticated:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        if savegame:
            is_enclosed = savegame.is_enclosed
    return {"savegame": savegame, "is_enclosed": is_enclosed}
