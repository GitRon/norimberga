import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from django.views import generic

from apps.city.mixins import SavegameRequiredMixin
from apps.city.tests.factories import SavegameFactory, UserFactory


class TestView(SavegameRequiredMixin, generic.TemplateView):
    """Test view that uses SavegameRequiredMixin."""

    template_name = "city/landing_page.html"


@pytest.fixture
def request_factory():
    """Provide Django request factory."""
    return RequestFactory()


# SavegameRequiredMixin Tests
@pytest.mark.django_db
def test_savegame_required_mixin_redirects_without_active_savegame(request_factory):
    """Test SavegameRequiredMixin redirects to savegame list when no active savegame exists."""
    user = UserFactory()
    request = request_factory.get("/")
    request.user = user

    view = TestView()
    response = view.dispatch(request)

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("city:savegame-list")


@pytest.mark.django_db
def test_savegame_required_mixin_redirects_with_inactive_savegame(request_factory):
    """Test SavegameRequiredMixin redirects when user has only inactive savegames."""
    user = UserFactory()
    SavegameFactory(user=user, is_active=False)
    request = request_factory.get("/")
    request.user = user

    view = TestView()
    response = view.dispatch(request)

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("city:savegame-list")


@pytest.mark.django_db
def test_savegame_required_mixin_allows_with_active_savegame(request_factory):
    """Test SavegameRequiredMixin allows access when user has active savegame."""
    user = UserFactory()
    SavegameFactory(user=user, is_active=True)
    request = request_factory.get("/")
    request.user = user

    view = TestView.as_view()
    response = view(request)

    # Response should not be a redirect
    assert not isinstance(response, HttpResponseRedirect)
    assert response.status_code == 200


@pytest.mark.django_db
def test_savegame_required_mixin_allows_unauthenticated_user(request_factory):
    """Test SavegameRequiredMixin doesn't redirect for unauthenticated users."""
    request = request_factory.get("/")
    request.user = AnonymousUser()

    view = TestView.as_view()
    response = view(request)

    # Should not redirect to savegame list (authentication should be handled by LoginRequiredMixin)
    assert not isinstance(response, HttpResponseRedirect) or response.url != reverse("city:savegame-list")


@pytest.mark.django_db
def test_savegame_required_mixin_with_multiple_savegames(request_factory):
    """Test SavegameRequiredMixin works correctly when user has multiple savegames."""
    user = UserFactory()
    SavegameFactory(user=user, is_active=False)
    SavegameFactory(user=user, is_active=False)
    SavegameFactory(user=user, is_active=True)

    request = request_factory.get("/")
    request.user = user

    view = TestView.as_view()
    response = view(request)

    # Should allow access because user has an active savegame
    assert not isinstance(response, HttpResponseRedirect)
    assert response.status_code == 200
