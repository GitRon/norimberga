from apps.city.models import Savegame


def get_current_savegame(request) -> dict:
    if hasattr(request, "user") and request.user.is_authenticated:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        if not savegame:
            # Create a default savegame if user has none
            savegame = Savegame.objects.create(user=request.user, city_name="New City", is_active=True)
    else:
        # For unauthenticated users or backward compatibility
        savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"user_id": 1, "city_name": "Default City"})
    return {"savegame": savegame}
