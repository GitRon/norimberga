# Generated by Django 5.0 on 2023-12-13 17:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("city", "0004_tile_tile_type"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="building",
            options={"default_related_name": "buildings"},
        ),
        migrations.AlterModelOptions(
            name="savegame",
            options={"default_related_name": "savegames"},
        ),
        migrations.AlterModelOptions(
            name="tile",
            options={"default_related_name": "tiles"},
        ),
        migrations.AlterModelOptions(
            name="tiletype",
            options={"default_related_name": "tile_types"},
        ),
        migrations.AddField(
            model_name="tiletype",
            name="probability",
            field=models.PositiveSmallIntegerField(
                default=50,
                validators=[
                    django.core.validators.MaxValueValidator(100),
                    django.core.validators.MinValueValidator(1),
                ],
            ),
            preserve_default=False,
        ),
    ]
