# Custom data migration to copy Savegame data from city app to savegame app
from django.db import migrations


def copy_savegame_data(apps, schema_editor):
    """Copy all Savegame instances from city app to savegame app."""
    # Get the old city Savegame model
    CitySavegame = apps.get_model("city", "Savegame")
    # Get the new savegame Savegame model
    NewSavegame = apps.get_model("savegame", "Savegame")

    # Copy all savegame instances
    for old_savegame in CitySavegame.objects.all():
        NewSavegame.objects.create(
            id=old_savegame.id,
            user=old_savegame.user,
            city_name=old_savegame.city_name,
            coins=old_savegame.coins,
            population=old_savegame.population,
            unrest=old_savegame.unrest,
            current_year=old_savegame.current_year,
            is_active=old_savegame.is_active,
            is_enclosed=old_savegame.is_enclosed,
        )


def reverse_copy_savegame_data(apps, schema_editor):
    """Reverse operation: delete all Savegame instances from savegame app."""
    NewSavegame = apps.get_model("savegame", "Savegame")
    NewSavegame.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("savegame", "0001_initial"),
        ("city", "0042_remove_savegame_map_size"),  # Ensure city model still exists
    ]

    operations = [
        migrations.RunPython(copy_savegame_data, reverse_copy_savegame_data),
    ]
