import pytest
from django.contrib import messages as django_messages

from apps.event.models import EventNotification
from apps.event.services.notification_creation import NotificationCreationService
from apps.event.tests.factories import MockEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_notification_creation_service_creates_notifications():
    """Test that service creates EventNotification records from events."""
    savegame = SavegameFactory.create(current_year=1200)
    event1 = MockEvent(savegame=savegame)
    event2 = MockEvent(savegame=savegame)

    service = NotificationCreationService(savegame=savegame, events=[event1, event2])
    notifications = service.process()

    assert len(notifications) == 2
    assert EventNotification.objects.count() == 2


@pytest.mark.django_db
def test_notification_creation_service_sets_correct_fields():
    """Test that service sets all notification fields correctly."""
    savegame = SavegameFactory.create(current_year=1250)
    event = MockEvent(savegame=savegame)
    event.TITLE = "Test Event Title"
    event.LEVEL = django_messages.SUCCESS

    service = NotificationCreationService(savegame=savegame, events=[event])
    notifications = service.process()

    notification = notifications[0]
    assert notification.savegame == savegame
    assert notification.year == 1250
    assert notification.title == "Test Event Title"
    assert notification.message == "Mock event occurred"
    assert notification.level == EventNotification.Level.SUCCESS
    assert notification.acknowledged is False


@pytest.mark.django_db
def test_notification_creation_service_level_mapping():
    """Test that Django message levels are correctly mapped to EventNotification levels."""
    savegame = SavegameFactory.create()

    level_mappings = [
        (django_messages.INFO, EventNotification.Level.INFO),
        (django_messages.SUCCESS, EventNotification.Level.SUCCESS),
        (django_messages.WARNING, EventNotification.Level.WARNING),
        (django_messages.ERROR, EventNotification.Level.ERROR),
    ]

    for django_level, expected_notification_level in level_mappings:
        event = MockEvent(savegame=savegame)
        event.LEVEL = django_level

        service = NotificationCreationService(savegame=savegame, events=[event])
        notifications = service.process()

        assert notifications[0].level == expected_notification_level

        # Clean up for next iteration
        EventNotification.objects.all().delete()


@pytest.mark.django_db
def test_notification_creation_service_processes_events():
    """Test that service calls event.process() to execute effects."""
    savegame = SavegameFactory.create()

    # Create a mock event with a side effect to track process() calls
    event = MockEvent(savegame=savegame)
    process_called = False

    original_process = event.process

    def mock_process():
        nonlocal process_called
        process_called = True
        return original_process()

    event.process = mock_process

    service = NotificationCreationService(savegame=savegame, events=[event])
    service.process()

    assert process_called


@pytest.mark.django_db
def test_notification_creation_service_with_empty_events_list():
    """Test that service handles empty events list gracefully."""
    savegame = SavegameFactory.create()

    service = NotificationCreationService(savegame=savegame, events=[])
    notifications = service.process()

    assert len(notifications) == 0
    assert EventNotification.objects.count() == 0


@pytest.mark.django_db
def test_notification_creation_service_returns_created_notifications():
    """Test that service returns list of created EventNotification instances."""
    savegame = SavegameFactory.create()
    events = [MockEvent(savegame=savegame) for _ in range(3)]

    service = NotificationCreationService(savegame=savegame, events=events)
    notifications = service.process()

    assert isinstance(notifications, list)
    assert len(notifications) == 3
    assert all(isinstance(n, EventNotification) for n in notifications)
    assert all(n.pk is not None for n in notifications)  # All should be saved to DB


@pytest.mark.django_db
def test_notification_creation_service_unknown_level_defaults_to_info():
    """Test that unknown Django message levels default to INFO."""
    savegame = SavegameFactory.create()
    event = MockEvent(savegame=savegame)
    event.LEVEL = 9999  # Unknown level

    service = NotificationCreationService(savegame=savegame, events=[event])
    notifications = service.process()

    assert notifications[0].level == EventNotification.Level.INFO


@pytest.mark.django_db
def test_notification_creation_service_skips_events_with_no_message():
    """Test that service skips events that return None or empty string from process()."""
    savegame = SavegameFactory.create()

    # Create event that returns None
    event_with_none = MockEvent(savegame=savegame)
    original_process = event_with_none.process

    def mock_process_none():
        original_process()
        return None

    event_with_none.process = mock_process_none

    # Create event that returns empty string
    event_with_empty = MockEvent(savegame=savegame)
    original_process2 = event_with_empty.process

    def mock_process_empty():
        original_process2()
        return ""

    event_with_empty.process = mock_process_empty

    # Create normal event
    normal_event = MockEvent(savegame=savegame)

    service = NotificationCreationService(savegame=savegame, events=[event_with_none, event_with_empty, normal_event])
    notifications = service.process()

    # Only the normal event should create a notification
    assert len(notifications) == 1
    assert EventNotification.objects.count() == 1
