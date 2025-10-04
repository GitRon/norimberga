from apps.city.models import Savegame


def get_current_savegame(request) -> dict:
    savegame = None
    if hasattr(request, "user") and request.user.is_authenticated:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        if not savegame:
            # TODO(developer): handle case that we dont have a savegame yet, ie as an unauthenticated user
            # Create a default savegame if user has none
            savegame = Savegame.objects.create(user=request.user, city_name="New City", is_active=True)
    return {"savegame": savegame}
