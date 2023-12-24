from django.contrib import admin

from apps.city.models import Building, Savegame, Terrain, Tile


@admin.register(Savegame)
class SavegameAdmin(admin.ModelAdmin):
    pass


@admin.register(Tile)
class TileAdmin(admin.ModelAdmin):
    pass


@admin.register(Terrain)
class TerrainAdmin(admin.ModelAdmin):
    list_display = ("name", "color_class", "probability")


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "behaviour_type", "building_costs")
