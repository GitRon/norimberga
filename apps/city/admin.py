from django.contrib import admin

from apps.city.models import Savegame, Building, TileType, Tile


@admin.register(Savegame)
class SavegameAdmin(admin.ModelAdmin):
    pass


@admin.register(Tile)
class TileAdmin(admin.ModelAdmin):
    pass


@admin.register(TileType)
class TileTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    pass
