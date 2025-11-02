import pytest

from apps.event.models.event_choice import EventChoice
from apps.event.tests.factories import EventChoiceFactory, MockEventWithChoices
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_event_choice_creation():
    """Test that EventChoice can be created successfully."""
    # Arrange & Act
    event_choice = EventChoiceFactory()

    # Assert
    assert event_choice.id is not None
    assert event_choice.savegame is not None
    assert event_choice.event_module == "apps.event.tests.factories"
    assert event_choice.event_class_name == "MockEventWithChoices"


@pytest.mark.django_db
def test_event_choice_get_event_instance():
    """Test that get_event_instance returns a proper event instance."""
    # Arrange
    savegame = SavegameFactory()
    event_choice = EventChoiceFactory(
        savegame=savegame,
        event_module="apps.event.tests.factories",
        event_class_name="MockEventWithChoices",
    )

    # Act
    event = event_choice.get_event_instance()

    # Assert
    assert isinstance(event, MockEventWithChoices)
    assert event.savegame == savegame


@pytest.mark.django_db
def test_event_choice_get_choices():
    """Test that get_choices returns the event's choices."""
    # Arrange
    event_choice = EventChoiceFactory()

    # Act
    choices = event_choice.get_choices()

    # Assert
    assert len(choices) == 2
    assert choices[0].label == "Good choice"
    assert choices[1].label == "Bad choice"


@pytest.mark.django_db
def test_event_choice_get_title():
    """Test that get_title returns the event title."""
    # Arrange
    event_choice = EventChoiceFactory()

    # Act
    title = event_choice.get_title()

    # Assert
    assert title == "Mock Event With Choices"


@pytest.mark.django_db
def test_event_choice_get_verbose_text():
    """Test that get_verbose_text returns the event description."""
    # Arrange
    event_choice = EventChoiceFactory()

    # Act
    verbose_text = event_choice.get_verbose_text()

    # Assert
    assert verbose_text == "Mock event with choices occurred"


@pytest.mark.django_db
def test_event_choice_get_level():
    """Test that get_level returns the event level."""
    # Arrange
    event_choice = EventChoiceFactory()

    # Act
    level = event_choice.get_level()

    # Assert
    from django.contrib import messages

    assert level == messages.INFO


@pytest.mark.django_db
def test_event_choice_ordering():
    """Test that EventChoice records are ordered by creation time."""
    # Arrange
    savegame = SavegameFactory()
    event_choice_1 = EventChoiceFactory(savegame=savegame)
    event_choice_2 = EventChoiceFactory(savegame=savegame)
    event_choice_3 = EventChoiceFactory(savegame=savegame)

    # Act
    choices = EventChoice.objects.filter(savegame=savegame)

    # Assert
    assert list(choices) == [event_choice_1, event_choice_2, event_choice_3]


@pytest.mark.django_db
def test_event_choice_str():
    """Test the string representation of EventChoice."""
    # Arrange
    savegame = SavegameFactory(city_name="Test City")
    event_choice = EventChoiceFactory(
        savegame=savegame,
        event_module="apps.city.events.events.fire",
    )

    # Act
    result = str(event_choice)

    # Assert
    assert "Test City" in result
    assert "apps.city.events.events.fire" in result
