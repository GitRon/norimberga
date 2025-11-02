import pytest

from apps.city.events.events.wandering_preacher import Event as WanderingPreacherEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_wandering_preacher_has_choices():
    """Test that the Wandering Preacher event has choices."""
    # Arrange
    savegame = SavegameFactory()
    event = WanderingPreacherEvent(savegame=savegame)

    # Act
    has_choices = event.has_choices()

    # Assert
    assert has_choices is True


@pytest.mark.django_db
def test_wandering_preacher_returns_two_choices():
    """Test that the Wandering Preacher event returns two choices."""
    # Arrange
    savegame = SavegameFactory()
    event = WanderingPreacherEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert len(choices) == 2


@pytest.mark.django_db
def test_wandering_preacher_choice_labels():
    """Test the labels of the Wandering Preacher choices."""
    # Arrange
    savegame = SavegameFactory()
    event = WanderingPreacherEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert choices[0].label == "Grant him permission to speak"
    assert choices[1].label == "Silence him quietly"


@pytest.mark.django_db
def test_wandering_preacher_choice_effects():
    """Test that choices have effects defined."""
    # Arrange
    savegame = SavegameFactory()
    event = WanderingPreacherEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert len(choices[0].effects) == 2  # Decrease and increase unrest
    assert len(choices[1].effects) == 1  # Just increase unrest


@pytest.mark.django_db
def test_wandering_preacher_grant_permission_choice():
    """Test applying the 'grant permission' choice."""
    # Arrange
    savegame = SavegameFactory(unrest=50)
    event = WanderingPreacherEvent(savegame=savegame)
    choices = event.get_choices()

    # Act
    choices[0].apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    # Net effect should be negative (decrease more than increase) or at least change unrest
    assert savegame.unrest != 50


@pytest.mark.django_db
def test_wandering_preacher_silence_choice():
    """Test applying the 'silence him quietly' choice."""
    # Arrange
    savegame = SavegameFactory(unrest=50)
    initial_unrest = savegame.unrest
    event = WanderingPreacherEvent(savegame=savegame)
    choices = event.get_choices()

    # Act
    choices[1].apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.unrest > initial_unrest  # Should increase unrest


@pytest.mark.django_db
def test_wandering_preacher_verbose_text():
    """Test the event description text."""
    # Arrange
    savegame = SavegameFactory()
    event = WanderingPreacherEvent(savegame=savegame)

    # Act
    text = event.get_verbose_text()

    # Assert
    assert "preacher" in text.lower()
    assert "city gates" in text.lower()


@pytest.mark.django_db
def test_wandering_preacher_probability():
    """Test that the event has the correct probability."""
    # Arrange
    savegame = SavegameFactory()
    event = WanderingPreacherEvent(savegame=savegame)

    # Act
    probability = event.get_probability()

    # Assert
    assert probability == 3
