from django.contrib import admin

from apps.event.models import EventNotification


@admin.register(EventNotification)
class EventNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "year", "savegame", "acknowledged")
    list_filter = ("acknowledged", "year", "savegame")
    search_fields = ("title", "message", "savegame__city_name")
    list_select_related = ("savegame",)
    ordering = ("-year",)

    fieldsets = (
        (
            "Event Information",
            {
                "fields": ("title", "message", "year"),
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
                "fields": ("acknowledged",),
            },
        ),
    )
