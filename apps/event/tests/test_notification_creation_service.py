import pytest

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

    service = NotificationCreationService(savegame=savegame, events=[event])
    notifications = service.process()

    notification = notifications[0]
    assert notification.savegame == savegame
    assert notification.year == 1250
    assert notification.title == "Test Event Title"
    assert notification.message == "Mock event occurred"
    assert notification.acknowledged is False


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
