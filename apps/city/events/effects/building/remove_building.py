from apps.city.models import Building, BuildingType, Tile


class RemoveBuilding:
    building: Tile

    def __init__(self, *, tile: Tile):
        self.tile = tile

    def process(self, *, savegame=None):
        # Replace the building with ruins instead of removing it entirely
        # This ensures that damaged buildings leave ruins that need to be demolished
        ruins_type, _ = BuildingType.objects.get_or_create(
            type=BuildingType.Type.RUINS,
            defaults={
                "name": "Ruins",
                "is_country": False,
                "is_city": False,
                "is_house": False,
                "is_wall": False,
                "is_unique": False,
            },
        )
        # Ensure allowed_terrains is set after creation
        if not ruins_type.allowed_terrains.exists():
            from apps.city.models import Terrain

            ruins_type.allowed_terrains.set(Terrain.objects.all())

        ruins, _ = Building.objects.get_or_create(
            building_type=ruins_type,
            defaults={
                "name": "Ruins",
                "level": 1,
                "taxes": 0,
                "building_costs": 0,
                "demolition_costs": 20,
                "maintenance_costs": 0,
                "housing_space": 0,
            },
        )
        self.tile.building = ruins
        self.tile.save()
