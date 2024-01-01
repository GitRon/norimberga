from django.contrib import admin

from apps.city.models import Building, BuildingType, Savegame, Terrain, Tile


@admin.register(Savegame)
class SavegameAdmin(admin.ModelAdmin):
    pass


@admin.register(Tile)
class TileAdmin(admin.ModelAdmin):
    pass


@admin.register(Terrain)
class TerrainAdmin(admin.ModelAdmin):
    list_display = ("name", "color_class", "probability")


class BuildingInline(admin.TabularInline):
    model = Building
    fields = ("name", "level", "taxes", "building_costs", "maintenance_costs", "housing_space")


@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_country", "is_city", "is_house", "is_wall", "is_unique")
    list_filter = ("is_country", "is_city", "is_house", "is_wall", "is_unique")
    inlines = (BuildingInline,)
