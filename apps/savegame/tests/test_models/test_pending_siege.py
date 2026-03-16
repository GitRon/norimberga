import pytest

from apps.savegame.models import PendingSiege
from apps.savegame.tests.factories import PendingSiegeFactory, SavegameFactory


@pytest.mark.django_db
def test_pending_siege_creation():
    """Test basic creation of PendingSiege."""
    siege = PendingSiegeFactory.create()
    assert siege.pk is not None
    assert siege.resolved is False


@pytest.mark.django_db
def test_pending_siege_str():
    """Test __str__ representation."""
    siege = PendingSiegeFactory.create(attack_year=1155, direction="N")
    result = str(siege)
    assert "1155" in result
    assert "N" in result


@pytest.mark.django_db
def test_pending_siege_default_resolved_false():
    """Test resolved defaults to False."""
    siege = PendingSiegeFactory.create()
    assert siege.resolved is False


@pytest.mark.django_db
def test_pending_siege_direction_choices():
    """Test direction choices are valid."""
    directions = [
        PendingSiege.Direction.NORTH,
        PendingSiege.Direction.SOUTH,
        PendingSiege.Direction.EAST,
        PendingSiege.Direction.WEST,
    ]
    values = [d.value for d in directions]
    assert set(values) == {"N", "S", "E", "W"}


@pytest.mark.django_db
def test_pending_siege_cascade_delete():
    """Test PendingSiege is deleted when savegame is deleted."""
    savegame = SavegameFactory.create()
    PendingSiegeFactory.create(savegame=savegame)
    assert PendingSiege.objects.filter(savegame=savegame).count() == 1

    savegame.delete()
    assert PendingSiege.objects.count() == 0


@pytest.mark.django_db
def test_pending_siege_default_related_name():
    """Test default_related_name is 'pending_sieges'."""
    savegame = SavegameFactory.create()
    siege = PendingSiegeFactory.create(savegame=savegame)
    assert savegame.pending_sieges.filter(pk=siege.pk).exists()


@pytest.mark.django_db
def test_pending_siege_fields():
    """Test all fields are stored correctly."""
    savegame = SavegameFactory.create()
    siege = PendingSiegeFactory.create(
        savegame=savegame,
        attack_year=1160,
        actual_strength=200,
        announced_strength=150,
        direction="E",
        resolved=False,
    )
    siege.refresh_from_db()
    assert siege.attack_year == 1160
    assert siege.actual_strength == 200
    assert siege.announced_strength == 150
    assert siege.direction == "E"
    assert siege.resolved is False
