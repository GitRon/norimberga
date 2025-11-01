from django.contrib import admin

from apps.event.models import EventNotification


@admin.register(EventNotification)
class EventNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "year", "savegame", "level", "acknowledged", "created_at")
    list_filter = ("level", "acknowledged", "year", "savegame")
    search_fields = ("title", "message", "savegame__city_name")
    list_select_related = ("savegame",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Event Information",
            {
                "fields": ("title", "message", "level", "year"),
            },
        ),
        (
            "Game Context",
            {
                "fields": ("savegame",),
            },
        ),
        (
            "Status",
            {
                "fields": ("acknowledged", "created_at"),
            },
        ),
    )
