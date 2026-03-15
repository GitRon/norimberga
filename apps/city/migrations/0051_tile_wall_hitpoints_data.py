from django.db import migrations


def initialize_wall_hitpoints(apps, schema_editor):
    Tile = apps.get_model("city", "Tile")
    wall_tiles = Tile.objects.filter(
        building__building_type__is_wall=True
    ).select_related("building", "building__building_type")

    for tile in wall_tiles:
        tile.wall_hitpoints = tile.building.level * 100

    Tile.objects.bulk_update(wall_tiles, ["wall_hitpoints"])


class Migration(migrations.Migration):

    dependencies = [
        ("city", "0050_tile_wall_hitpoints"),
    ]

    operations = [
        migrations.RunPython(initialize_wall_hitpoints, migrations.RunPython.noop),
    ]
