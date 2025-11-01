import pytest

from apps.event.models import EventNotification
from apps.event.tests.factories import EventNotificationFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_event_notification_creation():
    """Test that EventNotification can be created with all required fields."""
    savegame = SavegameFactory.create()
    notification = EventNotificationFactory.create(
        savegame=savegame,
        year=1200,
        title="Fire!",
        message="A fire destroyed several buildings.",
        level=EventNotification.Level.ERROR,
        acknowledged=False,
    )

    assert notification.savegame == savegame
    assert notification.year == 1200
    assert notification.title == "Fire!"
    assert notification.message == "A fire destroyed several buildings."
    assert notification.level == EventNotification.Level.ERROR
    assert notification.acknowledged is False
    assert notification.created_at is not None


@pytest.mark.django_db
def test_event_notification_str_representation():
    """Test the string representation of EventNotification."""
    notification = EventNotificationFactory.create(title="Alms", year=1175)

    assert str(notification) == "Alms (Year 1175)"


@pytest.mark.django_db
def test_event_notification_default_values():
    """Test that EventNotification has correct default values."""
    savegame = SavegameFactory.create()
    notification = EventNotification.objects.create(savegame=savegame, year=1150, title="Test", message="Test message")

    assert notification.level == EventNotification.Level.INFO
    assert notification.acknowledged is False


@pytest.mark.django_db
def test_event_notification_ordering():
    """Test that notifications are ordered by created_at."""
    savegame = SavegameFactory.create()

    # Create notifications in reverse order
    notification3 = EventNotificationFactory.create(savegame=savegame, title="Third")
    notification1 = EventNotificationFactory.create(savegame=savegame, title="First")
    notification2 = EventNotificationFactory.create(savegame=savegame, title="Second")

    # Update created_at to ensure specific order
    notification1.created_at = "2024-01-01 10:00:00"
    notification1.save()
    notification2.created_at = "2024-01-01 11:00:00"
    notification2.save()
    notification3.created_at = "2024-01-01 12:00:00"
    notification3.save()

    notifications = savegame.event_notifications.all()

    assert notifications[0] == notification1
    assert notifications[1] == notification2
    assert notifications[2] == notification3


@pytest.mark.django_db
def test_event_notification_acknowledged_filter():
    """Test filtering notifications by acknowledged status."""
    savegame = SavegameFactory.create()

    # Create acknowledged and unacknowledged notifications
    EventNotificationFactory.create(savegame=savegame, acknowledged=True)
    EventNotificationFactory.create(savegame=savegame, acknowledged=False)
    EventNotificationFactory.create(savegame=savegame, acknowledged=False)

    unacknowledged = savegame.event_notifications.filter(acknowledged=False)
    acknowledged = savegame.event_notifications.filter(acknowledged=True)

    assert unacknowledged.count() == 2
    assert acknowledged.count() == 1


@pytest.mark.django_db
def test_event_notification_cascade_delete_on_savegame_deletion():
    """Test that notifications are deleted when savegame is deleted."""
    savegame = SavegameFactory.create()
    EventNotificationFactory.create(savegame=savegame)
    EventNotificationFactory.create(savegame=savegame)

    assert EventNotification.objects.count() == 2

    savegame.delete()

    assert EventNotification.objects.count() == 0


@pytest.mark.django_db
def test_event_notification_level_choices():
    """Test that all level choices can be saved correctly."""
    savegame = SavegameFactory.create()

    for level_value, _level_display in EventNotification.Level.choices:
        notification = EventNotificationFactory.create(savegame=savegame, level=level_value)
        assert notification.level == level_value
