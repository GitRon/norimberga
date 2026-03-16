import pytest

from apps.savegame.models import SiegeChronicle
from apps.savegame.tests.factories import SavegameFactory, SiegeChronicleFactory


@pytest.mark.django_db
def test_siege_chronicle_creation():
    """Test basic creation of SiegeChronicle."""
    chronicle = SiegeChronicleFactory.create()
    assert chronicle.pk is not None


@pytest.mark.django_db
def test_siege_chronicle_str():
    """Test __str__ representation."""
    chronicle = SiegeChronicleFactory.create(year=1155)
    result = str(chronicle)
    assert "1155" in result


@pytest.mark.django_db
def test_siege_chronicle_result_choices():
    """Test result choices are valid."""
    results = [SiegeChronicle.Result.REPELLED, SiegeChronicle.Result.DAMAGED, SiegeChronicle.Result.BREACHED]
    values = [r.value for r in results]
    assert set(values) == {"repelled", "damaged", "breached"}


@pytest.mark.django_db
def test_siege_chronicle_ordering_by_year():
    """Test chronicles are ordered by year ascending."""
    savegame = SavegameFactory.create()
    SiegeChronicleFactory.create(savegame=savegame, year=1200)
    SiegeChronicleFactory.create(savegame=savegame, year=1155)
    SiegeChronicleFactory.create(savegame=savegame, year=1175)

    years = list(savegame.siege_chronicles.values_list("year", flat=True))
    assert years == [1155, 1175, 1200]


@pytest.mark.django_db
def test_siege_chronicle_cascade_delete():
    """Test SiegeChronicle is deleted when savegame is deleted."""
    savegame = SavegameFactory.create()
    SiegeChronicleFactory.create(savegame=savegame)
    assert SiegeChronicle.objects.filter(savegame=savegame).count() == 1

    savegame.delete()
    assert SiegeChronicle.objects.count() == 0


@pytest.mark.django_db
def test_siege_chronicle_default_related_name():
    """Test default_related_name is 'siege_chronicles'."""
    savegame = SavegameFactory.create()
    chronicle = SiegeChronicleFactory.create(savegame=savegame)
    assert savegame.siege_chronicles.filter(pk=chronicle.pk).exists()


@pytest.mark.django_db
def test_siege_chronicle_fields():
    """Test all fields are stored correctly."""
    savegame = SavegameFactory.create()
    chronicle = SiegeChronicleFactory.create(
        savegame=savegame,
        year=1165,
        direction="W",
        attacker_strength=180,
        defense_score=120,
        result=SiegeChronicle.Result.DAMAGED,
        report_text="The west wall was damaged.",
    )
    chronicle.refresh_from_db()
    assert chronicle.year == 1165
    assert chronicle.direction == "W"
    assert chronicle.attacker_strength == 180
    assert chronicle.defense_score == 120
    assert chronicle.result == "damaged"
    assert chronicle.report_text == "The west wall was damaged."
