import json

import pytest
from django.urls import reverse

from apps.event.models.event_choice import EventChoice
from apps.event.tests.factories import EventChoiceFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_pending_events_view_shows_pending_events(client, django_user_model):
    """Test that the pending events view shows pending events."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    savegame = SavegameFactory(user=user, is_active=True)
    event_choice = EventChoiceFactory(savegame=savegame)
    client.login(username="testuser", password="testpass")

    # Act
    response = client.get(reverse("event:pending"))

    # Assert
    assert response.status_code == 200
    assert event_choice.get_title() in response.content.decode()


@pytest.mark.django_db
def test_pending_events_view_shows_no_events_when_none_pending(client, django_user_model):
    """Test that the view shows nothing when no events are pending."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    SavegameFactory(user=user, is_active=True)
    client.login(username="testuser", password="testpass")

    # Act
    response = client.get(reverse("event:pending"))

    # Assert
    assert response.status_code == 200
    # Template should not show modal when no events
    assert "modal-open" not in response.content.decode()


@pytest.mark.django_db
def test_pending_events_view_only_shows_first_event(client, django_user_model):
    """Test that only the first pending event is shown."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    savegame = SavegameFactory(user=user, is_active=True)
    event_choice_1 = EventChoiceFactory(savegame=savegame)
    EventChoiceFactory(savegame=savegame)  # Second event
    client.login(username="testuser", password="testpass")

    # Act
    response = client.get(reverse("event:pending"))

    # Assert
    assert response.status_code == 200
    content = response.content.decode()
    # Should only have one modal
    assert content.count("modal-open") == 1
    # Should show first event
    assert event_choice_1.get_title() in content


@pytest.mark.django_db
def test_event_choice_select_view_applies_choice(client, django_user_model):
    """Test that selecting a choice applies its effects."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    savegame = SavegameFactory(user=user, is_active=True, coins=100)
    event_choice = EventChoiceFactory(savegame=savegame)
    client.login(username="testuser", password="testpass")

    # Act - Select the "good choice" which adds 100 coins
    response = client.post(
        reverse("event:select-choice", kwargs={"pk": event_choice.id}),
        data={"choice_index": 0},
    )

    # Assert
    assert response.status_code == 200
    savegame.refresh_from_db()
    assert savegame.coins == 200  # 100 initial + 100 from choice


@pytest.mark.django_db
def test_event_choice_select_view_deletes_event_choice(client, django_user_model):
    """Test that selecting a choice deletes the EventChoice record."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    savegame = SavegameFactory(user=user, is_active=True)
    event_choice = EventChoiceFactory(savegame=savegame)
    client.login(username="testuser", password="testpass")

    # Act
    client.post(
        reverse("event:select-choice", kwargs={"pk": event_choice.id}),
        data={"choice_index": 0},
    )

    # Assert
    assert not EventChoice.objects.filter(id=event_choice.id).exists()


@pytest.mark.django_db
def test_event_choice_select_view_triggers_next_event_if_more_pending(client, django_user_model):
    """Test that HTMX trigger is sent to show next event if more are pending."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    savegame = SavegameFactory(user=user, is_active=True)
    event_choice_1 = EventChoiceFactory(savegame=savegame)
    EventChoiceFactory(savegame=savegame)  # Second event
    client.login(username="testuser", password="testpass")

    # Act
    response = client.post(
        reverse("event:select-choice", kwargs={"pk": event_choice_1.id}),
        data={"choice_index": 0},
    )

    # Assert
    assert response.status_code == 200
    triggers = json.loads(response["HX-Trigger"])
    assert "showPendingEvents" in triggers


@pytest.mark.django_db
def test_event_choice_select_view_no_trigger_when_no_more_pending(client, django_user_model):
    """Test that no showPendingEvents trigger is sent when no more events pending."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    savegame = SavegameFactory(user=user, is_active=True)
    event_choice = EventChoiceFactory(savegame=savegame)  # Only one event
    client.login(username="testuser", password="testpass")

    # Act
    response = client.post(
        reverse("event:select-choice", kwargs={"pk": event_choice.id}),
        data={"choice_index": 0},
    )

    # Assert
    assert response.status_code == 200
    triggers = json.loads(response["HX-Trigger"])
    assert "showPendingEvents" not in triggers


@pytest.mark.django_db
def test_event_choice_select_view_invalid_choice_index(client, django_user_model):
    """Test that invalid choice index returns bad request."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    savegame = SavegameFactory(user=user, is_active=True)
    event_choice = EventChoiceFactory(savegame=savegame)
    client.login(username="testuser", password="testpass")

    # Act - Select invalid choice index (only 0 and 1 exist)
    response = client.post(
        reverse("event:select-choice", kwargs={"pk": event_choice.id}),
        data={"choice_index": 99},
    )

    # Assert
    assert response.status_code == 400


@pytest.mark.django_db
def test_event_choice_select_view_nonexistent_event(client, django_user_model):
    """Test that accessing a non-existent event returns 404."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    SavegameFactory(user=user, is_active=True)
    client.login(username="testuser", password="testpass")

    # Act
    response = client.post(
        reverse("event:select-choice", kwargs={"pk": 99999}),
        data={"choice_index": 0},
    )

    # Assert
    assert response.status_code == 404


@pytest.mark.django_db
def test_event_choice_select_view_applies_second_choice(client, django_user_model):
    """Test that selecting the second choice applies its effects."""
    # Arrange
    user = django_user_model.objects.create_user(username="testuser", password="testpass")
    savegame = SavegameFactory(user=user, is_active=True, coins=100)
    event_choice = EventChoiceFactory(savegame=savegame)
    client.login(username="testuser", password="testpass")

    # Act - Select the "bad choice" which removes 50 coins
    response = client.post(
        reverse("event:select-choice", kwargs={"pk": event_choice.id}),
        data={"choice_index": 1},
    )

    # Assert
    assert response.status_code == 200
    savegame.refresh_from_db()
    assert savegame.coins == 50  # 100 initial - 50 from choice
