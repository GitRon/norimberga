from django.contrib import admin

from apps.event.admin import EventNotificationAdmin
from apps.event.models import EventNotification


def test_event_notification_admin_is_registered():
    """Test that EventNotification is registered in Django admin."""
    assert admin.site.is_registered(EventNotification)


def test_event_notification_admin_configuration():
    """Test EventNotificationAdmin has correct configuration."""
    admin_instance = admin.site._registry[EventNotification]

    assert isinstance(admin_instance, EventNotificationAdmin)
    assert admin_instance.list_display == ("id", "title", "year", "savegame", "level", "acknowledged", "created_at")
    assert admin_instance.list_filter == ("level", "acknowledged", "year", "savegame")
    assert admin_instance.search_fields == ("title", "message", "savegame__city_name")
    assert admin_instance.list_select_related == ("savegame",)
    assert admin_instance.readonly_fields == ("created_at",)
    assert admin_instance.ordering == ("-created_at",)


def test_event_notification_admin_fieldsets():
    """Test EventNotificationAdmin fieldsets structure."""
    admin_instance = admin.site._registry[EventNotification]

    assert len(admin_instance.fieldsets) == 3

    # Event Information section
    assert admin_instance.fieldsets[0][0] == "Event Information"
    assert admin_instance.fieldsets[0][1]["fields"] == ("title", "message", "level", "year")

    # Game Context section
    assert admin_instance.fieldsets[1][0] == "Game Context"
    assert admin_instance.fieldsets[1][1]["fields"] == ("savegame",)

    # Status section
    assert admin_instance.fieldsets[2][0] == "Status"
    assert admin_instance.fieldsets[2][1]["fields"] == ("acknowledged", "created_at")
