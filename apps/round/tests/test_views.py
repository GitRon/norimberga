import json
from unittest import mock

import pytest
from django.contrib import messages
from django.urls import reverse

from apps.round.views import RoundView


# RoundView Tests
@pytest.mark.django_db
def test_round_view_http_method_names():
    """Test RoundView only allows POST method."""
    view = RoundView()
    assert view.http_method_names == ("post",)


@pytest.mark.django_db
def test_round_view_post_with_events(request_factory):
    """Test RoundView processes events and adds messages."""
    from apps.savegame.tests.factories import SavegameFactory, UserFactory

    # Create user and savegame
    user = UserFactory()
    savegame = SavegameFactory(user=user, is_active=True)

    # Create mock events
    mock_event1 = mock.Mock()
    mock_event1.process.return_value = "Event 1 happened"
    mock_event1.LEVEL = messages.INFO
    mock_event1.TITLE = "Event 1"

    mock_event2 = mock.Mock()
    mock_event2.process.return_value = "Event 2 happened"
    mock_event2.LEVEL = messages.WARNING
    mock_event2.TITLE = "Event 2"

    events = [mock_event1, mock_event2]

    # Mock EventSelectionService
    with mock.patch("apps.round.views.EventSelectionService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.process.return_value = events

        # Create request and view
        request = request_factory.post("/")
        request.user = user  # Add user to request
        view = RoundView()
        view.request = request

        # Mock messages framework
        with mock.patch("apps.round.views.messages") as mock_messages:
            response = view.post(request)

            # Verify service was called with savegame keyword argument
            mock_service.assert_called_once_with(savegame=savegame)
            mock_service_instance.process.assert_called_once()

            # Verify events were processed
            mock_event1.process.assert_called_once()
            mock_event2.process.assert_called_once()

            # Verify messages were added
            assert mock_messages.add_message.call_count == 2
            mock_messages.add_message.assert_any_call(
                request, mock_event1.LEVEL, "Event 1 happened", extra_tags="Event 1"
            )
            mock_messages.add_message.assert_any_call(
                request, mock_event2.LEVEL, "Event 2 happened", extra_tags="Event 2"
            )

            # Verify response
            assert response.status_code == 200
            hx_trigger = json.loads(response["HX-Trigger"])
            assert "reloadMessages" in hx_trigger
            assert "refreshMap" in hx_trigger
            assert "updateNavbarValues" in hx_trigger


@pytest.mark.django_db
def test_round_view_post_with_no_events(request_factory):
    """Test RoundView handles case when no events occur."""
    from apps.savegame.tests.factories import SavegameFactory, UserFactory

    # Create user and savegame
    user = UserFactory()
    savegame = SavegameFactory(user=user, is_active=True)

    # Mock EventSelectionService to return empty list
    with mock.patch("apps.round.views.EventSelectionService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.process.return_value = []

        # Create request and view
        request = request_factory.post("/")
        request.user = user  # Add user to request
        view = RoundView()
        view.request = request

        # Mock messages framework
        with mock.patch("apps.round.views.messages") as mock_messages:
            response = view.post(request)

            # Verify service was called with savegame keyword argument
            mock_service.assert_called_once_with(savegame=savegame)
            mock_service_instance.process.assert_called_once()

            # Verify quiet year message was added
            mock_messages.add_message.assert_called_once_with(
                request, mock_messages.INFO, "It was a quiet year. Nothing happened out of the ordinary."
            )

            # Verify response
            assert response.status_code == 200
            hx_trigger = json.loads(response["HX-Trigger"])
            assert "reloadMessages" in hx_trigger
            assert "refreshMap" in hx_trigger
            assert "updateNavbarValues" in hx_trigger


@pytest.mark.django_db
def test_round_view_post_response_headers(request_factory):
    """Test RoundView sets correct HTMX trigger headers."""
    from apps.savegame.tests.factories import SavegameFactory, UserFactory

    # Create user and savegame
    user = UserFactory()
    SavegameFactory(user=user, is_active=True)

    # Mock EventSelectionService
    with mock.patch("apps.round.views.EventSelectionService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.process.return_value = []

        # Create request and view
        request = request_factory.post("/")
        request.user = user  # Add user to request
        view = RoundView()
        view.request = request

        # Mock messages framework
        with mock.patch("apps.round.views.messages"):
            response = view.post(request)

            # Verify response headers
            assert response.status_code == 200
            assert "HX-Trigger" in response

            hx_trigger = json.loads(response["HX-Trigger"])
            assert hx_trigger == {
                "reloadMessages": "-",
                "refreshMap": "-",
                "updateNavbarValues": "-",
            }


@pytest.mark.django_db
def test_round_view_post_via_client(authenticated_client, user):
    """Test RoundView responds correctly via Django test client."""
    from apps.savegame.tests.factories import SavegameFactory

    # Create savegame
    SavegameFactory(user=user, is_active=True)

    # Mock EventSelectionService
    with mock.patch("apps.round.views.EventSelectionService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.process.return_value = []

        response = authenticated_client.post(reverse("round:finish"))

        # Verify successful response
        assert response.status_code == 200
        assert "HX-Trigger" in response

        hx_trigger = json.loads(response["HX-Trigger"])
        assert "reloadMessages" in hx_trigger
        assert "refreshMap" in hx_trigger
        assert "updateNavbarValues" in hx_trigger


@pytest.mark.django_db
def test_round_view_get_not_allowed(authenticated_client):
    """Test RoundView rejects GET requests."""
    response = authenticated_client.get(reverse("round:finish"))
    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.django_db
def test_round_view_event_processing_order(request_factory):
    """Test RoundView processes events in the order returned by service."""
    from apps.savegame.tests.factories import SavegameFactory, UserFactory

    # Create user and savegame
    user = UserFactory()
    SavegameFactory(user=user, is_active=True)

    # Create mock events with different processing order
    mock_event1 = mock.Mock()
    mock_event1.process.return_value = "First event"
    mock_event1.LEVEL = messages.INFO
    mock_event1.TITLE = "First"

    mock_event2 = mock.Mock()
    mock_event2.process.return_value = "Second event"
    mock_event2.LEVEL = messages.INFO
    mock_event2.TITLE = "Second"

    events = [mock_event1, mock_event2]

    # Mock EventSelectionService
    with mock.patch("apps.round.views.EventSelectionService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.process.return_value = events

        # Create request and view
        request = request_factory.post("/")
        request.user = user  # Add user to request
        view = RoundView()
        view.request = request

        # Track call order
        call_order = []
        mock_event1.process.side_effect = lambda: call_order.append("event1")
        mock_event2.process.side_effect = lambda: call_order.append("event2")

        # Mock messages framework
        with mock.patch("apps.round.views.messages"):
            view.post(request)

            # Verify events were processed in correct order
            assert call_order == ["event1", "event2"]


@pytest.mark.django_db
def test_round_view_single_event(request_factory):
    """Test RoundView handles single event correctly."""
    from apps.savegame.tests.factories import SavegameFactory, UserFactory

    # Create user and savegame
    user = UserFactory()
    SavegameFactory(user=user, is_active=True)

    # Create single mock event
    mock_event = mock.Mock()
    mock_event.process.return_value = "Single event occurred"
    mock_event.LEVEL = messages.SUCCESS
    mock_event.TITLE = "Single Event"

    events = [mock_event]

    # Mock EventSelectionService
    with mock.patch("apps.round.views.EventSelectionService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.process.return_value = events

        # Create request and view
        request = request_factory.post("/")
        request.user = user  # Add user to request
        view = RoundView()
        view.request = request

        # Mock messages framework
        with mock.patch("apps.round.views.messages") as mock_messages:
            response = view.post(request)

            # Verify single event was processed
            mock_event.process.assert_called_once()

            # Verify single message was added
            mock_messages.add_message.assert_called_once_with(
                request, mock_event.LEVEL, "Single event occurred", extra_tags="Single Event"
            )

            # Should not add quiet year message
            assert mock_messages.add_message.call_count == 1

            # Verify response
            assert response.status_code == 200


@pytest.mark.django_db
def test_round_view_no_active_savegame(request_factory):
    """Test RoundView returns 400 when no active savegame found."""
    from apps.city.tests.factories import UserFactory

    # Create user without active savegame
    user = UserFactory()

    # Create request and view
    request = request_factory.post("/")
    request.user = user
    view = RoundView()
    view.request = request

    response = view.post(request)

    # Verify error response
    assert response.status_code == 400
    assert response.content == b"No active savegame found"


@pytest.mark.django_db
def test_round_view_increments_year(request_factory):
    """Test RoundView increments the current year."""
    from apps.savegame.tests.factories import SavegameFactory, UserFactory

    # Create user and savegame with initial year
    user = UserFactory()
    savegame = SavegameFactory(user=user, is_active=True, current_year=1150)

    # Mock EventSelectionService
    with mock.patch("apps.round.views.EventSelectionService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.process.return_value = []

        # Create request and view
        request = request_factory.post("/")
        request.user = user
        view = RoundView()
        view.request = request

        # Mock messages framework
        with mock.patch("apps.round.views.messages"):
            response = view.post(request)

            # Verify year was incremented
            savegame.refresh_from_db()
            assert savegame.current_year == 1151

            # Verify successful response
            assert response.status_code == 200


@pytest.mark.django_db
def test_round_view_triggers_navbar_update(request_factory):
    """Test RoundView triggers navbar update event."""
    from apps.savegame.tests.factories import SavegameFactory, UserFactory

    # Create user and savegame with initial year
    user = UserFactory()
    savegame = SavegameFactory(user=user, is_active=True, current_year=1150)

    # Mock EventSelectionService
    with mock.patch("apps.round.views.EventSelectionService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.process.return_value = []

        # Create request and view
        request = request_factory.post("/")
        request.user = user
        view = RoundView()
        view.request = request

        # Mock messages framework
        with mock.patch("apps.round.views.messages"):
            response = view.post(request)

            # Verify year was incremented
            savegame.refresh_from_db()
            assert savegame.current_year == 1151

            # Verify updateNavbarValues event is triggered
            assert response.status_code == 200
            hx_trigger = json.loads(response["HX-Trigger"])
            assert "updateNavbarValues" in hx_trigger
