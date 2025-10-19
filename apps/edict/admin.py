from django.contrib import admin

from apps.edict.models import Edict, EdictLog


@admin.register(Edict)
class EdictAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "cost_coins",
        "cost_population",
        "effect_unrest",
        "cooldown_years",
        "is_active",
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]


@admin.register(EdictLog)
class EdictLogAdmin(admin.ModelAdmin):
    list_display = ["edict", "savegame", "activated_at_year", "created_at"]
    list_filter = ["edict", "activated_at_year"]
    search_fields = ["savegame__city_name"]
    raw_id_fields = ["savegame", "edict"]
