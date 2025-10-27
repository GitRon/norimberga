import pytest
from django.urls import reverse

from apps.edict.models import EdictLog
from apps.edict.tests.factories import EdictFactory
from apps.edict.views import EdictListView
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_edict_list_view_get_context_data_with_savegame(request_factory, user):
    from apps.edict.models import Edict

    SavegameFactory(user=user, is_active=True)
    Edict.objects.all().delete()
    EdictFactory.create()

    request = request_factory.get("/")
    request.user = user

    view = EdictListView()
    view.request = request

    context = view.get_context_data()

    assert "edicts" in context
    assert len(context["edicts"]) == 1


@pytest.mark.django_db
def test_edict_list_view_includes_availability_information(request_factory, user):
    from apps.edict.models import Edict

    SavegameFactory(user=user, is_active=True, coins=500)
    Edict.objects.all().delete()
    edict = EdictFactory(cost_coins=100)

    request = request_factory.get("/")
    request.user = user

    view = EdictListView()
    view.request = request

    context = view.get_context_data()

    edict_data = context["edicts"][0]
    assert edict_data["edict"] == edict
    assert edict_data["is_available"] is True
    assert edict_data["can_afford"] is True


@pytest.mark.django_db
def test_edict_activate_view_activates_edict_successfully(authenticated_client, user):
    savegame = SavegameFactory(user=user, is_active=True, coins=500, unrest=50)
    edict = EdictFactory(cost_coins=100, effect_unrest=-10)

    response = authenticated_client.post(reverse("edict:edict-activate", kwargs={"pk": edict.pk}))

    assert response.status_code == 200
    savegame.refresh_from_db()
    assert savegame.coins == 400
    assert savegame.unrest == 40


@pytest.mark.django_db
def test_edict_activate_view_creates_edict_log(authenticated_client, user):
    savegame = SavegameFactory(user=user, is_active=True, current_year=1200)
    edict = EdictFactory.create()

    authenticated_client.post(reverse("edict:edict-activate", kwargs={"pk": edict.pk}))

    log = EdictLog.objects.filter(savegame=savegame, edict=edict).first()
    assert log is not None
    assert log.activated_at_year == 1200


@pytest.mark.django_db
def test_edict_activate_view_returns_htmx_redirect(authenticated_client, user):
    SavegameFactory(user=user, is_active=True)
    edict = EdictFactory.create()

    response = authenticated_client.post(reverse("edict:edict-activate", kwargs={"pk": edict.pk}))

    assert "HX-Redirect" in response
    assert response["HX-Redirect"] == reverse("edict:edict-list-view")


@pytest.mark.django_db
def test_edict_activate_view_fails_when_not_enough_coins(authenticated_client, user):
    savegame = SavegameFactory(user=user, is_active=True, coins=50)
    edict = EdictFactory(cost_coins=100)

    authenticated_client.post(reverse("edict:edict-activate", kwargs={"pk": edict.pk}))

    savegame.refresh_from_db()
    assert savegame.coins == 50


@pytest.mark.django_db
def test_edict_activate_view_returns_404_for_nonexistent_edict(authenticated_client, user):
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.post(reverse("edict:edict-activate", kwargs={"pk": 99999}))

    assert response.status_code == 404


@pytest.mark.django_db
def test_edict_activate_view_only_accepts_post(authenticated_client, user):
    SavegameFactory(user=user, is_active=True)
    edict = EdictFactory.create()

    response = authenticated_client.get(reverse("edict:edict-activate", kwargs={"pk": edict.pk}))

    assert response.status_code == 405
