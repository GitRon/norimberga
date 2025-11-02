import pytest

from apps.event.models.event_choice import EventChoice
from apps.event.services.storage import EventChoiceStorageService
from apps.event.tests.factories import MockEvent, MockEventWithChoices
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_storage_service_stores_event_with_choices():
    """Test that the storage service stores events with choices."""
    # Arrange
    savegame = SavegameFactory()
    event = MockEventWithChoices(savegame=savegame)
    service = EventChoiceStorageService(savegame=savegame)

    # Act
    stored_events = service.process(events=[event])

    # Assert
    assert len(stored_events) == 1
    assert EventChoice.objects.count() == 1
    stored = EventChoice.objects.first()
    assert stored.savegame == savegame
    assert stored.event_module == "apps.event.tests.factories"
    assert stored.event_class_name == "MockEventWithChoices"


@pytest.mark.django_db
def test_storage_service_does_not_store_event_without_choices():
    """Test that the storage service does not store events without choices."""
    # Arrange
    savegame = SavegameFactory()
    event = MockEvent(savegame=savegame)  # No choices
    service = EventChoiceStorageService(savegame=savegame)

    # Act
    stored_events = service.process(events=[event])

    # Assert
    assert len(stored_events) == 0
    assert EventChoice.objects.count() == 0


@pytest.mark.django_db
def test_storage_service_stores_multiple_events_with_choices():
    """Test that the storage service stores multiple events with choices."""
    # Arrange
    savegame = SavegameFactory()
    event1 = MockEventWithChoices(savegame=savegame)
    event2 = MockEventWithChoices(savegame=savegame)
    service = EventChoiceStorageService(savegame=savegame)

    # Act
    stored_events = service.process(events=[event1, event2])

    # Assert
    assert len(stored_events) == 2
    assert EventChoice.objects.count() == 2


@pytest.mark.django_db
def test_storage_service_filters_mixed_events():
    """Test that the storage service only stores events with choices from a mixed list."""
    # Arrange
    savegame = SavegameFactory()
    event_with_choices = MockEventWithChoices(savegame=savegame)
    event_without_choices = MockEvent(savegame=savegame)
    service = EventChoiceStorageService(savegame=savegame)

    # Act
    stored_events = service.process(events=[event_with_choices, event_without_choices])

    # Assert
    assert len(stored_events) == 1
    assert EventChoice.objects.count() == 1
    stored = EventChoice.objects.first()
    assert stored.event_class_name == "MockEventWithChoices"


@pytest.mark.django_db
def test_storage_service_handles_empty_list():
    """Test that the storage service handles an empty event list gracefully."""
    # Arrange
    savegame = SavegameFactory()
    service = EventChoiceStorageService(savegame=savegame)

    # Act
    stored_events = service.process(events=[])

    # Assert
    assert len(stored_events) == 0
    assert EventChoice.objects.count() == 0
