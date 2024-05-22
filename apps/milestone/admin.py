from django.contrib import admin

from apps.milestone.models import MilestoneLog


@admin.register(MilestoneLog)
class MilestoneLogAdmin(admin.ModelAdmin):
    list_display = ("milestone", "savegame", "accomplished_at")
