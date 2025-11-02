from unittest import mock

import pytest
from django.urls import reverse

from apps.milestone.tests.factories import MilestoneFactory
from apps.milestone.views import MilestoneListView
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_milestone_list_view_get_context_data_with_savegame(request_factory, user):
    """Test MilestoneListView includes milestone tree in context when savegame exists."""
    savegame = SavegameFactory(user=user, is_active=True)
    milestone = MilestoneFactory.create()

    request = request_factory.get("/")
    request.user = user

    with mock.patch("apps.milestone.views.milestone_list_view.MilestoneTreeService") as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.process.return_value = [{"milestone": milestone, "children": []}]

        view = MilestoneListView()
        view.request = request

        context = view.get_context_data()

        assert "milestone_tree" in context
        assert len(context["milestone_tree"]) == 1
        assert context["milestone_tree"][0]["milestone"] == milestone
        mock_service.assert_called_once_with(savegame=savegame)
        mock_instance.process.assert_called_once()


@pytest.mark.django_db
def test_milestone_list_view_get_context_data_without_savegame(request_factory, user):
    """Test MilestoneListView returns empty tree when no savegame exists."""
    request = request_factory.get("/")
    request.user = user

    view = MilestoneListView()
    view.request = request

    context = view.get_context_data()

    assert "milestone_tree" in context
    assert context["milestone_tree"] == []


@pytest.mark.django_db
def test_milestone_list_view_response(authenticated_client, user):
    """Test MilestoneListView responds correctly."""
    SavegameFactory(user=user, is_active=True)

    with mock.patch("apps.milestone.views.milestone_list_view.MilestoneTreeService"):
        response = authenticated_client.get(reverse("milestone:milestone-list-view"))

        assert response.status_code == 200
        assert "milestone/milestone_list.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_milestone_list_view_template_name():
    """Test MilestoneListView uses correct template."""
    view = MilestoneListView()
    assert view.template_name == "milestone/milestone_list.html"
