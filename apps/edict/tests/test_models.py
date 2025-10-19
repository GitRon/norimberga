import pytest

from apps.edict.tests.factories import EdictFactory, EdictLogFactory


@pytest.mark.django_db
def test_edict_str_returns_name():
    edict = EdictFactory(name="Give Bread to the Poor")

    assert str(edict) == "Give Bread to the Poor"


@pytest.mark.django_db
def test_edict_ordering_by_name():
    edict_z = EdictFactory(name="Zulu Edict")
    edict_a = EdictFactory(name="Alpha Edict")

    edicts = list(edict_z.__class__.objects.filter(name__in=["Zulu Edict", "Alpha Edict"]))

    assert edicts[0] == edict_a
    assert edicts[1] == edict_z


@pytest.mark.django_db
def test_edict_log_str_includes_edict_name_and_year():
    edict_log = EdictLogFactory(
        edict__name="Test Edict",
        activated_at_year=1250,
    )

    result = str(edict_log)

    assert "Test Edict" in result
    assert "1250" in result


@pytest.mark.django_db
def test_edict_log_ordering_by_activated_year_descending():
    log_1200 = EdictLogFactory(activated_at_year=1200)
    log_1250 = EdictLogFactory(activated_at_year=1250)

    logs = list(log_1200.__class__.objects.all())

    assert logs[0] == log_1250
    assert logs[1] == log_1200
