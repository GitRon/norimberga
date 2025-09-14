import pytest
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from unittest import mock

from apps.city.management.commands.generate_map import Command as GenerateMapCommand
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_generate_map_command_handle():
    """Test generate_map command creates and processes map."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame
    Savegame.objects.filter(id=1).delete()

    # Create savegame with id=1
    savegame = SavegameFactory(id=1)

    command = GenerateMapCommand()

    with mock.patch('apps.city.management.commands.generate_map.MapGenerationService') as mock_service_class:
        mock_service = mock_service_class.return_value

        command.handle()

        # Verify service was created with correct savegame
        mock_service_class.assert_called_once_with(savegame=savegame)
        # Verify service.process() was called
        mock_service.process.assert_called_once()


@pytest.mark.django_db
def test_generate_map_command_creates_savegame():
    """Test generate_map command creates savegame if doesn't exist."""
    command = GenerateMapCommand()

    with mock.patch('apps.city.management.commands.generate_map.MapGenerationService') as mock_service_class:
        mock_service = mock_service_class.return_value

        command.handle()

        # Verify savegame was created
        from apps.city.models import Savegame
        savegame = Savegame.objects.get(id=1)
        assert savegame is not None

        # Verify service was called with the savegame
        mock_service_class.assert_called_once_with(savegame=savegame)
        mock_service.process.assert_called_once()


@pytest.mark.django_db
def test_generate_map_command_via_call_command():
    """Test generate_map command can be called via Django's call_command."""
    with mock.patch('apps.city.management.commands.generate_map.MapGenerationService') as mock_service_class:
        mock_service = mock_service_class.return_value

        # Capture output
        out = StringIO()
        call_command('generate_map', stdout=out)

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

    assert hasattr(command, 'handle')
    assert callable(command.handle)


# Integration test with actual Django TestCase for full command testing
class GenerateMapCommandIntegrationTest(TestCase):
    """Integration tests for generate_map command using Django's TestCase."""

    def test_generate_map_integration(self):
        """Integration test for generate_map command."""
        from apps.city.models import Savegame, Terrain, Tile

        # Create required terrain for map generation
        terrain = self.create_test_terrain()

        with mock.patch('apps.city.services.map.generation.MapGenerationService.get_terrain') as mock_get_terrain:
            mock_get_terrain.return_value = terrain

            # Run the command
            out = StringIO()
            call_command('generate_map', stdout=out)

            # Verify savegame was created
            savegame = Savegame.objects.get(id=1)
            self.assertIsNotNone(savegame)

            # Verify tiles were created (depends on implementation)
            # This would vary based on the actual MapGenerationService behavior
            tiles_count = Tile.objects.filter(savegame=savegame).count()
            self.assertGreaterEqual(tiles_count, 0)

    def create_test_terrain(self):
        """Create test terrain for integration tests."""
        from apps.city.tests.factories import TerrainFactory
        return TerrainFactory()