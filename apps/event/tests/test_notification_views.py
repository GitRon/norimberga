import pytest
from django.urls import reverse

from apps.event.tests.factories import EventNotificationFactory
from apps.savegame.tests.factories import SavegameFactory


# NotificationBoardView Tests
@pytest.mark.django_db
def test_notification_board_view_displays_first_unacknowledged_notification(authenticated_client, user):
    """Test that NotificationBoardView displays the first unacknowledged notification."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    notification1 = EventNotificationFactory.create(savegame=savegame, title="First", acknowledged=False)
    EventNotificationFactory.create(savegame=savegame, title="Second", acknowledged=False)
    EventNotificationFactory.create(savegame=savegame, title="Third", acknowledged=True)

    response = authenticated_client.get(reverse("event:notification-board"))

    assert response.status_code == 200
    assert response.context["notification"] == notification1
    assert "First" in response.content.decode()


@pytest.mark.django_db
def test_notification_board_view_shows_total_notification_count(authenticated_client, user):
    """Test that NotificationBoardView shows total unacknowledged notification count."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    EventNotificationFactory.create(savegame=savegame, acknowledged=False)
    EventNotificationFactory.create(savegame=savegame, acknowledged=False)
    EventNotificationFactory.create(savegame=savegame, acknowledged=False)
    EventNotificationFactory.create(savegame=savegame, acknowledged=True)  # Should not be counted

    response = authenticated_client.get(reverse("event:notification-board"))

    assert response.status_code == 200
    assert response.context["total_notifications"] == 3


@pytest.mark.django_db
def test_notification_board_view_redirects_when_no_notifications(authenticated_client, user):
    """Test that NotificationBoardView shows redirect script when no notifications exist."""
    SavegameFactory.create(user=user, is_active=True)

    response = authenticated_client.get(reverse("event:notification-board"))

    content = response.content.decode()
    assert response.status_code == 200
    # Check for redirect script in response (template renders JS redirect)
    assert "window.location.href" in content or response.context["notification"] is None


@pytest.mark.django_db
def test_notification_board_view_without_savegame(authenticated_client, user):
    """Test that NotificationBoardView redirects when no active savegame exists."""
    response = authenticated_client.get(reverse("event:notification-board"))

    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


@pytest.mark.django_db
def test_notification_board_view_only_shows_current_savegame_notifications(authenticated_client, user):
    """Test that NotificationBoardView only shows notifications for current savegame."""
    savegame1 = SavegameFactory.create(user=user, is_active=True)
    savegame2 = SavegameFactory.create(user=user, is_active=False)

    notification1 = EventNotificationFactory.create(savegame=savegame1, title="Savegame 1")
    EventNotificationFactory.create(savegame=savegame2, title="Savegame 2")

    response = authenticated_client.get(reverse("event:notification-board"))

    assert response.status_code == 200
    assert response.context["notification"] == notification1
    assert "Savegame 1" in response.content.decode()
    assert "Savegame 2" not in response.content.decode()


@pytest.mark.django_db
def test_notification_board_view_renders_notification_details(authenticated_client, user):
    """Test that NotificationBoardView renders all notification details correctly."""
    savegame = SavegameFactory.create(user=user, is_active=True, current_year=1250)
    EventNotificationFactory.create(
        savegame=savegame,
        year=1250,
        title="Fire!",
        message="A terrible fire ravaged the city.",
    )

    response = authenticated_client.get(reverse("event:notification-board"))

    content = response.content.decode()
    assert response.status_code == 200
    assert "Fire!" in content
    assert "A terrible fire ravaged the city." in content
    assert "1250" in content


# NotificationAcknowledgeView Tests
@pytest.mark.django_db
def test_notification_acknowledge_view_marks_notification_acknowledged(authenticated_client, user):
    """Test that NotificationAcknowledgeView marks notification as acknowledged."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    notification = EventNotificationFactory.create(savegame=savegame, acknowledged=False)

    assert notification.acknowledged is False

    response = authenticated_client.post(reverse("event:notification-acknowledge", args=[notification.pk]))

    notification.refresh_from_db()
    assert notification.acknowledged is True
    assert response.status_code == 200


@pytest.mark.django_db
def test_notification_acknowledge_view_redirects_to_next_notification(authenticated_client, user):
    """Test that view redirects to notification board when more notifications exist."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    notification1 = EventNotificationFactory.create(savegame=savegame, acknowledged=False)
    EventNotificationFactory.create(savegame=savegame, acknowledged=False)

    response = authenticated_client.post(reverse("event:notification-acknowledge", args=[notification1.pk]))

    assert response.status_code == 200
    assert response["HX-Redirect"] == reverse("event:notification-board")


@pytest.mark.django_db
def test_notification_acknowledge_view_redirects_to_city_when_no_more_notifications(authenticated_client, user):
    """Test that view redirects to city when no more unacknowledged notifications exist."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    notification = EventNotificationFactory.create(savegame=savegame, acknowledged=False)

    response = authenticated_client.post(reverse("event:notification-acknowledge", args=[notification.pk]))

    assert response.status_code == 200
    assert response["HX-Redirect"] == reverse("city:landing-page")


@pytest.mark.django_db
def test_notification_acknowledge_view_returns_404_for_wrong_savegame(authenticated_client, user):
    """Test that view returns 404 when notification belongs to different savegame."""
    SavegameFactory.create(user=user, is_active=True)
    other_savegame = SavegameFactory.create(is_active=False)
    notification = EventNotificationFactory.create(savegame=other_savegame)

    response = authenticated_client.post(reverse("event:notification-acknowledge", args=[notification.pk]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_notification_acknowledge_view_without_savegame(authenticated_client, user):
    """Test that view redirects when no active savegame exists (SavegameRequiredMixin)."""
    notification = EventNotificationFactory.create()

    response = authenticated_client.post(reverse("event:notification-acknowledge", args=[notification.pk]))

    # SavegameRequiredMixin redirects to savegame list when no active savegame
    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


@pytest.mark.django_db
def test_notification_acknowledge_view_only_accepts_post(authenticated_client, user):
    """Test that view only accepts POST requests."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    notification = EventNotificationFactory.create(savegame=savegame)

    response = authenticated_client.get(reverse("event:notification-acknowledge", args=[notification.pk]))

    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.django_db
def test_notification_acknowledge_view_ignores_already_acknowledged_notifications(authenticated_client, user):
    """Test that view handles already acknowledged notifications correctly."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    notification = EventNotificationFactory.create(savegame=savegame, acknowledged=True)

    response = authenticated_client.post(reverse("event:notification-acknowledge", args=[notification.pk]))

    notification.refresh_from_db()
    assert notification.acknowledged is True  # Should remain True
    assert response.status_code == 200
