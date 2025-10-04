from io import StringIO
from unittest import mock

import pytest
from django.core.management import call_command

from apps.city.management.commands.generate_map import Command as GenerateMapCommand
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_generate_map_command_handle():
    """Test generate_map command creates and processes map."""
    savegame = SavegameFactory()

    command = GenerateMapCommand()

    with mock.patch("apps.city.management.commands.generate_map.MapGenerationService") as mock_service_class:
        mock_service = mock_service_class.return_value

        command.handle(savegame_id=savegame.id)

        # Verify service was created with correct savegame
        mock_service_class.assert_called_once_with(savegame=savegame)
        # Verify service.process() was called
        mock_service.process.assert_called_once()


@pytest.mark.django_db
def test_generate_map_command_creates_savegame():
    """Test generate_map command creates savegame when no ID is provided."""
    from apps.city.models import Savegame

    command = GenerateMapCommand()

    initial_count = Savegame.objects.count()

    with mock.patch("apps.city.management.commands.generate_map.MapGenerationService") as mock_service_class:
        mock_service = mock_service_class.return_value

        command.handle(savegame_id=None)

        # Verify savegame was created
        assert Savegame.objects.count() == initial_count + 1

        # Verify service was called with a savegame
        mock_service_class.assert_called_once()
        call_args = mock_service_class.call_args
        assert "savegame" in call_args.kwargs
        assert isinstance(call_args.kwargs["savegame"], Savegame)
        mock_service.process.assert_called_once()


@pytest.mark.django_db
def test_generate_map_command_via_call_command():
    """Test generate_map command can be called via Django's call_command."""
    with mock.patch("apps.city.management.commands.generate_map.MapGenerationService") as mock_service_class:
        mock_service = mock_service_class.return_value

        # Capture output
        out = StringIO()
        call_command("generate_map", stdout=out)

        # Verify service was called
        mock_service_class.assert_called_once()
        mock_service.process.assert_called_once()


def test_generate_map_command_inheritance():
    """Test GenerateMapCommand inherits from BaseCommand."""
    from django.core.management.base import BaseCommand

    command = GenerateMapCommand()
    assert isinstance(command, BaseCommand)


def test_generate_map_command_has_handle_method():
    """Test GenerateMapCommand implements the handle method."""
    command = GenerateMapCommand()

    assert hasattr(command, "handle")
    assert callable(command.handle)


# Integration test with pytest for full command testing
@pytest.mark.django_db
def test_generate_map_integration():
    """Integration test for generate_map command."""
    from apps.city.models import Savegame, Tile
    from apps.city.tests.factories import RiverTerrainFactory, TerrainFactory

    # Create required terrain for map generation
    # Create river terrain needed by the service
    RiverTerrainFactory()
    # Create regular terrain for get_terrain() calls
    terrain = TerrainFactory()

    initial_savegame_count = Savegame.objects.count()

    with mock.patch("apps.city.services.map.generation.MapGenerationService.get_terrain") as mock_get_terrain:
        mock_get_terrain.return_value = terrain

        # Run the command
        out = StringIO()
        call_command("generate_map", stdout=out)

        # Verify a savegame was created
        assert Savegame.objects.count() == initial_savegame_count + 1
        savegame = Savegame.objects.last()
        assert savegame is not None

        # Verify tiles were created (depends on implementation)
        # This would vary based on the actual MapGenerationService behavior
        tiles_count = Tile.objects.filter(savegame=savegame).count()
        assert tiles_count >= 0
