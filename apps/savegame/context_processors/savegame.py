from apps.savegame.models import Savegame


def get_current_savegame(request) -> dict:
    # Import here to avoid circular imports
    from apps.city.services.building.housing import BuildingHousingService

    savegame = None
    is_enclosed = False
    max_housing_space = 0
    if hasattr(request, "user") and request.user.is_authenticated:
        savegame = (
            Savegame.objects.filter(user=request.user, is_active=True)
            .prefetch_related(
                "tiles__terrain",
                "tiles__building",
                "tiles__building__building_type",
            )
            .first()
        )
        if savegame:
            is_enclosed = savegame.is_enclosed
            max_housing_space = BuildingHousingService(savegame=savegame).calculate_max_space()
    return {"savegame": savegame, "is_enclosed": is_enclosed, "max_housing_space": max_housing_space}
