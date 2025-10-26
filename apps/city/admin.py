from django.contrib import admin

from apps.city.models import Building, BuildingType, Terrain, Tile


@admin.register(Tile)
class TileAdmin(admin.ModelAdmin):
    list_display = ("id", "x", "y", "savegame", "terrain", "building")
    list_filter = ("savegame", "terrain", "building__building_type")
    search_fields = ("savegame__city_name", "x", "y")
    list_select_related = ("savegame", "terrain", "building", "building__building_type")


@admin.register(Terrain)
class TerrainAdmin(admin.ModelAdmin):
    list_display = ("name", "color_class", "probability", "is_water")


class BuildingInline(admin.TabularInline):
    model = Building
    fields = ("name", "level", "taxes", "building_costs", "maintenance_costs", "housing_space")


@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_country", "is_city", "is_house", "is_wall", "is_unique")
    list_filter = ("is_country", "is_city", "is_house", "is_wall", "is_unique")
    inlines = (BuildingInline,)
