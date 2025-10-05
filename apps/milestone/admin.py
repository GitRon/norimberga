from django.contrib import admin

from apps.milestone.models import Milestone, MilestoneCondition, MilestoneLog


class MilestoneConditionInline(admin.TabularInline):
    model = MilestoneCondition
    extra = 1


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "order")
    list_filter = ("parent",)
    search_fields = ("name", "description")
    inlines = [MilestoneConditionInline]


@admin.register(MilestoneLog)
class MilestoneLogAdmin(admin.ModelAdmin):
    list_display = ("milestone", "savegame", "accomplished_at")
    list_filter = ("milestone",)
    search_fields = ("savegame__city_name", "milestone__name")
