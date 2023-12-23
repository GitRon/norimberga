from django.contrib import admin

from apps.city.models import Building, Savegame, Tile, TileType


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
