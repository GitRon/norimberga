import pytest

from apps.edict.selectors import get_available_edicts_for_savegame
from apps.edict.tests.factories import EdictFactory, EdictLogFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_returns_all_active_edicts():
    from apps.edict.models import Edict

    savegame = SavegameFactory()
    Edict.objects.all().delete()
    edict_1 = EdictFactory(is_active=True, name="Edict A")
    edict_2 = EdictFactory(is_active=True, name="Edict B")
    EdictFactory(is_active=False, name="Inactive Edict")

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert len(result) == 2
    assert result[0]["edict"] == edict_1
    assert result[1]["edict"] == edict_2


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_marks_affordable_edict():
    savegame = SavegameFactory(coins=500, population=100)
    EdictFactory(cost_coins=100, cost_population=50)

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert result[0]["can_afford"] is True
    assert result[0]["is_available"] is True


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_marks_unaffordable_coins():
    from apps.edict.models import Edict

    savegame = SavegameFactory(coins=50)
    Edict.objects.all().delete()
    EdictFactory(cost_coins=100)

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert result[0]["can_afford"] is False
    assert result[0]["is_available"] is True


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_marks_unaffordable_population():
    savegame = SavegameFactory(population=25)
    EdictFactory(cost_population=50)

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert result[0]["can_afford"] is False
    assert result[0]["is_available"] is True


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_marks_edict_on_cooldown():
    from apps.edict.models import Edict

    savegame = SavegameFactory(current_year=1200)
    Edict.objects.all().delete()
    edict = EdictFactory(cooldown_years=3)
    EdictLogFactory(savegame=savegame, edict=edict, activated_at_year=1199)

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert result[0]["is_available"] is False
    assert "2 years remaining" in result[0]["unavailable_reason"]


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_marks_available_after_cooldown():
    savegame = SavegameFactory(current_year=1203)
    edict = EdictFactory(cooldown_years=3)
    EdictLogFactory(savegame=savegame, edict=edict, activated_at_year=1200)

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert result[0]["is_available"] is True
    assert result[0]["unavailable_reason"] is None


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_when_no_previous_activation():
    savegame = SavegameFactory()
    EdictFactory(cooldown_years=3)

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert result[0]["is_available"] is True
    assert result[0]["unavailable_reason"] is None


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_when_no_cooldown():
    savegame = SavegameFactory(current_year=1200)
    edict = EdictFactory(cooldown_years=None)
    EdictLogFactory(savegame=savegame, edict=edict, activated_at_year=1199)

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert result[0]["is_available"] is True


@pytest.mark.django_db
def test_get_available_edicts_for_savegame_returns_edicts_ordered_by_name():
    from apps.edict.models import Edict

    savegame = SavegameFactory()
    Edict.objects.all().delete()
    edict_z = EdictFactory(name="Zulu Edict")
    edict_a = EdictFactory(name="Alpha Edict")

    result = get_available_edicts_for_savegame(savegame=savegame)

    assert result[0]["edict"] == edict_a
    assert result[1]["edict"] == edict_z
