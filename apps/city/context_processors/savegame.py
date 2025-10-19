from apps.city.models import Savegame
from apps.city.services.building.housing import BuildingHousingService


def get_current_savegame(request) -> dict:
    savegame = None
    is_enclosed = False
    max_housing_space = 0
    if hasattr(request, "user") and request.user.is_authenticated:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        if savegame:
            is_enclosed = savegame.is_enclosed
            max_housing_space = BuildingHousingService(savegame=savegame).calculate_max_space()
    return {"savegame": savegame, "is_enclosed": is_enclosed, "max_housing_space": max_housing_space}
