from django.contrib import admin

from apps.savegame.models import Savegame


@admin.register(Savegame)
class SavegameAdmin(admin.ModelAdmin):
    list_display = ("id", "city_name")
