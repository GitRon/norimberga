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
        acknowledged=False,
    )

    assert notification.savegame == savegame
    assert notification.year == 1200
    assert notification.title == "Fire!"
    assert notification.message == "A fire destroyed several buildings."
    assert notification.acknowledged is False


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

    assert notification.acknowledged is False


@pytest.mark.django_db
def test_event_notification_ordering():
    """Test that notifications are ordered by year."""
    savegame = SavegameFactory.create()

    # Create notifications with different years
    notification2 = EventNotificationFactory.create(savegame=savegame, title="Second", year=1200)
    notification3 = EventNotificationFactory.create(savegame=savegame, title="Third", year=1250)
    notification1 = EventNotificationFactory.create(savegame=savegame, title="First", year=1150)

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
