import pytest

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
