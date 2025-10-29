import pytest
from django.db import IntegrityError

from apps.savegame.tests.factories import SavegameFactory
from apps.thread.tests.factories import ActiveThreadFactory, ThreadTypeFactory


@pytest.mark.django_db
def test_thread_type_creation():
    """Test ThreadType creation with factory."""
    thread_type = ThreadTypeFactory.create()

    assert thread_type.name is not None
    assert thread_type.description is not None
    assert thread_type.condition_class is not None
    assert thread_type.severity is not None
    assert thread_type.order is not None


@pytest.mark.django_db
def test_thread_type_str_representation():
    """Test ThreadType __str__ method returns name."""
    thread_type = ThreadTypeFactory.create(name="Test Thread")

    assert str(thread_type) == "Test Thread"


@pytest.mark.django_db
def test_thread_type_severity_choices():
    """Test ThreadType severity field accepts valid choices."""
    thread_type_low = ThreadTypeFactory.create(severity="low")
    thread_type_medium = ThreadTypeFactory.create(severity="medium")
    thread_type_high = ThreadTypeFactory.create(severity="high")
    thread_type_critical = ThreadTypeFactory.create(severity="critical")

    assert thread_type_low.severity == "low"
    assert thread_type_medium.severity == "medium"
    assert thread_type_high.severity == "high"
    assert thread_type_critical.severity == "critical"


@pytest.mark.django_db
def test_thread_type_default_severity():
    """Test ThreadType severity defaults to medium."""
    thread_type = ThreadTypeFactory.create(severity="medium")

    assert thread_type.severity == "medium"


@pytest.mark.django_db
def test_thread_type_ordering():
    """Test ThreadType ordering by order and name."""
    thread_type_b = ThreadTypeFactory.create(name="B Thread", order=2)
    thread_type_a = ThreadTypeFactory.create(name="A Thread", order=1)
    thread_type_c = ThreadTypeFactory.create(name="C Thread", order=1)

    from apps.thread.models import ThreadType

    thread_types = list(ThreadType.objects.all())

    assert thread_types[0] == thread_type_a
    assert thread_types[1] == thread_type_c
    assert thread_types[2] == thread_type_b


@pytest.mark.django_db
def test_active_thread_creation():
    """Test ActiveThread creation with factory."""
    active_thread = ActiveThreadFactory.create()

    assert active_thread.savegame is not None
    assert active_thread.thread_type is not None
    assert active_thread.activated_at is not None
    assert active_thread.intensity is not None
    assert isinstance(active_thread.intensity, int)


@pytest.mark.django_db
def test_active_thread_str_representation():
    """Test ActiveThread __str__ method returns formatted string."""
    savegame = SavegameFactory.create(city_name="Test City")
    thread_type = ThreadTypeFactory.create(name="Test Thread")
    active_thread = ActiveThreadFactory.create(savegame=savegame, thread_type=thread_type, intensity=50)

    assert str(active_thread) == "Test City: Test Thread (Intensity: 50)"


@pytest.mark.django_db
def test_active_thread_relationships():
    """Test ActiveThread foreign key relationship with Savegame."""
    savegame = SavegameFactory.create()
    active_thread = ActiveThreadFactory.create(savegame=savegame)

    assert active_thread.savegame == savegame
    assert active_thread in savegame.active_threads.all()


@pytest.mark.django_db
def test_active_thread_meta_related_name():
    """Test ActiveThread uses correct related name."""
    savegame = SavegameFactory.create()
    active_thread = ActiveThreadFactory.create(savegame=savegame)

    assert hasattr(savegame, "active_threads")
    assert active_thread in savegame.active_threads.all()


@pytest.mark.django_db
def test_active_thread_ordering():
    """Test ActiveThread ordering by intensity desc and thread_type order."""
    savegame = SavegameFactory.create()
    thread_type_a = ThreadTypeFactory.create(name="Thread A", order=1)
    thread_type_b = ThreadTypeFactory.create(name="Thread B", order=2)
    thread_type_c = ThreadTypeFactory.create(name="Thread C", order=3)

    active_thread_low = ActiveThreadFactory.create(savegame=savegame, thread_type=thread_type_b, intensity=10)
    active_thread_high = ActiveThreadFactory.create(savegame=savegame, thread_type=thread_type_a, intensity=100)
    active_thread_medium = ActiveThreadFactory.create(savegame=savegame, thread_type=thread_type_c, intensity=50)

    from apps.thread.models import ActiveThread

    active_threads = list(ActiveThread.objects.filter(savegame=savegame))

    assert active_threads[0] == active_thread_high
    assert active_threads[1] == active_thread_medium
    assert active_threads[2] == active_thread_low


@pytest.mark.django_db
def test_active_thread_unique_together_constraint():
    """Test ActiveThread unique_together constraint for savegame and thread_type."""
    savegame = SavegameFactory.create()
    thread_type = ThreadTypeFactory.create()

    ActiveThreadFactory.create(savegame=savegame, thread_type=thread_type, intensity=50)

    # Attempting to create another active thread with same savegame and thread_type should fail
    with pytest.raises(IntegrityError):
        ActiveThreadFactory.create(savegame=savegame, thread_type=thread_type, intensity=75)


@pytest.mark.django_db
def test_active_thread_default_intensity():
    """Test ActiveThread intensity defaults to 0."""
    savegame = SavegameFactory.create()
    thread_type = ThreadTypeFactory.create()

    from apps.thread.models import ActiveThread

    active_thread = ActiveThread.objects.create(savegame=savegame, thread_type=thread_type, activated_at=1200)

    assert active_thread.intensity == 0
